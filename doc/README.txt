The project was developed in python 3.9.2.

Running the project:
To run the project first run the serve with the command "python service.py".
After that we can run the requests from the client from the test_api.py file. To execute the operations we use the python function eval that calls the respective method in the client file.
With this being said, some examples on how to run the 4 operations:
Subscribe - python test_api.py "subscribe('topic1', 1)"
Put - python test_api.py "put('topic1', 'message1')" 
Get - python test_api.py "get('topic1', 1)"
Unsubscribe - python test_api.py "unsubscribe('topic1', 1)"

There is also two modifications that we implemented: a state function that shows the content of the server and a small modification to the get method where we can simulate a client crash.
State - python test_api.py "state()"
Get - python test_api.py "get('topic1', 1, True)"