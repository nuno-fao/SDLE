import asyncio
import sys
import node
import menu
from server import KServer
import json
from threading import Thread

PORT_FLAG = "-p"
BOOTSTRAP_FLAG = "-b"


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
    #while True: 
       
    
        
    

if __name__ == '__main__':
    main()