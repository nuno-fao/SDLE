"""
    PROXY
"""
import time
import random
from threading import Thread
from zhelpers import context

import zmq
import zhelpers


# context = zmq.Context.instance()

publisher = context.socket(zmq.ROUTER)
publisher.bind("tcp://*:5671")

ACK_pub = context.socket(zmq.ROUTER)
ACK_pub.bind("tcp://*:5670")

client = context.socket(zmq.ROUTER)
client.bind("tcp://*:5672")


sequence_number = {}
message_list = []
# [(topic1, msg1, seq1), (topic2, msg2, seq2), (topic1, msg3, seq3)]

clients_idx = {} 
# {client_1: {topic1: idx1, topic2: idx2}, client_1: {topic1: idx1, topic3: idx2}}
# for each client, track the pointer in each topic



# Initialize poll set
poller = zmq.Poller()
poller.register(publisher, zmq.POLLIN)
poller.register(client, zmq.POLLIN)


def garbage_collect():
    while True:
        clean_messages()
        print(clients_idx,message_list)
        time.sleep(5)

def check_subscribers(topic):
    for client in clients_idx.keys():
        for _topic_, idx in clients_idx[client].items():
            if _topic_ == topic:
                return True
    
    return False



def insert_message(topic, message, address): #inserts message in topic
    global sequence_number
    #check if any subscribers are subscribed to topic
    if not check_subscribers(topic):
        # sequence_number.pop(topic)
        print("DISCARDING MESSAGE: no subscribers.")
        return None

    if topic not in sequence_number:
        sequence_number[topic] = 0
    else:
        sequence_number[topic] += 1
    message_list.append((topic, message, sequence_number[topic]))



def determine_unreceived(x,topic,idx):
    if x[0]==topic and x[2]>=idx:
        return True
    else:
        return False


def rollback_message(topic, address):
    clients_idx[address][topic] -= 1


def retrieve_message(topic, address):
    global clients_idx
    if address not in clients_idx.keys() or topic not in clients_idx[address].keys():
        return b"Invalid. No clients subscribed to the topic."
    sorted_messages = sorted(message_list, key = lambda x: (x[0], x[2]))
    idx = clients_idx[address][topic]
    topic_messages = [x for x in sorted_messages if determine_unreceived(x,topic,idx)] #possible messages from the required topic
    print("sorted_messages: ", sorted_messages)
    if len(topic_messages) < 1:
        return b"All messages were read from this topic"
    message = topic_messages[0][1].encode()
    clients_idx[address][topic]+=1
    return message




def subscribe_topic(topic, address):
    if topic not in sequence_number:
        sequence_number[topic] = 0
    if address not in clients_idx.keys():
        clients_idx[address] = {topic : sequence_number[topic] + 1} 
        return b"Subscribe to topic."
    elif topic not in clients_idx[address]:
        clients_idx[address][topic] = sequence_number[topic] + 1
        return b"Resubscribe to topic."
    else:
        return b"Already subscribed to topic."

def unsubscribe_topic(topic, address):
    if address not in clients_idx.keys() or topic not in clients_idx[address].keys():
        return b"Client not subscribed to topic"
    
    clients_idx[address].pop(topic)
    return b"Successfully unsubscribed to topic"



def handle_REQ(request, address = None):
    req_list = request.decode('utf8').split(" ")
    req_type = req_list[0]
    if req_type == "PUT":
        insert_message(req_list[1], " ".join(req_list[2:]), address)
    elif req_type == "GET":
        return retrieve_message(req_list[1], address)
    elif req_type == "SUBSCRIBE":
        return subscribe_topic(req_list[1], address)
    elif req_type == "UNSUBSCRIBE":
        return unsubscribe_topic(req_list[1], address)

    return "response to request".encode()

def determine_delivered(oldest_subs,x):
    (topic1, _, seq1) = x
    if topic1 not in oldest_subs:
        return False
    elif oldest_subs[topic1] > seq1:
        return False
    else:
        return True


def clean_messages():

    global clients_idx
    global message_list

    oldest_subs={}
    for client in clients_idx:
        for topic,index in clients_idx[client].items():
            if topic not in oldest_subs:
                oldest_subs[topic] = index
            elif oldest_subs[topic] > index:
                oldest_subs[topic] = index

    message_list[:] = [x for x in message_list if determine_delivered(oldest_subs,x)]
    
    ### clean information about clients not subscribed to any topic
    toRemoveKeys = []
    for client in clients_idx.keys():
        if list(clients_idx[client].keys()) == []:
            toRemoveKeys.append(client)
    for key in toRemoveKeys:
        clients_idx.pop(key)

def ack_message(client, address, empty, response, socket):
    tries = 3
    count = 1
    while count <= 3:
        try:
            socket.recv() #socket times out after 1 second
            print ("Received ACK")
            break
        except:
            print("Timeout occured: Server is handling ...")
            time.sleep(2)
            client.send_multipart([address, empty, response])
    socket.close()
        



gc = Thread(target=garbage_collect)
gc.daemon = True  # allows us to kill the process on ctrl+c
gc.start()

while True:
    socks = dict(poller.poll())

    if socks.get(client) == zmq.POLLIN:
        previous_sn, previous_ml, previous_ci = sequence_number, message_list, clients_idx
        address, empty, message = client.recv_multipart()
        response = handle_REQ(message, address.decode('utf8'))
        # print("Sending response: " + response.decode('utf8'))
        client.send_multipart([address, empty, response])
        port = zhelpers.get_address(address.decode("utf8"))
        pull_socket = zhelpers.start_ACK_socket("tcp://127.0.0.1:" + str(port))
        # print("Port: " , port)
        if message.decode('utf8').split(" ")[0] == "GET":
            pull_socket.RCVTIMEO = 2000
            ack_thread = Thread(target=ack_message, args=(client, address, empty, response, pull_socket,))
            ack_thread.daemon = True
            ack_thread.start()
            # pull_socket.RCVTIMEO = 2000
            # try:
            #     pull_socket.recv() #socket times out after 1 second
            #     print ("Received ACK")
            #     pull_socket.close()
            # except:
            #     topic = message.decode('utf8').split(" ")[1]
            #     #rollback_message(topic, address.decode("utf8"))
            #     print("Timeout occured: Server is handling ...")
            #     # sequence_number, message_list, clients_idx = previous_sn, previous_ml, previous_ci
            #     pull_socket.close()
    

    if socks.get(publisher) == zmq.POLLIN:
        address, empty, message = publisher.recv_multipart()
        response = handle_REQ(message, address.decode('utf8'))
        publisher.send_multipart([address, empty, response])


publisher.close()
client.close()

