The project was developed in python 3.9.2.

To have the zmq library just run the following command: "pip install pyzmq".

Running the project:
To run the project first run the serve with the command "python service.py".
After that we can run the requests from the client from the test_api.py file. To execute the operations we use the python function eval that calls the respective method in the client or publisher file.
With this being said, some examples on how to run the 4 operations:
Subscribe - python test_api.py "subscribe('topic1', 1)" 
    (first argument is the topic name and the second is the subscriber id)
Put - python test_api.py "put('topic1', 'message1')" 
    (first argument is the topic name and the second is the message itself)
Get - python test_api.py "get('topic1', 1)"
    (first argument is the topic name and the second is the subscriber id)
Unsubscribe - python test_api.py "unsubscribe('topic1', 1)"
    (first argument is the topic name and the second is the subscriber id)

There is also two modifications that we implemented: a state function that shows the content of the server and a small modification to the get method where we can simulate a client crash.
State - python test_api.py "state()"
Get - python test_api.py "get('topic1', 1, True)"
