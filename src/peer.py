import sys
import node
import json

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


def main():

    args = sys.argv
    if len(args) != 5 and len(args) != 3:
        raise RuntimeError("Invalid arguments!")

    
    port = int(args[args.index(PORT_FLAG) + 1])

    
    if BOOTSTRAP_FLAG in args:
        address = args[args.index(BOOTSTRAP_FLAG) + 1]
        address_port = address.split(":")
        server, loop = node.start(port, address_port[0], int(address_port[1]))
        loop.run_forever()
        
    else:
        server, loop = node.start(port)
        loop.run_forever()
               
        
    

if __name__ == '__main__':
    main()