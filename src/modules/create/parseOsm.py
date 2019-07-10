import xml.sax
from src.modules.create.utils import utils
import networkx as nx

class OsmParsers(xml.sax.ContentHandler):
    '''
        OsmParsers parse OSM data to nodes and ways. Nodes are represents as dictionary in order to fast accesss to it.
        Ways are list.
    '''
    def __init__(self):
        self.nodes = {}  # nodes are save
        self.ways = []
        self.tmpWays = []
        self.tags = {}
        self.roads = {"motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "service",
                      "living_street", "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link",
                      "motorway_junction"}

    def startElement(self, name, attrs):
        if name == "node":
            node = Node()
            if "id" in attrs and "lat" in attrs and "lon" in attrs:
                node.addNode(int(attrs["id"]), float(attrs["lat"]), float(attrs["lon"]))
                self.nodes[int(attrs["id"])] = node
        if name == "way":
            self.tmpWays = []
            self.tags = {}
            # for key in dict(attrs):
            #    print(key + ", " + attrs[key])
        if name == "nd":
            self.tmpWays.append(attrs["ref"])
        if name == "tag":
            self.tags[attrs["k"]] = attrs["v"]


    def endElement(self, name):
        if name == "way":
            if "highway" in self.tags and self.tags["highway"] in self.roads:
                for i in range(1, len(self.tmpWays)):
                    distance = 0
                    way = Way()
                    node1 = self.nodes[int(self.tmpWays[i - 1])]
                    node2 = self.nodes[int(self.tmpWays[i])]
                    way.addPath(int(self.tmpWays[i - 1]), int(self.tmpWays[i]))
                    distance = utils.calcDistance(node1.lat, node1.lon, node2.lat, node2.lon)
                    way.addDistance(distance)
                    self.ways.append(way)
                self.tags = {}
                self.tmpWays = {}
class OsmHandler(xml.sax.ContentHandler):


    def __init__(self):
        # create an XMLReader

        parser = xml.sax.make_parser()
        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # override the default ContextHandler
        handler = OsmParsers()
        parser.setContentHandler(handler)

        parser.parse("data/test_export.osm")

        self.ways = handler.ways
        self.nodes = handler.nodes

    def graphViz(self):
        G = nx.Graph()
        n = set()

        for edge in self.ways:
            l = edge.getAllNodes()
            if l[0] not in n:
                G.add_node(l[0], pos=(self.nodes[l[0]].lat, self.nodes[l[0]].lon))
            if l[1] not in n:
                G.add_node(l[1], pos=(self.nodes[l[1]].lat, self.nodes[l[1]].lon))
            G.add_edge(l[0], l[1], weight=edge.distance)
            n.add(l[0])
            n.add(l[1])
        return G


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
