#!/usr/bin/python3
import sys
import csv
import math
from src.modules.create.utils import utils
from src.modules.create import parseOsm
import networkx as nx

class Post:
    def __init__(self, address, latitude, longitude):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude

class PostHandler:

    def __init__(self):
        self.posts = []

    def isNumber(self, str):
        try:
            return float(str)
        except ValueError:
            return None

    def readPostalOffices(self):
        ''' Postal offices are read from csv file and than added to array
        '''
        self.posts = []
        with open('data/List of Postal Offices (geographical location).csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            for row in csv_reader:
                address = [row[13], row[14], row[15]]
                if (self.isNumber(row[22]) != None and self.isNumber(row[23]) != None):
                    post = Post(' '.join(address), self.isNumber(row[22]), self.isNumber(row[23]))
                    self.posts.append(post)

        return self.posts


    def alignNodesAndPosts(self, nodesL):
        '''
        Align post offices with nodes

        :param posts:
        :param nodesL:
        :return:
        '''
        posts = self.readPostalOffices()
        postsNodes = []
        for post in posts:
            minDist = sys.maxsize
            nodeKey = ""
            for key, node in nodesL.items():
                tmpDist = utils.calcDistance(post.latitude, post.longitude, node.lat, node.lon)
                if minDist > tmpDist:
                    minDist = tmpDist
                    nodeKey = key

            tmpNode = nodesL[nodeKey]
            if utils.calcDistance(post.latitude, post.longitude, tmpNode.lat, tmpNode.lon) < 1:
                print(nodeKey)
                print(post.address)
                print(utils.calcDistance(post.latitude, post.longitude, tmpNode.lat, tmpNode.lon))
                postsNodes.append(nodeKey)
                tmpNode.addPost(post.address)
                nodesL[nodeKey] = tmpNode
        return (nodesL, postsNodes)



def drawGraph(algPostalWays, H, nodes):
    G = nx.Graph()
    n = set()

    li = []
    for edge in algPostalWays:
        l= edge.getAllNodes()
        if l[0] not in n:
            G.add_node(l[0], pos=(nodes[l[0]].lat, nodes[l[0]].lon))
        if l[1] not in n:
            G.add_node(l[1], pos=(nodes[l[1]].lat, nodes[l[1]].lon))
        G.add_edge(l[0], l[1], weight=edge.distance)
        n.add(l[0])
        n.add(l[1])
        li.append(l[0])
        li.append(l[1])

        import matplotlib.pyplot as plt


        #plt.figure(1)
        pos = nx.get_node_attributes(H, 'pos')
        nx.draw(H, pos=pos, node_size=1)
        nx.draw_networkx_nodes(G, pos, nodelist=l, node_color='g')
        nx.draw_networkx_edges(G, pos, nodelist=l, node_color='g')

        #plt.figure(2)
        #nx.draw(G)
        plt.show()


'''
    for edge in waysL:
        l= edge.getAllNodes()
        if l[0] not in n:
            G.add_node(l[0], pos=(nodes[l[0]].lat, nodes[l[0]].lon))
        if l[1] not in n:
            G.add_node(l[1], pos=(nodes[l[1]].lat, nodes[l[1]].lon))
        G.add_edge(l[0], l[1], weight=edge.distance)
        n.add(l[0])
        n.add(l[1])


    # rendering
    plt.figure(figsize=(8,8))
    plt.axis('off')
    pos = nx.get_node_attributes(G, 'pos')

    #  plt.figure(2)
    # nx.draw(H)

    print(pos)
    nx.draw(G, pos =pos, node_size = 1)
    plt.savefig("Graph.png", format="PNG")
    plt.show()
'''


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

        if current_element in nodes and nodes[current_element].get("post"):
            current_visited_points.append(current_element)
            print(current_visited_points)
            if len(current_visited_points) == 1:
                results.append(current_element)
        fronta.append((current_element, current_sdistance, current_visited_points))
        print(fronta)

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
        import time
        #time.sleep(2)
    print("aa")
    print(results)
    return results


if (__name__ == "__main__"):

    osmHandler = parseOsm.OsmHandler()
    G = osmHandler.graphViz()

    roadNodes = osmHandler.nodes
    roadWays = osmHandler.ways
    postHandler = PostHandler()

    nodesFiltered = {}
    for way in roadWays:
        for id in way.ids:
            nodesFiltered[id] = roadNodes[id]
    (roadNodesAnotated, postsNodes) = postHandler.alignNodesAndPosts(nodesFiltered)


    nodesDict = {}
    edgesDict = {}

    for key, node in roadNodesAnotated.items():
        nodesDict[node.id] = {"post":node.post}

    for key, node in roadNodesAnotated.items():
        edgesDict[node.id] = {}

    for way in roadWays:
        tmpD = edgesDict[way.ids[0]]
        tmpD[way.ids[1]] = {"weight": way.distance}
        edgesDict[way.ids[0]] = tmpD

    print(len(roadNodes))
    print(len(edgesDict))

    #for n in nodesNode:


    algPostalWays = []
    for posts in postsNodes:
        results = search_near_posts(nodesDict, edgesDict, posts)
        for result in results:
            tmp = parseOsm.Way()
            tmp.addPath(result, posts)
            tmp.addDistance(utils.calcDistance(roadNodes[result].lat, roadNodes[result].lon, roadNodes[posts].lat, roadNodes[posts].lon))
            algPostalWays.append(tmp)


    drawGraph(algPostalWays, G, roadNodesAnotated)


    



