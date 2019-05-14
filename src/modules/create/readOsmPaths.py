#!/usr/bin/python3
import sys
import xml.sax
import networkx as nx
import matplotlib.pyplot as plt
import csv
from math import radians, cos, sin, asin, sqrt, atan2
import math

nodes = {}
ways = []


class OsmHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.tmpWays = []
    def startElement(self, name, attrs):
        if name == "node":
            node = Node()
            if "id" in attrs and "lat" in attrs and "lon" in attrs:
                node.addNode(attrs["id"], float(attrs["lat"]), float(attrs["lon"]))
                nodes[attrs["id"]] = node
        if name == "way":
            self.tmpWays = []
            for key in dict(attrs):
                print(key + ", " + attrs[key])
        if name == "nd":
            self.tmpWays.append(attrs["ref"])


    def endElement(self, name):
        if name == "way":
            for i in range(1, len(self.tmpWays)):
                way = Way()
                way.addNode(self.tmpWays[i - 1])
                way.addNode(self.tmpWays[i])
                node1 = nodes[self.tmpWays[i - 1]]
                node2 = nodes[self.tmpWays[i]]
                distance = calcDistance(node1.lat, node1.lon, node2.lat, node2.lon)
                way.addDistance(distance)
                ways.append(way)


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

    def addDistance(self, distance):
        self.distance = distance


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
    R = 6373.0
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


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

    for post in posts:
        minDist = sys.maxsize
        nodeKey = ""
        for key, node in nodes.items():
            tmpDist = calcDistance(post.latitude, post.longitude, node.lat, node.lon)
            if minDist > tmpDist:
                minDist = tmpDist
                nodeKey = key

        tmpNode = nodes[nodeKey]
        if calcDistance(post.latitude, post.longitude, tmpNode.lat, tmpNode.lon) < 0.5:
            print(nodeKey)
            print(post.address)
            tmpNode.addPost(post.address)
            nodes[nodeKey] = tmpNode
    return nodes

def search_near_posts(nodes, edges, start_nodes):
    fronta = [(start_nodes, 0, [])]
    visited_nodes = set()
    results = []

    while len(fronta) != 0:
        current_element = 0
        current_sdistance = math.inf
        current_visited_points = []
        previous_element = 0
        for (index, distance, visited_node) in fronta:
            Neigbours = edges[index]  # get neighbors od te tocke
            for neigbour in Neigbours:
                if ((distance + Neigbours[neigbour]["weight"]) < current_sdistance) and (neigbour not in visited_nodes):
                    current_sdistance = distance + Neigbours[neigbour]["weight"]
                    current_element = neigbour
                    current_visited_points = list(visited_node)
                    previous_element = index
        print(current_element)
        print(current_sdistance)
        print(current_visited_points)
        print(previous_element)
        if nodes[current_element].get("post"):
            current_visited_points.append(current_element)
            print(current_visited_points)
            if len(current_visited_points) == 1:
                results.append(current_element)
        fronta.append((current_element, current_sdistance, current_visited_points))
        print(fronta)
        st = 0
        visited_nodes.add(current_element)
        visited_nodes.add(start_nodes)
        # deleting procedure id should be much more simple

        d = []
        i = 0
        for (index, distance, vn) in fronta:
            st = 0
            for n in edges[index]:
                for visited_node in visited_nodes:
                    if n == visited_node:
                        st = st + 1
                        ##break;
            if st == len(edges[index]):
                d.append(i)
            i = i + 1

        for index in sorted(d, reverse=True):
            del fronta[index]
            print("remove: "+str(index))


        print("visited:"+str(visited_nodes))
        print("results:"+str(results))
        #import time
        #time.sleep(2)
    print("aa")
    print(results)



def writeDict(dict):
    import json
    json = json.dumps(dict)
    f = open("dict.json", "w")
    f.write(json)
    f.close()
def readDict(dict):
    import json
    f = open("dict.txt", "w")
    f.write(str(dict))
    f.close()


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
    nodesC = alignNodesAndPosts(posts, nodes)

    nodesDict = {}
    for key, node in nodes.items():
        nodesDict[node.id] = {"post":node.post}

    edgesDict = {}
    for key, node in nodes.items():
        edgesDict[node.id] = {}
    for way in ways:

        tmpD = edgesDict[way.ids[0]]
        tmpD[way.ids[1]] = {"weight": way.distance}
        edgesDict[way.ids[0]] = tmpD
    search_near_posts(nodesDict, edgesDict, "4862147915")
    print(nodesDict)
    print(edgesDict)
    #6326558776
    #Vir Gubčeva ulica 12



    #drawGraph()


    



