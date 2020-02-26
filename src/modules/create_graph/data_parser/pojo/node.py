
class Node:

    def __init__(self):
        self.post = False
        self.address = ""

    def add_node(self, id, lat, lon):
        self.id = id
        self.lat = lat
        self.lon = lon

    def add_post(self, address, post):
        self.post = True
        self.address = address
        self.post = post

    def get_id(self):
        return self.id



