import asyncio
import sys
import node
import json
from threading import Thread
from prompt import Prompt

PORT_FLAG = "-p"
BOOTSTRAP_FLAG = "-b"

# handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# log = logging.getLogger('kademlia')
# log.setLevel(logging.DEBUG)
# log.addHandler(handler)

# BOOTSTRAP_NODES = [('127.0.0.1', 8468)]



# async def run():
#     server = Server()
#     await server.listen(8469)
#     await server.bootstrap([('127.0.0.1', 8468)])
#     await server.set("key", "val")
#     server.stop()

# asyncio.run(run())

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

    
    if BOOTSTRAP_FLAG in args:
        address = args[args.index(BOOTSTRAP_FLAG) + 1]
        address_port = address.split(":")
        server, loop = node.start(port, address_port[0], int(address_port[1]))
        Thread(target=loop.run_forever, daemon=True).start()
                
    else:
        server, loop = node.start(port)
        
        Thread(target=loop.run_forever, daemon=True).start()


    #prompt = Prompt(loop)
    username = input("Username: ")
    try:
        asyncio.run_coroutine_threadsafe(register(server, username, "127.0.0.1", port), loop)
    except Exception:
        print(Exception)

    while True:
        a = 1

    # print(username)

    

    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(register(server, "127.0.0.1", port, prompt))
    # Thread(target=loop.run_forever, daemon=True).start()
    # future = asyncio.run_coroutine_threadsafe(register(server, "127.0.0.1", port, prompt),loop)
    
    # print(future.result())

    
        
    

if __name__ == '__main__':
    main()