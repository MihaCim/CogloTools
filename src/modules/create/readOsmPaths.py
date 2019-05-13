#!/usr/bin/python3

import xml.sax
import networkx as nx
import matplotlib.pyplot as plt
import csv
from math import radians, cos, sin, asin, sqrt

nodes = {}
ways = []


class OsmHandler(xml.sax.ContentHandler):

    def startElement(self, name, attrs):
        if name == "node":
            node = Node()
            if "id" in attrs and "lat" in attrs and "lon" in attrs:
                node.addNode(attrs["id"], float(attrs["lat"]), float(attrs["lon"]))
                nodes[attrs["id"]] = node
        if name == "way":
            self.way = Way()
            for key in dict(attrs):
                print(key + ", " + attrs[key])
        if name == "nd":
            self.way.addNode(attrs["ref"])

    def endElement(self, name):
        if name == "way":
            ways.append(self.way)


    #def characters(self, data):
    #  print("Characters: %s" % data)

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
        self.ids = []

    def addNode(self, id):
        self.ids.append(id)

    def getNodes(self):
        return (self.ids[0], self.ids[len(self.ids)-1])

    def getAllNodes(self):
        return self.ids

class Post:
    def __init__(self, address, latitude, longitude):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude

def drawGraph():
    G = nx.Graph()
    color_map = []

    for edge in ways:
        l= edge.getAllNodes()
        if(len(l) > 1):
            G.add_node(l[0])
            for i in range(1, len(l)-1):
                G.add_edge(l[i-1], l[i], weight=1)
                G.add_node(l[i])

    # use one of the edge properties to control line thickness
    edgewidth = [d['weight'] for (u, v, d) in G.edges(data=True)]

    # rendering
    plt.figure(1)
    plt.axis('off')
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos,
                           node_color=color_map,
                           alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edgewidth, )
    plt.show()

def isNumber(str):
    try:
        return float(str)
    except ValueError:
        return None


def calcDistance(lat1, lon1, lat2, lon2):

    # Code coppied form: http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km


def readPostalOffices():
    posts = []
    with open('data/List of Postal Offices (geographical location).csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            address = [row[13], row[14], row[15]]
            if (isNumber(row[22]) != None and isNumber(row[23]) != None):
                post = Post(' '.join(address), isNumber(row[22]), isNumber(row[23]))
                posts.append(post)

    return posts

def alignNodesAndPosts(posts, nodes):
    import sys
    minDist = sys.maxsize
    nodeKey = ""
    for post in posts:
        for key, node in nodes.items():
            tmpDist = calcDistance(post.latitude, post.longitude, node.lat, node.lon)
            if minDist > tmpDist:
                minDist = tmpDist
                nodeKey = key

        tmpNode = nodes[nodeKey]
        tmpNode.addPost(post.address)
        nodes[nodeKey] = tmpNode
    return nodes

if (__name__ == "__main__"):
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = OsmHandler()
    parser.setContentHandler(Handler)

    parser.parse("stahovica.osm")

    print(len(nodes))
    print(len(ways))
    posts = readPostalOffices()
    nodes = alignNodesAndPosts(posts, nodes)
    print(nodes)
    #drawGraph()


    



