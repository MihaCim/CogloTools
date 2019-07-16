#!/usr/bin/python3
import sys
import csv

from src.modules.create_graph.utils import utils
from src.modules.create_graph import parseOsm
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
        with open('config/List of Postal Offices (geographical location).csv') as csv_file:
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


def drawGraph(algPostalWays, H, nodes, postalNodes):
    G = nx.Graph()
    li = []

    for posts in postalNodes:
        li.append(posts)
        G.add_node(posts, pos=(nodes[posts].lat, nodes[posts].lon))

    for edge in algPostalWays:
        l = edge.getAllNodes()
        ##if l[0] not in n:
        #   G.add_node(l[0], pos=(nodes[l[0]].lat, nodes[l[0]].lon))
        # if l[1] not in n:
        #    G.add_node(l[1], pos=(nodes[l[1]].lat, nodes[l[1]].lon))
        G.add_edge(l[0], l[1], weight=edge.distance)

        import matplotlib.pyplot as plt

        # plt.figure(1)
        pos = nx.get_node_attributes(H, 'pos')
        nx.draw(H, pos=pos, node_size=1)
        nx.draw_networkx_nodes(G, pos, nodelist=li, node_color='g')
        nx.draw_networkx_edges(G, pos, nodelist=li, node_color='g')

        # plt.figure(2)
        # nx.draw(G)
        plt.show()


def drawStaticGraph(nodes, ways, results):
    G = nx.Graph()
    li = []

    #    edge
    labels = {}
    i = 0
    color_map = []
    for posts in nodes:
        if nodes[posts].post_id != None:
            if nodes[posts].post_id in results:
                color_map.append('red')
            else:
                color_map.append('blue')
            labels[i] = nodes[posts].post_id + "(" + str(posts) + ")"
        else:
            labels[i] = posts
            color_map.append('green')

        li.append(posts)
        G.add_node(posts)

        i = i + 1

    for key, value in ways.items():
        for kc, vc in value.items():
            print(value)
            print(vc)

            G.add_edge(key, kc, weight=vc['weight'])

    import matplotlib.pyplot as plt

    # plt.figure(1)
    pos = nx.spring_layout(G, k=0.25, iterations=40)
    nx.draw_networkx_nodes(G, pos, node_color=color_map, nodelist=li)
    nx.draw_networkx_edges(G, pos, nodelist=li, node_color='g')

    nx.draw_networkx_labels(G, pos, labels, font_size=16)

    plt.show()




if __name__ == "__main__":

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

    i = 1
    for key, node in roadNodesAnotated.items():
        if node.post:
            nodesDict[node.id] = SearchNode(node.id, i, node.post)
            i = i + 1
        else:
            nodesDict[node.id] = SearchNode(node.id)

    for key, node in roadNodesAnotated.items():
        edgesDict[node.id] = {}

    for way in roadWays:
        tmpD = edgesDict[way.ids[0]]
        tmpD[way.ids[1]] = {"weight": way.distance}
        edgesDict[way.ids[0]] = tmpD

    # nodesDict,edgesDict = synticGraph()
    # drawStaticGraph(nodesDict, edgesDict, results)

    for posts in postsNodes:
        results = search_near_posts(nodesDict, edgesDict, posts, 1)
        for result in results:
            tmp = parseOsm.Way()
            tmp.addPath(result, posts)
            tmp.addDistance(utils.calcDistance(roadNodes[result].lat, roadNodes[result].lon, roadNodes[posts].lat,
                                               roadNodes[posts].lon))
            # algPostalWays.append(tmp)

    # drawGraph(algPostalWays, G, roadNodesAnotated, postsNodes)
