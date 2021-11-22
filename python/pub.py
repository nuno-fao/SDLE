#
#   Request-reply client in Python
#   Connects REQ socket to tcp://localhost:5559
#   Sends "Hello" to server, expects "World" back
#

import zhelpers
import zmq
import sys

#  Prepare our context and sockets
def start():
    context = zmq.Context().instance()
    socket = context.socket(zmq.REQ)
    zhelpers.set_id(socket)
    socket.connect("tcp://localhost:5671")
    return socket

def put(topic, message):
    socket = start()
    socket.send("PUT {topic} {message}".format(topic=topic, message=message).encode())
    response = socket.recv()
    #print("Successfully published message: " + message)

#put("TESTE", zhelpers.generate_random_message()) 
