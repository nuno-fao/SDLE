from server import KServer
import asyncio
import sys

message_queue = asyncio.Queue()


def recv_input(loop=None):
    global message_queue
    if loop == None:
        loop = asyncio.get_event_loop()
    asyncio.ensure_future(message_queue.put(sys.stdin.readline()), loop=loop)

async def read(msg, loop=None):
    print(msg)
    
    if loop == None:
        loop = asyncio.get_event_loop()
    
    sys.stdout.flush()
    loop.add_reader(sys.stdin, recv_input)
    inp = await message_queue.get()
    loop.remove_reader(sys.stdin)
    print(inp)
    return inp



def auth_menu(kserver):

    sys.stdout.flush()
    print("[1] Register")
    print("[2] Login")

    loop = kserver.loop
    option = int(input("Option > "))
    username = input("Username: ")
    
    if option == 1:
        try:
            future = asyncio.run_coroutine_threadsafe(kserver.register(username), loop)
            return future.result()
        
        except Exception as e:
            print(e)

    elif option == 2:
        try:
            future = asyncio.run_coroutine_threadsafe(kserver.login(username), loop)
            return future.result()
        
        except Exception as e:
            print(e)

    return None


def main_menu(kserver):
    print("[1] Follow user")
    print("[2] Show followers")
    option = int(input("option > "))
    loop = kserver.loop
    

    if option == 1:
        try:
            username = input("Username: ")
            future = asyncio.run_coroutine_threadsafe(kserver.follow_user(username), loop)
            return future.result()
        
        except Exception as e:
            print(e)

    elif option == 2:
        kserver.node.show_followers()