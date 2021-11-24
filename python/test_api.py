import zhelpers
from pub import put
from client import get, subscribe, unsubscribe, state
from threading import Thread
import random
# from service import state
import sys
import concurrent.futures


def test_puts():
    #PUBLISH 20 TOPICS
    for i in range(20):
        topic = "Topic_" + str(i % 5)
        # print("PUBLISHING MESSAGE")
        put(topic, zhelpers.generate_random_message())

def publish_topic(topic):
    for i in range(5):
        topic = "Topic_" + str(i % 5)
        put(topic, zhelpers.generate_random_message())


def test_gets(start = 0):
    for i in range(start, start + 5):
        topic = "Topic_" + str(i % 5)
        subscribe(topic, i)
        put(topic, zhelpers.generate_random_message())
        get(topic, i)
        unsubscribe(topic, i)

def test_concurrency():
    threads = [Thread(target=test_gets, args=(i*5,)) for i in range(2)]
    for t in threads:
        t.start()

    

    # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    #     futures.append(executor.submit(test_gets))
    # print(futures)
    # concurrent.futures.wait(futures)    
    # for future in concurrent.futures.as_completed(futures):
    #     print("future: ", future.result())



# on successful return of put() on a topic, the service guarantees that the message will eventually
#  be delivered "to all subscribers of that topic", as long as the subscribers keep calling get()

def publish(topic, n=10):
    for i in range(n):
        put(topic, zhelpers.generate_random_message())

if (len(sys.argv) > 1):
    call = sys.argv[1]
    eval(call)
else:
    #do something
    test_gets()

# test_gets()
# get("Topic_0", 0)