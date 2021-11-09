#
#   Weather update client
#   Connects SUB socket to tcp://localhost:5556
#   Collects weather updates and finds avg temp in zipcode
#

import sys
import zmq
from zmq.sugar import poll


#  Socket to talk to server
context = zmq.Context()
socket1 = context.socket(zmq.SUB)
socket2 = context.socket(zmq.SUB)

print("Collecting updates from weather server...")
socket1.connect("tcp://localhost:5557")
socket2.connect("tcp://localhost:5556")

# Subscribe to zipcode, default is NYC, 10001
zip_filter = sys.argv[1] if len(sys.argv) > 1 else "2"
socket1.setsockopt_string(zmq.SUBSCRIBE, zip_filter)
socket2.setsockopt_string(zmq.SUBSCRIBE, zip_filter)

poller = zmq.Poller()
poller.register(socket1, zmq.POLLIN)
poller.register(socket2, zmq.POLLIN)


while True:
    try:
        socks = dict(poller.poll(-1))
        if socks.get(socket1) == zmq.POLLIN:
            string = socket1.recv()
            print(22222222)

        if socks.get(socket2) == zmq.POLLIN:
            string = socket2.recv()
            print(1111111)
        zipcode, temperature, relhumidity = string.split()
        print(zipcode, temperature)
        break
    except KeyboardInterrupt:
        break