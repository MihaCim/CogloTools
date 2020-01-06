#!/usr/bin/python3

import sys
import math
import json
print(sys.path)
from modules.create_graph.data_parser.data_handler import DataHandler
from modules.create_graph.neighbours_finder import NeighboursFinder
import networkx as nx
import matplotlib.pyplot as plt


def drawGraph(H, postalNodes, postalWays):
    G = nx.Graph()
    D = nx.Graph()
    li = []
    labels = {}

    for posts in postalNodes:
        li.append(posts)
        G.add_node(posts, pos=(postalNodes[posts]["lat"], postalNodes[posts]["lon"]))
        labels[posts] = postalNodes[posts]["post_id"]

    tmpDifColoring = []
    for posts in postalNodes:
        tmpDifColoring.append(posts)
        D.add_node(posts, pos=(postalNodes[posts]['post'].latitude, postalNodes[posts]['post'].longitude))

    for src, dest, weight in postalWays:
        G.add_edge(src, dest, weight=weight)


        # plt.figure(1)

    #pos = nx.spring_layout(G, k=0.25, iterations=40)
    pos = nx.get_node_attributes(H, 'pos', )
    nx.draw(H, pos=pos, node_size=0.1, node_color='g', edge_color='g',)
    nx.draw_networkx_nodes(D, pos, nodelist=li, node_color='b')
    nx.draw_networkx_nodes(G, pos, nodelist=tmpDifColoring, node_color='g')
    col = nx.draw_networkx_edges(G, pos, nodelist=li, node_color='g',edge_color='r')
    col.set_zorder(20)
    nx.draw_networkx_labels(G, pos, labels, font_size=16)

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
            G.add_edge(key, kc, weight=vc['weight'])

    import matplotlib.pyplot as plt

    # plt.figure(1)
    pos = nx.spring_layout(G, k=0.1, iterations=80)
    nx.draw_networkx_nodes(G, pos, node_color=color_map, nodelist=li)
    nx.draw_networkx_edges(G, pos, nodelist=li, node_color='g')

    nx.draw_networkx_labels(G, pos, labels, font_size=16)

    plt.show()


import modules.create_graph.pojo.search_node as search_node
def syntetic_graph1_construction():
        nodes = {}
        nodes[0] = search_node.SearchNode(0, 'A0', True)
        nodes[1] = search_node.SearchNode(1, None, False)
        nodes[2] = search_node.SearchNode(2, None, False)
        nodes[3] = search_node.SearchNode(3, None, False)
        nodes[4] = search_node.SearchNode(4, None, False)
        nodes[5] = search_node.SearchNode(5, None, False)
        nodes[6] = search_node.SearchNode(6, 'A1', True)
        nodes[7] = search_node.SearchNode(7, 'A2', True)
        nodes[8] = search_node.SearchNode(8, None, False)
        nodes[9] = search_node.SearchNode(9, None, False)
        nodes[10] = search_node.SearchNode(10, None, False)
        nodes[11] = search_node.SearchNode(11, None, False)
        nodes[12] = search_node.SearchNode(12, 'A3', True)
        nodes[13] = search_node.SearchNode(13, None, False)
        nodes[14] = search_node.SearchNode(14, 'A4', True)
        nodes[15] = search_node.SearchNode(15, None, False)
        nodes[16] = search_node.SearchNode(16, None, False)
        nodes[17] = search_node.SearchNode(17, None, False)
        nodes[18] = search_node.SearchNode(18, None, False)
        nodes[19] = search_node.SearchNode(19, None, False)
        nodes[20] = search_node.SearchNode(20, None, False)
        nodes[21] = search_node.SearchNode(21, None, False)
        nodes[22] = search_node.SearchNode(22, None, False)
        nodes[23] = search_node.SearchNode(23, 'A5', True)
        nodes[24] = search_node.SearchNode(24, None, False)
        nodes[25] = search_node.SearchNode(25, None, False)
        nodes[26] = search_node.SearchNode(26, None, False)
        nodes[27] = search_node.SearchNode(27, None, False)
        nodes[28] = search_node.SearchNode(28, None, False)
        nodes[29] = search_node.SearchNode(29, None, False)
        nodes[30] = search_node.SearchNode(30, None, False)

        edges = {0: {1: {"weight": 0.5}, 2: {"weight": 0.2}, 20: {"weight": 0.3}, 21: {"weight": 0.6}},
                 1: {7: {"weight": 0.5}, 0: {"weight": 0.5}},
                 2: {0: {"weight": 0.5}, 3: {"weight": 0.5}, 6: {"weight": 0.5}},
                 3: {2: {"weight": 0.5}, 4: {"weight": 0.5}, 5: {"weight": 0.5}},
                 4: {3: {"weight": 0.5}},
                 5: {3: {"weight": 0.5}},
                 6: {2: {"weight": 0.5}, 7: {"weight": 0.5}, 16: {"weight": 0.5}},
                 7: {8: {"weight": 0.5}, 11: {"weight": 0.5}, 15: {"weight": 0.5}, 6: {"weight": 0.5},
                     1: {"weight": 0.5}},
                 8: {9: {"weight": 0.5}, 10: {"weight": 0.5}, 7: {"weight": 0.5}},
                 9: {8: {"weight": 0.5}},
                 10: {11: {"weight": 0.5}, 8: {"weight": 0.5}},
                 11: {10: {"weight": 0.5}, 7: {"weight": 0.5}},
                 12: {15: {"weight": 0.5}},
                 13: {15: {"weight": 0.5}},
                 14: {16: {"weight": 0.5}},
                 15: {13: {"weight": 0.5}, 12: {"weight": 0.5}, 7: {"weight": 0.5}, 16: {"weight": 0.5}},
                 16: {14: {"weight": 0.5}, 15: {"weight": 0.5}, 6: {"weight": 0.5}},
                 17: {19: {"weight": 0.5}},
                 18: {19: {"weight": 0.5}},
                 19: {17: {"weight": 0.5}, 18: {"weight": 0.5}, 20: {"weight": 0.5}},
                 20: {19: {"weight": 0.5}, 0: {"weight": 0.5}, 23: {"weight": 0.5}},
                 21: {0: {"weight": 0.5}, 24: {"weight": 0.5}, 25: {"weight": 0.5}},
                 22: {23: {"weight": 0.5}},
                 23: {20: {"weight": 0.5}, 22: {"weight": 0.5}, 26: {"weight": 0.5}},
                 24: {21: {"weight": 0.5}, 27: {"weight": 0.5}, 28: {"weight": 0.5}, 29: {"weight": 0.5}},
                 25: {21: {"weight": 0.5}, 30: {"weight": 0.5}, 29: {"weight": 0.5}},
                 26: {23: {"weight": 0.5}},
                 27: {24: {"weight": 0.5}},
                 28: {24: {"weight": 0.5}},
                 29: {24: {"weight": 0.5}, 25: {"weight": 0.5}},
                 30: {25: {"weight": 0.5}}}

        return nodes, edges

