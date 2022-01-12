from asyncio.tasks import wait
import logging
import asyncio
import json
import constants
from threading import Thread
from kademlia.network import Server
from node import KNode
import pytz
from datetime import datetime
from tzlocal import get_localzone
import time


DEBUG = False

class KServer:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.node = None

    def start(self, bootstrap_nodes=None):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        if DEBUG:
            log = logging.getLogger('kademlia')
            log.setLevel(logging.DEBUG)
            log.addHandler(handler)
        
        self.loop = asyncio.get_event_loop()
        
        self.server = Server()
        self.loop.run_until_complete(self.server.listen(self.port))
        
        if bootstrap_nodes != None:
            self.loop.run_until_complete(self.server.bootstrap(bootstrap_nodes))
            

        return self.loop

    def close_server(self):
        self.server.stop()


    async def register(self, username=None):

        user = await self.server.get(username)

        if user is None:
            value = {"followers": [],
                    "following": [],
                    "address": self.address,
                    "port": self.port,
                    "messages":[],
                    "username": username,
                    "online": True,
                    "timeline": [],
                    "followers_with_timeline":[]
                }

            value_json = json.dumps(value)
            await self.server.set(username, value_json)

            self.node = KNode(value)
            Thread(target=self.listen, daemon=True).start()
            return self.node
        
        else:
            raise Exception("Username already exists!")

    async def login(self, username):
        
        user = await self.server.get(username)

        user = json.loads(user)

        if user != None:
            value = {"followers": user["followers"], 
                    "following": user["following"], 
                    "address": self.address, 
                    "port": self.port, 
                    "messages":[],
                    "username": username,
                    "online": True,
                    "timeline": user["timeline"],
                    "followers_with_timeline": user["followers_with_timeline"]
                }
            value_json = json.dumps(value)
            await self.server.set(username, value_json)

            self.node = KNode(value)
            Thread(target=self.listen, daemon=True).start()
            return self.node

        else:
            raise Exception("User does not exist!")

    async def logout(self):
        self.node.online = False
        await self.update_user(self.node)
        self.close_listener()
        self.close_server()


    async def get_user_by_username(self, username):
        user = await self.server.get(username)
        
        
        if user == None:
            print("\nUser does not exit!\n")
            return None

        user = json.loads(user)
        
        value = {"followers": user["followers"], 
                "following": user["following"], 
                "address": user["address"], 
                "port": user["port"], 
                "messages": user["messages"],
                "username": username,
                "online": user["online"],
                "timeline": user["timeline"],
                "followers_with_timeline": user["followers_with_timeline"]
            }

        node = KNode(value)

        return node

    async def create_listener(self):
        self.listen_server = await asyncio.start_server(self.establish_connection, self.address, self.port)
        await self.listen_server.serve_forever()
    
    def close_listener(self):
        self.listen_server.close()


    def listen(self):
        print(f"Listening on address {self.address}:{self.port}")
        self.listen_loop = asyncio.new_event_loop()
        self.listen_loop.run_until_complete(self.create_listener())


    async def follow_user(self, username):
        user = await self.get_user_by_username(username)

        if user == None:
            return

        if user.username in self.node.following:
            print(f"\nYou already follow {user.username}!\n")
            return

        self.node.following.append(username)
        await self.update_user(self.node)
        user.followers.append(self.node.username)
        await self.update_user(user)
        if user.online == False:
            return 
        try:
            reader, writer = await asyncio.open_connection(user.address, user.port)
        except Exception as e:
            user.online = False
            await self.update_user(user)
            print(f"\nCould not connect to {username}!\n")
            return

        data = {"req_type": constants.FOLLOW_REQUEST ,"following_username": self.node.username}
        json_data = json.dumps(data) + '\n'
        writer.write(json_data.encode())
        
        await writer.drain()

        writer.close()       
        await writer.wait_closed()


    async def unfollow_user(self, username):      
        user = await self.get_user_by_username(username)

        if user == None:
            return

        if user.username not in self.node.following:
            print(f"\nSince you do not follow {user.username}, you cannot unfollow him!\n")
            return

        self.node.following.remove(user.username)
        await self.update_user(self.node)    
        user.followers.remove(self.node.username)
        await self.update_user(user)  
        if user.online == False:
            return 
        try:
            reader, writer = await asyncio.open_connection(user.address, user.port)
        except Exception as e:
            user.online = False
            await self.update_user(user)
            print(f"\nCould not connect to {username}!\n")
            return
        data = {"req_type": constants.UNFOLLOW_REQUEST ,"unfollowing_username": self.node.username}
        json_data = json.dumps(data) + '\n'
        writer.write(json_data.encode())
        
        await writer.drain()

        writer.close()       
        await writer.wait_closed()

        

    
    async def establish_connection(self, reader, writer):
        data = await reader.readline()


        json_str = data.decode()
        request = json.loads(json_str)
        
        if request["req_type"] == constants.FOLLOW_REQUEST:
            messages = self.node.messages
            self.node = await self.get_user_by_username(self.node.username)
            self.node.messages = messages
            #await self.update_follower(request)

            writer.close()
            await writer.wait_closed()

        if request["req_type"] == constants.UNFOLLOW_REQUEST:
            #await self.update_unfollower(request)
            messages = self.node.messages
            self.node = await self.get_user_by_username(self.node.username)
            self.node.messages = messages
            writer.close()
            await writer.wait_closed()

        elif request["req_type"] == constants.GET:
            redirects = None
            follower_username = request["follower_username"]
            username = request["username"]
            if username == self.node.username:
                if follower_username in self.node.followers_with_timeline:
                    self.node.followers_with_timeline.remove(follower_username)
                self.node.followers_with_timeline.insert(0,follower_username)
                await self.update_user(self.node)

            if "redirects" in request:
                redirects = request["redirects"]
            await self.post_message(writer, follower_username, username, redirects)
        
        elif request["req_type"] == constants.GET_STORED_TIMELINE:
            username = request["username"]
            redirects = request["redirects"]
            await self.post_stored_messages(writer, username, redirects)

        elif request["req_type"] == constants.DELETED_TIMELINE:
            username = request["username"]
            self.node.followers_with_timeline.remove(username)
            await self.update_user(self.node)
            writer.close()
            await writer.wait_closed()
    


    async def update_user(self, node):
        value_json = json.dumps(node.dump())
        await self.server.set(node.username, value_json)


    async def update_follower(self, request_data):
        following_username = request_data["following_username"]
        self.node.followers.append(following_username)
        await self.update_user(self.node)

    async def update_unfollower(self, request_data):
        following_username = request_data["unfollowing_username"]
        self.node.followers.remove(following_username)
        await self.update_user(self.node)


    async def send_message_to_node(self, user, message):

        try:
            if user.online == False:
                return 
            try:
                reader, writer = await asyncio.open_connection(user.address, user.port)
            except Exception as e:
                user.online = False
                await self.update_user(user)
                print(f"\nCould not connect to {user.username}!\n")
                return

            writer.write(message)

            await writer.drain()      
            
            data = await reader.readline()

            writer.close()       
            await writer.wait_closed()
        
            json_str = data.decode()

            request = json.loads(json_str)
            
            
            if request["req_type"] == constants.POST:
                #print("Mensagem recebida: ", request["message"])
                return request["message"]


        except Exception as e:
            print(e)
            return None

        

    async def save_message(self, message):
        self.node.messages.append((message,str(datetime.now()).split('.')[0],str(get_localzone())))


    async def post_stored_messages(self, writer, username, redirects=None):

        # msglist = list(filter(lambda x: x[0][0] == username, self.node.timeline))
        messages= []

        # for message in msglist:
        #     messages.append(message[0])

        #print(username)
        for tup in self.node.timeline:
            for msglist in tup[0]:
                if msglist[0] == username:
                #for msg in msglist:
                    #if msg[0] == username:
                    messages.append(msglist)


        if redirects != []:
            offline = True
            nodes_connected = []
            nodes = [await self.get_user_by_username(x) for x in redirects]
            online_nodes = list(filter(lambda x: x.online == True, nodes))

            if online_nodes == []:
                data = {"req_type": constants.POST, "message": messages}

                json_data = json.dumps(data) + '\n'
              
                writer.write(json_data.encode())

                await writer.drain()

                writer.close()
                await writer.wait_closed()
                 
                return

            users_offline = list(filter(lambda x: x.online == False, nodes))
            redirect_users = [x for x in online_nodes[:constants.MAX_CONNECTIONS]]
            
            rest_redirects = [x.username for x in online_nodes[constants.MAX_CONNECTIONS:]]
            
            for user in redirect_users:
                for k in list(rest_redirects):
                    if k in nodes_connected:
                        rest_redirects.remove(k)

                data = {"req_type": constants.GET_STORED_TIMELINE, "redirects": rest_redirects, "username": username}
                json_data = json.dumps(data) + '\n'
                
                redirect_messages = await self.send_message_to_node(user, json_data.encode())
                if redirect_messages != None:
                    messages += redirect_messages
                    nodes_connected += [x for (x, y) in redirect_messages]
                    offline = False
                else:
                    users_offline.append(user)
            
            if offline == True:
                await self.post_stored_messages(writer, username, redirects)
                return


        #print(messages)
        data = {"req_type": constants.POST, "message": messages}


        json_data = json.dumps(data) + '\n'

        
        writer.write(json_data.encode())

        await writer.drain()

        writer.close()
        await writer.wait_closed()

    async def post_message(self, writer, follower_username, username, redirects = None):
        #print(redirects)
        messages = [(self.node.username, msg) for msg in self.node.messages]

        if redirects != []:
            offline = True
            nodes_connected = []
            #users_offline = []
            nodes = [await self.get_user_by_username(x) for x in redirects]
            online_nodes = list(filter(lambda x: x.online == True, nodes))

            if online_nodes == []:
                data = {"req_type": constants.POST, "message": messages}

                json_data = json.dumps(data) + '\n'
              
                writer.write(json_data.encode())

                await writer.drain()

                writer.close()
                await writer.wait_closed()
                 
                return

            users_offline = list(filter(lambda x: x.online == False, nodes))
            redirect_users = [x for x in online_nodes[:constants.MAX_CONNECTIONS]]
            rest_redirects = [x.username for x in online_nodes[constants.MAX_CONNECTIONS:]]
            
            for user in redirect_users:
                for k in list(rest_redirects):
                    if k in nodes_connected:
                        rest_redirects.remove(k)

                data = {"req_type": constants.GET, "redirects": rest_redirects, "follower_username": follower_username, "username": username}
                json_data = json.dumps(data) + '\n'
                redirect_messages = await self.send_message_to_node(user, json_data.encode())
                if redirect_messages != None:
                    messages += redirect_messages
                    nodes_connected += [x for (x, y) in redirect_messages]
                    offline = False
                else:
                    users_offline.append(user)
            
            if offline == True:
                await self.post_message(writer, follower_username, username, redirects)
                return

            if users_offline != []:
                messages += await self.send_message_to_offline_nodes(users_offline)
            # replace_nodes = await self.get_followers_online_with_timeline(users_offline)
            # hierarchy_replace_nodes = replace_nodes[constants.MAX_CONNECTIONS:]
            # replace_nodes_connected = []

            # for replace_node in replace_nodes[:constants.MAX_CONNECTIONS]:
            #     redirects = [x.username for x in hierarchy_replace_nodes]

            #     data = {"req_type": constants.GET_STORED_TIMELINE, "redirects": redirects, "username": users_offline[replace_nodes.index(replace_node)].username}
            #     json_data = json.dumps(data) + '\n'
            #     for node in replace_node:
            #         returned_messages = await self.send_message_to_node(node, json_data.encode())
            #         if returned_messages != None:
            #             messages += returned_messages
            #             replace_nodes_connected += [x for (x, y) in returned_messages]
            #             break

            #     for k in list(hierarchy_replace_nodes):
            #         if k.username in replace_nodes_connected:
            #             hierarchy_replace_nodes.remove(k)
            

        #print(messages)
        data = {"req_type": constants.POST, "message": messages}


        json_data = json.dumps(data) + '\n'

        
        writer.write(json_data.encode())

        await writer.drain()

        writer.close()
        await writer.wait_closed()

    async def get_followers_online_with_timeline(self, following_nodes):
        result = []
        for node in following_nodes:
            result.append([])
            for follower_username_with_timeline in node.followers_with_timeline:
                follower_node = await self.get_user_by_username(follower_username_with_timeline)
                if follower_node.online == True:
                    result[following_nodes.index(node)].append(follower_node)
                    break

        return result


    async def get_timeline(self):   
         
        following_nodes = []
        offline = True
        for user in self.node.following:
            following_nodes.append(await self.get_user_by_username(user))
            
        following_nodes.sort(key = lambda x: len(x.following))
        following_nodes_offline = list(filter(lambda x: x.online == False, following_nodes))

        following_nodes = list(filter(lambda x: x.online == True, following_nodes))

        if following_nodes == []:
            return []
        #replace_nodes = await self.get_followers_online_with_timeline(following_nodes_offline)

        #offline_nodes = []

        timeline = []

        hierarchy_nodes = following_nodes[constants.MAX_CONNECTIONS:]
        

        nodes_connected = []
        for following_node in following_nodes[:constants.MAX_CONNECTIONS]:
            redirects = [x.username for x in hierarchy_nodes]

            data = {"req_type": constants.GET, "redirects": redirects, "follower_username": self.node.username, "username": following_node.username}
            json_data = json.dumps(data) + '\n'
            returned_messages = await self.send_message_to_node(following_node, json_data.encode())
            if returned_messages != None:
                timeline += returned_messages
                nodes_connected += [x for (x, y) in returned_messages]
                offline = False
            else:
                following_nodes_offline.append(following_node)

            for k in list(hierarchy_nodes):
                if k.username in nodes_connected:
                    hierarchy_nodes.remove(k)

        if offline == True:
            return await self.get_timeline()

        if following_nodes_offline != []:
            timeline += await self.send_message_to_offline_nodes(following_nodes_offline)
        # replace_nodes = await self.get_followers_online_with_timeline(following_nodes_offline)
        # hierarchy_replace_nodes = replace_nodes[constants.MAX_CONNECTIONS:]
        # replace_nodes_connected = []

        # for replace_node in replace_nodes[:constants.MAX_CONNECTIONS]:
        #     redirects = [x.username for x in hierarchy_replace_nodes]

        #     data = {"req_type": constants.GET_STORED_TIMELINE, "redirects": redirects, "username": following_nodes_offline[replace_nodes.index(replace_node)].username}
        #     json_data = json.dumps(data) + '\n'
        #     for node in replace_node:
        #         returned_messages = await self.send_message_to_node(node, json_data.encode())
        #         if returned_messages != None:
        #             timeline += returned_messages
        #             replace_nodes_connected += [x for (x, y) in returned_messages]
        #             break

        #     for k in list(hierarchy_replace_nodes):
        #         if k.username in replace_nodes_connected:
        #             hierarchy_replace_nodes.remove(k)

        self.node.timeline.append((timeline, str(datetime.now()).split('.')[0]))
        
        await self.update_user(self.node)
    
        return timeline

    async def send_message_to_offline_nodes(self, following_nodes_offline):
        timeline = []

        replace_nodes = await self.get_followers_online_with_timeline(following_nodes_offline)
        hierarchy_replace_nodes = replace_nodes[constants.MAX_CONNECTIONS:]
        #print(replace_nodes)
        #print(hierarchy_replace_nodes)
        offline = True
        replace_nodes_connected = []
        if replace_nodes == []:
            return []

        for x in replace_nodes:
            if x != []:
                break
            elif x == [] and replace_nodes.index(x) == (len(replace_nodes) - 1):
                return []

        for replace_node in replace_nodes[:constants.MAX_CONNECTIONS]:
            redirects = [x[0].username for x in hierarchy_replace_nodes]

            data = {"req_type": constants.GET_STORED_TIMELINE, "redirects": redirects, "username": following_nodes_offline[replace_nodes.index(replace_node)].username}
            json_data = json.dumps(data) + '\n'
            #for node in replace_node:
            returned_messages = await self.send_message_to_node(replace_node[0], json_data.encode())
            #print(replace_node[0].username)
            #print(returned_messages)
            #print(returned_messages)
            if returned_messages != None:
                timeline += returned_messages
                replace_nodes_connected += [x for (x, y) in returned_messages]
                offline = False
                break


            for k in list(hierarchy_replace_nodes):
                if k.username in replace_nodes_connected:
                    hierarchy_replace_nodes.remove(k)
        
        if offline == True:
            return await self.send_message_to_offline_nodes(following_nodes_offline)
        
        return timeline

    
    async def garbage_collect(self):
        while True:
            time.sleep(5)
            now = datetime.now()
            users_deleted = []
            if self.node and len(self.node.timeline) > 0:
                #print(self.node.timeline)

                i = 0
                arraySize = len(self.node.timeline)
                while i < arraySize:
                    date = datetime.strptime(self.node.timeline[i][1],'%Y-%m-%d %H:%M:%S')
                    difference = now - date
                    if difference.total_seconds() > constants.MESSAGE_LIFETIME:
                        users_deleted.append(self.node.timeline[i][0][0][0])
                        del self.node.timeline[i]
                        arraySize -= 1
                    else:
                        i += 1
                
                nodes = [await self.get_user_by_username(x) for x in users_deleted]
                
                for node in nodes:
                    data = {"req_type": constants.DELETED_TIMELINE, "username": self.node.username}
                    try:
                        reader, writer = await asyncio.open_connection(node.address, node.port)
                    except Exception as e:
                        node.online = False
                        node.followers_with_timeline.remove(self.node.username)
                        await self.update_user(node)
                        print(f"\nCould not connect to {node.username}!\n")
                    
                    json_data = json.dumps(data) + '\n'
                    writer.write(json_data.encode())
        
                    await writer.drain()

                    writer.close()       
                    await writer.wait_closed()
                # print(users_deleted)

                    
                    # dar update no server e informar os nós que são apagados (dentro do if onde se dá delete)


    def show_timeline(self, messages):
        print('\n')

        timeline = []
        
        localtz = pytz.timezone(str(get_localzone()))

        # convert times tuples and join all messages
        #print('a')
        for username, message in messages:
            #print('c')
            (text, time, pubtz) = message
            time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            pub_time = pytz.timezone(pubtz)
            pub = pub_time.localize(time)
            localtime = pub.astimezone(localtz).strftime("%Y-%m-%d %H:%M:%S")
            timeline.append((username,text,localtime))

        #sort list
        timeline.sort(key=lambda tup: tup[2])  

        for message in timeline:
            print( message[0] + " posted: \t" + message[1] + "\t" + str(message[2]) + "\n\n")

        
        


