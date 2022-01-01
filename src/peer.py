import asyncio
import sys
import node
import menu
from server import KServer
import json
from threading import Thread
from prompt import Prompt

PORT_FLAG = "-p"
BOOTSTRAP_FLAG = "-b"


async def register(server, username, address, port):

    user = await server.get(username)

    #there are no user with that username
    print("USER: " + str(user))
    if user is None:
        new_user = {
            "follower": [],
            "following": [],
            "address": address,
            "port": port
        }

        new_user_json = json.dumps(new_user)
        await server.set(username, new_user_json)

    else:
        raise Exception("Username already exists!")



def main():

    args = sys.argv
    if len(args) != 5 and len(args) != 3:
        raise RuntimeError("Invalid arguments!")


    port = int(args[args.index(PORT_FLAG) + 1])

    kserver = KServer("127.0.0.1", port)
    
    if BOOTSTRAP_FLAG in args:
        address = args[args.index(BOOTSTRAP_FLAG) + 1]
        address_port = address.split(":")
        server, loop = kserver.start([(address_port[0], int(address_port[1]))])
        Thread(target=loop.run_forever, daemon=True).start()

    else:
        server, loop = kserver.start()
        
        Thread(target=loop.run_forever, daemon=True).start()


    node = menu.auth_menu(kserver)
    while node == None:
        node = menu.auth_menu(kserver)

    
    menu.main_menu(kserver)
    
    while True: pass
    
        
    

if __name__ == '__main__':
    main()