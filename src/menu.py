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
    print("[0] Exit")

    loop = kserver.loop
    option = input("Option > ")

    if not option.isnumeric():
        print("Input must be a number between 0 and 1!")
        return None

    option = int(option)

    if option == 1 or option == 2:
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

    elif option == 0:
        kserver.close_server()
        return False

    return None


def main_menu(kserver):
    print("[1] Follow user")
    print("[2] Unfollow user")
    print("[3] Show followers")
    print("[4] Show following")
    print("[5] Post message")
    print("[6] Timeline")
    print("[0] Exit")

    option = input("option > ")

    if not option.isnumeric():
        print("Input must be a number between 0 and 6!")
        return None

    option = int(option)

    loop = kserver.loop   

    if option == 1:
        try:
            username = input("Username: ")

            if username == kserver.node.username:
                print("\nYou cannot follow yourself!\n")

            future = asyncio.run_coroutine_threadsafe(kserver.follow_user(username), loop)
            future.result()
            main_menu(kserver)
        
        except Exception as e:
            print(e)

    elif option == 2:
        try:
            username = input("Username: ")
            future = asyncio.run_coroutine_threadsafe(kserver.unfollow_user(username), loop)
            future.result()
            main_menu(kserver)
        
        except Exception as e:
            print(e)

    elif option == 3:
        kserver.node.show_followers()
        main_menu(kserver)

    elif option == 4:
        kserver.node.show_following()
        main_menu(kserver)


    elif option == 5:
        message = input("Message: ")
        future = asyncio.run_coroutine_threadsafe(kserver.save_message(message), loop)
        future.result()
        main_menu(kserver)
    
    elif option == 6:
        future = asyncio.run_coroutine_threadsafe(kserver.get_timeline(), loop)
        kserver.show_timeline(future.result())
        main_menu(kserver)

    elif option == 0:
        future = asyncio.run_coroutine_threadsafe(kserver.logout(), loop)
        future.result()
        return