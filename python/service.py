"""
    PROXY
"""
import time
import random
from threading import Thread
from zhelpers import context
import json

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
        return [b"Put operation failed.", b"-1"]

    if topic not in sequence_number:
        sequence_number[topic] = 0
    else:
        sequence_number[topic] += 1
    message_list.append((topic, message, sequence_number[topic]))
    return [b"Put operation executed.", b"0"]



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
        return [b"Invalid. No clients subscribed to the topic.", b"-1"]
    sorted_messages = sorted(message_list, key = lambda x: (x[0], x[2]))
    idx = clients_idx[address][topic]
    topic_messages = [x for x in sorted_messages if determine_unreceived(x,topic,idx)] #possible messages from the required topic
    if len(topic_messages) < 1:
        return [b"All messages were read from this topic", b"-1"]
    message = topic_messages[0][1].encode()
    clients_idx[address][topic]+=1
    return [message, b"0"]




def subscribe_topic(topic, address):
    if topic not in sequence_number:
        sequence_number[topic] = 0
    if address not in clients_idx.keys():
        clients_idx[address] = {topic : sequence_number[topic] + 1} 
        return [b"Subscribe to topic.", b"0"]
    elif topic not in clients_idx[address]:
        clients_idx[address][topic] = sequence_number[topic] + 1
        return [b"Resubscribe to topic.", b"-1"]
    else:
        return [b"Already subscribed to topic.", b"-1"]

def unsubscribe_topic(topic, address):
    if address not in clients_idx.keys() or topic not in clients_idx[address].keys():
        return [b"Client not subscribed to topic", b"-1"]
    
    clients_idx[address].pop(topic)
    clean_clients()
    return [b"Successfully unsubscribed to topic", b"0"]



def handle_REQ(request, address = None):
    req_list = request.decode('utf8').split(" ")
    req_type = req_list[0]
    if req_type == "PUT":
        return insert_message(req_list[1], " ".join(req_list[2:]), address)
    elif req_type == "GET":
        return retrieve_message(req_list[1], address)
    elif req_type == "SUBSCRIBE":
        return subscribe_topic(req_list[1], address)
    elif req_type == "UNSUBSCRIBE":
        return unsubscribe_topic(req_list[1], address)
    elif req_type == "STATE":
        return [state().encode(), b"0"]

    return b"Invalid Request. Try again."

def determine_delivered(oldest_subs,x):
    (topic1, _, seq1) = x
    if topic1 not in oldest_subs:
        return False
    elif oldest_subs[topic1] > seq1:
        return False
    else:
        return True

def clean_clients():
    # cleans information about clients not subscribed to any topics
    toRemoveKeys = []
    for client in clients_idx.keys():
        if list(clients_idx[client].keys()) == []:
            toRemoveKeys.append(client)
    for key in toRemoveKeys:
        clients_idx.pop(key)



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
    


def ack_message(client, address, response, socket, topic):
    tries = 5
    count = 1
    pull_socket.RCVTIMEO = 2000
    while count <= tries:
        try:
            socket.recv() #socket times out after 2 seconds
            # Received ACK
            break
        except Exception:
            print("Timeout occured: Server is handling ...")
            time.sleep(2)
            client.send_multipart([address, b"", response[0], response[1]])
        count += 1
    socket.close()
    if count > tries:
        print(address.decode("utf8") + " could not recover. Message will be rolled back.")
        rollback_message(topic, address.decode("utf8"))

        
def save_changes():
    global sequence_number
    global message_list
    global clients_idx
    dict_to_save = {
        "sequence_numbers": sequence_number,
        "messages":message_list,
        "clients":clients_idx
    }
    out_file = open("server_state.json", "w")
    json.dump(dict_to_save,out_file)
    out_file.close()

def load_state():
    global sequence_number
    global message_list
    global clients_idx

    f = open('server_state.json')
    data = json.load(f)

    sequence_number = data["sequence_numbers"]
    clients_idx=data["clients"]
    for x,y,z in data["messages"]:
        message_list.append((x,y,z))

load_state()
gc = Thread(target=garbage_collect)
gc.daemon = True  # allows us to kill the process on ctrl+c
gc.start()

def state():
    message = "="*20 + "Clients information" + "="*20 + "\n"
    for client in clients_idx.keys():
        topics = clients_idx[client].keys()
        message += (f"Client {client} is subscribed to {len(topics)} topics\n")
        message += "\t" + ", ".join(topics) + "\n"

    message += "="*20 + "Topics information" + "="*20 + "\n"

    all_topics = list(set([x[0] for x in message_list]))
    for topic in all_topics:
        n = len([x for x in message_list if x[0] == topic])
        message += f"\ttopic {topic}: {n} messages\n"
    return message


while True:
    rewrite = False
    socks = dict(poller.poll())

    if socks.get(client) == zmq.POLLIN:
        address, empty, message = client.recv_multipart()
        response = handle_REQ(message, address.decode('utf8'))
        client.send_multipart([address, empty, response[0], response[1]], zmq.DONTWAIT) 
        if message.decode('utf8').split(" ")[0] == "GET":
            port = zhelpers.get_address(address.decode("utf8"))
            pull_socket = zhelpers.start_ACK_socket("tcp://127.0.0.1:" + str(port))
            
            ack_thread = Thread(target=ack_message, args=(client, address, response, pull_socket, message.decode('utf8').split(" ")[1]))
            ack_thread.daemon = True
            ack_thread.start()
        rewrite = True
    

    if socks.get(publisher) == zmq.POLLIN:
        address, empty, message = publisher.recv_multipart()
        # print(message.decode('utf8'))
        response = handle_REQ(message, address.decode('utf8'))
        publisher.send_multipart([address, empty, response[0], response[1]], zmq.DONTWAIT)
        rewrite = True

    if rewrite:
        save_changes()




publisher.close()
client.close()

