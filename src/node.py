import logging
import asyncio
import sys

from kademlia.network import Server

DEBUG = False

def start(port, bootstrap_address=None, bootstrap_port=None):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    if DEBUG:
        log = logging.getLogger('kademlia')
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)
    
    loop = asyncio.get_event_loop()

    if DEBUG:
        loop.set_debug(True)

    server = Server()
    loop.run_until_complete(server.listen(port))

    #not first node in the network
    if bootstrap_port is not None:
        loop.run_until_complete(server.bootstrap([(bootstrap_address, bootstrap_port)]))


    return server, loop