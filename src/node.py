class KNode:
    def __init__(self, value):
        self.followers = value["followers"]
        self.following = value["following"]
        self.messages = value["messages"]


    def parse_node(self):
        print("Logged in successfully")
        # print (self.followers)
