import json

class KNode:
    def __init__(self, value):
        self.username = value["username"]
        self.followers = value["followers"]
        self.following = value["following"]
        self.messages = []
        self.port = value["port"]
        self.address = value["address"]
        self.online = value["online"]
        self.timeline = value["timeline"]
        self.followers_with_timeline = value["followers_with_timeline"]
        self.followers_timestamp = value["followers_timestamp"]

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
            "port": self.port,
            "address": self.address,
            "online": self.online,
            "timeline": self.timeline,
            "followers_with_timeline": self.followers_with_timeline,
            "followers_timestamp": self.followers_timestamp
        }

        return value
    
    def save_messages(self):
        dict_to_save = {
            "messages": self.messages
        }
        out_file = open(self.username + "_messages.json", "w")
        json.dump(dict_to_save,out_file)
        out_file.close()

    def load_messages(self):
        f = open(self.username + '_messages.json')
        data = json.load(f)

        self.messages = data["messages"]
        
