import logging
import asyncio
import json
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
        # self.prompt = Prompt(self.loop)  
        
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
            return self.node
        
        else:
            raise Exception("Username already exists!")

    async def login(self, username):
        
        user = await self.server.get(username)
        print("USER: ", user)

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
            return self.node

        else:
            raise Exception("User does not exist!")


    async def get_user_by_username(self, username):
        user = await self.server.get(username)

        user = json.loads(user)

        if user != None:
            value = {"followers": user["followers"], 
                    "following": user["following"], 
                    "address": self.address, 
                    "port": self.port, 
                    "message_number": user["message_number"], 
                    "redirects": user["redirects"],
                    "messages": user["messages"],
                    "username": username
                }
            node = KNode(value)
            return node


    async def follow_user(self, username):
        user = await self.get_user_by_username(username)

        user.followers.append(self.node.username)
        self.node.following.append(username)
        
        #TODO: implement connection between 2 peers
        # reader, writer = await asyncio.open_connection(user.port, user.address, loop=self.loop)

        # self.node.show_following()



