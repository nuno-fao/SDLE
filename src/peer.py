import asyncio
import sys
import node
import menu
from server import KServer, scheduler, time
import json
from threading import Thread
import sync

PORT_FLAG = "-p"
BOOTSTRAP_FLAG = "-b"

def start_garbage_collector(kserver):
    scheduler_aux = scheduler(time.time, time.sleep)
    scheduler_aux.enter(1, 200, kserver.run_garbage_collector, (scheduler_aux,))
    scheduler_aux.run()


def main():

    args = sys.argv
    if len(args) != 5 and len(args) != 3:
        raise RuntimeError("Invalid arguments!")


    port = int(args[args.index(PORT_FLAG) + 1])

    kserver = KServer("127.0.0.1", port)
    
    if BOOTSTRAP_FLAG in args:
        address = args[args.index(BOOTSTRAP_FLAG) + 1]
        address_port = address.split(":")
        loop = kserver.start([(address_port[0], int(address_port[1]))])
        Thread(target=loop.run_forever, daemon=True).start()

    else:
        loop = kserver.start()
        
        Thread(target=loop.run_forever, daemon=True).start()


    node = menu.auth_menu(kserver)
    while node == None:
       node = menu.auth_menu(kserver)

    if node == False:
        return
  
    gc = Thread(target=start_garbage_collector, args=(kserver,))
    gc.daemon = True  # allows us to kill the process on ctrl+c
    gc.start()

    synchronize_thread = Thread(target=sync.synchronize, daemon=True)
    synchronize_thread.start()
    
    menu.main_menu(kserver)   
        
    

if __name__ == '__main__':
    main()