def run():

    osmHandler = DataHandler("modules/create_graph/data/zagreb.osm",
                             {'si':'modules/create_graph/data/List of Postal Offices (geographical location).csv',
                              'hr':'modules/create_graph/data/PU_Geokoordinate.csv'
                               })
    G = osmHandler.graph_viz()
    roadNodes = osmHandler.modified_nodes
    roadWays = osmHandler.modified_ways
    map_posts_to_nodes = {}
    for k, v in roadNodes.items():
        if v.is_post:
            map_posts_to_nodes[v.post_id] = k
            print("Post_id: " + str(v.post_id) + " node_id" + str(k))

    postNode = {}
    postNodePlain = {}
    postEdge = set()
    tmpRes = []

    finder = NeighboursFinder(G)


    for postId, nodeId in map_posts_to_nodes.items():
        #postId = 'A8'
        #nodeId = 50
        res = finder.search_near_posts(roadNodes, roadWays, nodeId, 3)
        print('PostID ' + str(postId) + ' Node: ' + str(nodeId) + ' r: ' + str(res))

        tmpRes.append((postId, nodeId, res))
        for res_id, res_dist in res:
                dist = math.floor(res_dist*1000)
                postEdge.add((nodeId, map_posts_to_nodes[res_id], dist))
                postEdge.add((map_posts_to_nodes[res_id], nodeId, dist))
                print(res_id)


        for k, v in roadNodes.items():
            if v.post_id != None:
                d = {'address': v.address,
                     'lat': v.lat,
                     'lon': v.lon,
                     'node_id': v.node_id,
                     'post_id': v.post_id
                     }
                postNode[k] = v.__dict__
                postNodePlain[k] = d

        if len(postEdge) != 0:
            drawGraph(G, postNode, postEdge)

    print('nodes'+str(len(postNode)))
    print('edge'+str(len(postEdge)))
    graph = {'nodes': postNodePlain, 'edge': list(postEdge)}
    f = open("zagreb.json", "w")
    f.write(json.dumps(graph))
    f.close()

    '''
    nodes_dict, edges_dict = syntetic_graph1_construction()
    import modules.create_graph.neighbours_finder as neighbour_alg
    finder = neighbour_alg.NeighboursFinder()
    result = finder.search_near_posts(nodes_dict, edges_dict, 0, 1)
    print(result)
    '''

if __name__ == "__main__":
    run()

