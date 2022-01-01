import logging
import asyncio
import json
import constants
from threading import Thread
from kademlia.network import Server
from node import KNode


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
                    "message_number": 0,
                    "redirects": {},
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
                    "message_number": user["message_number"], 
                    "redirects": user["redirects"],
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
                    "message_number": user["message_number"], 
                    "redirects": user["redirects"],
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
        self.update_user(self.node)

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
                self.update_follower(request)

    def update_user(self, node):
        value_json = json.dumps(node.dump())
        self.server.set(node.username, value_json)


    def update_follower(self, request_data):
        following_username = request_data["following_username"]
        self.node.followers.append(following_username)
        self.update_user(self.node)

