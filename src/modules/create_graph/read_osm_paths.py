#!/usr/bin/python3
import os
import sys
import math
import json
print(sys.path)
from data_parser.data_handler import DataHandler
from neighbours_finder import NeighboursFinder
import networkx as nx
import matplotlib.pyplot as plt
import pojo.search_node as search_node


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


def run():

    osmHandler = DataHandler("./data/slovenia-latest.osm",
                             {'si':'./data/List of Postal Offices (geographical location).csv',
                              'hr':'./data/PU_Geokoordinate.csv'
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
    f = open("atene.json", "w")
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

