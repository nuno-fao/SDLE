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

        return self.server, self.loop

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
                    "username": username
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
                    "username": username
                }
            value_json = json.dumps(value)
            await self.server.set(username, value_json)

            self.node = KNode(value)
            Thread(target=self.listen, daemon=True).start()
            return self.node

        else:
            raise Exception("User does not exist!")


    async def get_user_by_username(self, username):
        user = await self.server.get(username)

        user = json.loads(user)

        if user != None:
            value = {"followers": user["followers"], 
                    "following": user["following"], 
                    "address": user["address"], 
                    "port": user["port"], 
                    "messages": user["messages"],
                    "username": username
                }
            node = KNode(value)

            return node

    async def create_listener(self):
        self.listen_server = await asyncio.start_server(self.establish_connection, self.address, self.port)
        await self.listen_server.serve_forever()
    
    async def close_listener(self):
        self.listen_server.close()



    def listen(self):
        print(f"Listening on address {self.address}:{self.port}")
        listen_loop = asyncio.new_event_loop()
        listen_loop.run_until_complete(self.create_listener())


    async def follow_user(self, username):
        user = await self.get_user_by_username(username)
        self.node.following.append(username)
        await self.update_user(self.node)
        reader, writer = await asyncio.open_connection(user.address, user.port)
        data = {"req_type": constants.FOLLOW_REQUEST ,"following_username": self.node.username}
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
            await self.update_follower(request)

            writer.close()
            await writer.wait_closed()

        elif request["req_type"] == constants.GET:
            redirects = None
            if "redirects" in request:
                redirects = request["redirects"]
            await self.post_message(writer, redirects)
        


    async def update_user(self, node):
        value_json = json.dumps(node.dump())
        await self.server.set(node.username, value_json)


    async def update_follower(self, request_data):
        following_username = request_data["following_username"]
        self.node.followers.append(following_username)
        await self.update_user(self.node)


    async def send_message_to_node(self, user, message):

        try:

            reader, writer = await asyncio.open_connection(user.address, user.port)

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


    async def post_message(self, writer, redirects = None):
        # messages = self.node.messages
        messages = [(self.node.username, msg) for msg in self.node.messages]

        if redirects != None:
            nodes_connected = []
            redirect_users = [await self.get_user_by_username(x) for x in redirects[:constants.MAX_CONNECTIONS]]
            # following_nodes = self.node.following
            #followings_nodes.sort(key = lambda x: len(x.following))
            
            rest_redirects = redirects[constants.MAX_CONNECTIONS:]
            
            for user in redirect_users:
                for k in list(rest_redirects):
                    if k in nodes_connected:
                        rest_redirects.remove(k)

                data = {"req_type": constants.GET, "redirects": rest_redirects}
                json_data = json.dumps(data) + '\n'
                
                redirect_messages = await self.send_message_to_node(user, json_data.encode())
                messages += redirect_messages
                nodes_connected += [x for (x, y) in redirect_messages]


        data = {"req_type": constants.POST, "message": messages}


        json_data = json.dumps(data) + '\n'

        
        writer.write(json_data.encode())

        await writer.drain()

        writer.close()
        await writer.wait_closed()


    async def get_timeline(self):   
         
        followings_nodes = []
        for user in self.node.following:
            followings_nodes.append(await self.get_user_by_username(user))
            
        followings_nodes.sort(key = lambda x: len(x.following))
        timeline = []

        hierarchy_nodes = followings_nodes[constants.MAX_CONNECTIONS:]
        

        nodes_connected = []
        for following_node in followings_nodes[:constants.MAX_CONNECTIONS]:
            redirects = [x.username for x in hierarchy_nodes]
            # num_redirects = len(hierarchy_nodes) // constants.MAX_CONNECTIONS
            # hierarchy_nodes = hierarchy_nodes[constants.MAX_CONNECTIONS:]

            data = {"req_type": constants.GET, "redirects": redirects}
            json_data = json.dumps(data) + '\n'
            returned_messages = await self.send_message_to_node(following_node, json_data.encode())
            timeline += returned_messages
            #print("Returned messages: ", returned_messages)
            nodes_connected += [x for (x, y) in returned_messages]

            # print("Nodes connected: ", nodes_connected)
            # print("Returned messages: ", returned_messages)
            for k in list(hierarchy_nodes):
                if k.username in nodes_connected:
                    # print(f"Removing {k.username} from hierarchy_nodes")
                    hierarchy_nodes.remove(k)

            # print("hierarchy_nodes: ", hierarchy_nodes)
    
        return timeline

    def show_timeline(self, messages):
        print('\n')

        timeline = []
        
        localtz = pytz.timezone(str(get_localzone()))

        # convert times tuples and join all messages
        for username, message in messages:
            (text, time, pubtz) = message
            time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            pub_time = pytz.timezone(pubtz)
            pub = pub_time.localize(time)
            localtime = pub.astimezone(localtz).strftime("%Y-%m-%d %H:%M:%S")
            timeline.append((username,text,localtime))

        #sort list
        timeline.sort(key=lambda tup: tup[2])  

        for message in timeline:
            print( message[0] + " posted: \t\t" + str(message[2]) + "\n" + message[1] + "\n\n")

        
        


