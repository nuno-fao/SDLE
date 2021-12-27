import logging
import asyncio
import json
from kademlia.network import Server

DEBUG = False

class KServer:
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def start(self, bootstrap_nodes):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        log = logging.getLogger('kademlia')
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)
        
        self.loop = asyncio.get_event_loop()

        self.server = Server()
        self.loop.run_until_complete(self.server.listen(self.port))
        self.loop.run_until_complete(self.server.bootstrap(bootstrap_nodes))

        return self.loop

    def close_server(self):
        self.server.stop()


    async def register(self, username):
        user = await self.server.get(username)

        if user is None:
            value = {"followers": [], 
                    "following": {}, 
                    "address": self.address, 
                    "port": self.port, 
                    "message_number": 0, 
                    "redirects": {}
                }

            value_json = json.dumps(value)
            await self.server.set(username, value_json)

            return value
        
        else:
            raise Exception("Username already exists!")

    async def login(self, username):
        user = self.server.get(username)
        user = json.loads(user)

        if user is not None:
            value = {"followers": user["followers"], 
                    "following": user["following"], 
                    "address": self.address, 
                    "port": self.port, 
                    "message_number": user["message_number"], 
                    "redirects": user["redirects"]
                }
            value_json = json.dumps(value)
            await self.server.set(username, value_json)

            return value

        else:
            raise Exception("User does not exist!")


