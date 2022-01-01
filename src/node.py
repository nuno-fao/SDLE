class KNode:
    def __init__(self, value):
        self.username = value["username"]
        self.followers = value["followers"]
        self.following = value["following"]
        self.messages = value["messages"]
        self.port = value["port"]
        self.address = value["address"]

    def show_node(self):
        print(f"Node {self.username}")
        print (f"Address {self.address}:{self.port}")

    def show_following(self):
        print (f"{self.username} is following: ")
        print(self.following)

    
    def show_followers(self):
        print (f"{self.username} is followed by: ")
        print(self.followers)

    def dump(self):
        value = {
            "username": self.username,
            "followers": self.followers,
            "following": self.following,
            "messages": self.messages,
            "port": self.port,
            "address": self.address
        }

        return value
