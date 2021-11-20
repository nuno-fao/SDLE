import zhelpers
import zmq
import sys


def start(ID):
    context = zmq.Context().instance()
    socket = context.socket(zmq.REQ)
    identity = "Client_" + str(ID)
    socket.setsockopt_string(zmq.IDENTITY, identity)
    socket.connect("tcp://localhost:5672")
    return socket

def subscribe(topic, ID):
    # client with id = ID subscribes to topic
    socket = start(ID)
    socket.send("SUBSCRIBE {topic}".format(topic=topic).encode())
    response = socket.recv()
    print(response)

def unsubscribe(topic , ID):
    socket = start(ID)
    socket.send("UNSUBSCRIBE {topic}".format(topic=topic).encode())
    response = socket.recv()
    print(response)

def get(topic, ID):
    socket = start(ID)
    socket.send("GET {topic}".format(topic=topic).encode())
    response = socket.recv()
    print(response)

subscribe("TESTE",1)
unsubscribe("TESTE",1)
subscribe("TESTE",1)
get("TESTE", 1)

