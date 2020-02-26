
class Way:

    def __init__(self):
        self.ids = ()

    def add_path(self, id1, id2):
        self.ids = (id1, id2)

    def get_nodes(self):
        return (self.ids[0], self.ids[len(self.ids) - 1])

    def get_all_nodes(self):
        return self.ids

    def add_distance(self, distance):
        self.distance = distance
