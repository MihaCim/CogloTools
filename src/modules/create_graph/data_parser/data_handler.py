import sys

import xml.sax
import networkx as nx
from modules.create_graph.utils import utils
from modules.create_graph.data_parser.parse_osm import OsmParsers
from modules.create_graph.data_parser.parse_posts import PostHandler
from modules.create_graph.pojo.search_node import SearchNode

class DataHandler():

    def align_nodes_and_posts(self, nodesL):
        '''
        Align post offices with nodes

        :param posts:
        :param nodesL:
        :return:
        '''

        postsNodes = []
        for post in self.posts:
            minDist = sys.maxsize
            nodeKey = ""
            for key, node in nodesL.items():
                tmpDist = utils.calcDistance(post.latitude, post.longitude, node.lat, node.lon)
                if minDist > tmpDist:
                    minDist = tmpDist
                    nodeKey = key

            tmpNode = nodesL[nodeKey]
            if utils.calcDistance(post.latitude, post.longitude, tmpNode.lat, tmpNode.lon) < 0.1:
                print(nodeKey)
                print(post.address)
                print(utils.calcDistance(post.latitude, post.longitude, tmpNode.lat, tmpNode.lon))
                postsNodes.append(nodeKey)
                tmpNode.add_post(post.address)
                nodesL[nodeKey] = tmpNode
        return (nodesL, postsNodes)




    def retrive_posts(self, post_path):
        post_handler = PostHandler()
        self.posts = post_handler.read_postal_offices(post_path)



    def retrieve_road_topology(self, osm_path, post_path):

        self.retrive_posts(post_path)

        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # parse osm files
        handler = OsmParsers()
        parser.setContentHandler(handler)
        parser.parse(osm_path)

        self.ways = handler.ways
        self.nodes = handler.nodes

        ###
        print(self.nodes)
        transformed_ids = {}
        cnt = 0
        self.new_nodes = {}
        for node_id, node_value in self.nodes.items():
            transformed_ids[node_id] = cnt
            node_value.id = cnt
            self.new_nodes[cnt] = node_value
            cnt += 1

        for way in self.ways:
            nodes = way.get_all_nodes()
            way.add_path(transformed_ids[nodes[0]], transformed_ids[nodes[1]])
        ###
        self.nodes = self.new_nodes

        print(self.ways)
        nodes_filtered = {}

        #in this step we remove nodes which are not connected to road
        #with this step we want to avoid that algoritm will hang on.
        for way in self.ways:
            for id in way.ids:
                nodes_filtered[id] = self.nodes[id]

        nodesDict = {}
        edgesDict = {}

        #alignement
        (roadNodesAnotated, postsNodes) =  self.align_nodes_and_posts(nodes_filtered)

        #generate ides for post offices (generic)
        i = 1
        for key, node in roadNodesAnotated.items():
            if node.post:
                nodesDict[node.id] = SearchNode(node.id, 'A' + str(i), node.post, node.lat, node.lon, node.address,)
                i = i + 1
            else:
                nodesDict[node.id] = SearchNode(node.id, None, None, node.lat, node.lon, node.address)


        for key, node in roadNodesAnotated.items():
            edgesDict[node.id] = {}

        for way in self.ways:
            #Firstly add edge from A to B
            tmpD = edgesDict[way.ids[0]]
            tmpD[way.ids[1]] = {"weight": way.distance}
            edgesDict[way.ids[0]] = tmpD

            #Than add edge from B to A
            tmpD = edgesDict[way.ids[1]]
            tmpD[way.ids[0]] = {"weight": way.distance}
            edgesDict[way.ids[1]] = tmpD

        self.modified_ways = edgesDict
        self.modified_nodes = nodesDict


    def __init__(self, osm_path, posts_path):
        # create_graph an XMLReader
        self.retrieve_road_topology(osm_path, posts_path)


    def graph_viz(self):
        G = nx.Graph()
        n = set()

        for edge in self.ways:
            l = edge.get_all_nodes()
            if l[0] not in n:
                G.add_node(l[0], pos=(self.nodes[l[0]].lat, self.nodes[l[0]].lon))
            if l[1] not in n:
                G.add_node(l[1], pos=(self.nodes[l[1]].lat, self.nodes[l[1]].lon))
            G.add_edge(l[0], l[1], weight=edge.distance)
            n.add(l[0])
            n.add(l[1])
        return G



