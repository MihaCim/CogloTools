
class Node:

    def __init__(self):
        self.post = False
        self.address = ""

    def addNode(self, id, lat, lon):
        self.id = id
        self.lat = lat
        self.lon = lon

    def addPost(self, address):
        self.post = True
        self.address = address;

    def getId(self):
        return self.id
