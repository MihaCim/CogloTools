
class Way:

    def __init__(self):
        self.ids = ()

    def addPath(self, id1, id2):
        self.ids = (id1, id2)

    def getNodes(self):
        return (self.ids[0], self.ids[len(self.ids) - 1])

    def getAllNodes(self):
        return self.ids

    def addDistance(self, distance):
        self.distance = distance
