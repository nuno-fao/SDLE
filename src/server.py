import logging
import asyncio
import json
import constants
from threading import Thread
from kademlia.network import Server
from node import KNode
from datetime import datetime


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
        # print("USER: ", user)

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
        user.followers.append(self.node.username)
        self.node.following.append(username)
        await self.update_user(self.node)

        reader, writer = await asyncio.open_connection(user.address, user.port)
        data = {"req_type": constants.FOLLOW_REQUEST ,"following_username": self.node.username}
        json_data = json.dumps(data)
        writer.write(json_data.encode())

        await writer.drain()
        writer.close()

    
    async def establish_connection(self, reader, writer):
        while True:
            data = await reader.readline()

            if not data: break

            json_str = data.decode()
            request = json.loads(json_str)
            
            if request["req_type"] == constants.FOLLOW_REQUEST:
                await self.update_follower(request)

            elif request["req_type"] == constants.GET:
                print("Recebi o GET")
                await self.post_message()

            elif request["req_type"] == constants.POST:
                await self.show_timeline(request)

    async def update_user(self, node):
        value_json = json.dumps(node.dump())
        await self.server.set(node.username, value_json)


    async def update_follower(self, request_data):
        following_username = request_data["following_username"]
        self.node.followers.append(following_username)
        await self.update_user(self.node)


    async def send_message_to_node(self, node, message):
        
        try:
            reader, writer = await asyncio.open_connection(node.address, node.port)

            writer.write(message)

            await writer.drain()

            writer.close()

        except Exception as e:
            print(e)
            return False

        return reader, writer

    async def save_message(self, message):
        self.node.messages.append((message,datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

        data = {"username": self.node.username, "message": self.node.messages}
        json_data = json.dumps(data)

        await self.server.set(self.node.username + "_tl", json_data)

        


    async def post_message(self):
        print("Entrei no post")
        messages = self.node.messages

        
        
        # followers_nodes = []
        # for user in self.node.followers:
        #     followers_nodes.append(await self.get_user_by_username(user))

        # tasks = []

        # for follower_node in followers_nodes:
        #     tasks.append(self.send_message_to_node(follower_node), json_data.encode())

        # await asyncio.gather(tasks)
        #success = [followers_nodes[i] for i in range(len(tasks_results)) if tasks_results[i] == True]
        
        
        #return success, unsuccess

    async def get_timeline(self):     
        data = {"req_type": constants.GET}
        json_data = json.dumps(data)

        followings_nodes = []
        for user in self.node.following:
            # followings_nodes.append(await self.get_user_by_username(user))
            print(user+"_tl")
            result = await self.server.get(user+"_tl")
            print(result)
        

        # tasks = []

        # for following_node in followings_nodes:
        #     tasks.append(self.send_message_to_node(following_node), json_data.encode())


        # await asyncio.gather(tasks)
        
        
    async def show_timeline(self, request):
        print("Entrei no show")

        message = request["message"]
        username = request["username"]
        print("User " + username + " published:")
        for m in message:
            print(m)

    async def show_own_messages(self):
        result = await self.server.get(self.node.username+"_tl")
        print(result)
        
        


