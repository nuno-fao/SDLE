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
    response = None
    socket.RCVTIMEO = 5000
    try:
        message, status = socket.recv_multipart()
    except Exception as e:
        if (e.errno == zmq.EAGAIN):
            raise IOError("Could not receive response. Server is down!")
    socket.close()

    print(f"Put status = {status.decode('utf8')}")
