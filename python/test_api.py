import zhelpers
from pub import put
from client import get, subscribe, unsubscribe

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


def test_gets():
    # test_puts()
    for i in range(5):
        topic = "Topic_" + str(i % 5)
        subscribe(topic, i)
        put(topic, zhelpers.generate_random_message())
        get(topic, i)
        unsubscribe(topic, i)

test_gets()
# get("Topic_0", 0)