import zhelpers
import zmq
import sys
import time
from zhelpers import context


SERVICE_ADDRESS = "tcp://localhost:5672"
ACK_ADDRESS = "tcp://*:5673"
# client_ACK = context.socket(zmq.PUSH)
# client_ACK.bind(ACK_ADDRESS)


def subscribe(topic, ID):
    # client with id = ID subscribes to topic
    socket = zhelpers.start(ID, SERVICE_ADDRESS)
    socket.send("SUBSCRIBE {topic}".format(topic=topic).encode())
    response = socket.recv()
    socket.close()

def unsubscribe(topic , ID):
    socket = zhelpers.start(ID, SERVICE_ADDRESS)
    socket.send("UNSUBSCRIBE {topic}".format(topic=topic).encode())
    response = socket.recv()
    socket.close()

def get(topic, ID):
    socket = zhelpers.start(ID, SERVICE_ADDRESS)
    socket.send("GET {topic}".format(topic=topic).encode())
    response = socket.recv()
    socket.close()
    print ("Received response: " + response.decode("utf8"))
    time.sleep(0.1)

    client_ACK = context.socket(zmq.PUSH)
    port = zhelpers.get_address("Client_" + str(ID))
    client_ACK.bind("tcp://*:" + str(port))

    # Comment the next 2 lines to simulate crash on client
    client_ACK.send(b"ACK") 
    client_ACK.close()
    
    
    #TODO: close client_ACK socket (?)

