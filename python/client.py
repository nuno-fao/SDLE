from zmq.sugar.frame import Message
import zhelpers
import zmq
import sys
import time
from zhelpers import context


SERVICE_ADDRESS = "tcp://localhost:5672"


def subscribe(topic, ID):
    # client with id = ID subscribes to topic
    socket = zhelpers.start(ID, SERVICE_ADDRESS)
    socket.send("SUBSCRIBE {topic}".format(topic=topic).encode(), zmq.DONTWAIT)
    socket.RCVTIMEO = 5000
    response = None
    try:
        response, status = socket.recv_multipart()
    except Exception as e:
        if (e.errno == zmq.EAGAIN):
            raise IOError("Could not receive response. Server is down!")
    socket.close()
    print(f"Subscribe operation status = {status.decode('utf8')}")


def unsubscribe(topic , ID):
    socket = zhelpers.start(ID, SERVICE_ADDRESS)
    socket.send("UNSUBSCRIBE {topic}".format(topic=topic).encode())
    socket.RCVTIMEO = 5000
    response = None
    try:
        response, status = socket.recv_multipart()
    except Exception as e:
        if (e.errno == zmq.EAGAIN):
            raise IOError("Could not receive response. Server is down!")
    socket.close()
    print(f"Unsubscribe operation status = {status.decode('utf8')}")


def get(topic, ID, crash=False):
    socket = zhelpers.start(ID, SERVICE_ADDRESS)
    socket.send("GET {topic}".format(topic=topic).encode(), zmq.DONTWAIT)
    socket.RCVTIMEO = 5000
    if crash:
        # time.sleep(15) #simulates a crash before receiving the message
        time.sleep(15)
        # return None
    response = None
    try:
        response, status = socket.recv_multipart()
    except Exception as e:
        if (e.errno == zmq.EAGAIN):
            raise IOError("Could not receive response. Server is down!")
    socket.close()
    time.sleep(0.1)

    if int(status.decode("utf8")) == -1:
        print(f"Couln't retrieve message from topic {topic}")
    else:
        print("Consumed message: {message}.".format(message = response.decode("utf8") ))

    client_ACK = context.socket(zmq.PUSH)
    port = zhelpers.get_address("Client_" + str(ID))
    client_ACK.bind("tcp://*:" + str(port))

    # # Comment the next 2 lines to simulate crash on client
    # #time.sleep(10) sleep to simulate a delay receiving an ACK
    client_ACK.send(b"ACK") 
    client_ACK.close()




def state():
    socket = zhelpers.start_pub_socket(SERVICE_ADDRESS)
    socket.send(b"STATE", zmq.DONTWAIT)
    socket.RCVTIMEO = 5000
    response = None
    try:
        response, status = socket.recv_multipart()
    except Exception as e:
        if (e.errno == zmq.EAGAIN):
            raise IOError("Could not receive response. Server is down!")
    socket.close()
    print("Service state:\n" + response.decode("utf8"))

