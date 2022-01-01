class KNode:
    def __init__(self, value):
        self.username = value["username"]
        self.followers = value["followers"]
        self.following = value["following"]
        self.messages = value["messages"]
        self.port = value["port"]
        self.address = value["address"]

    def show_following(self):
        print (f"{self.username} is following: ")
        print(self.following)

    
    def show_followers(self):   
        print (f"{self.username} is followed by: ")
        print(self.followers)