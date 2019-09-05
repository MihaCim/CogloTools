#!/usr/bin/python3

import sys
print(sys.path)
from modules.create_graph.data_parser.data_handler import DataHandler
from modules.create_graph.neighbours_finder import NeighboursFinder
import networkx as nx
import matplotlib.pyplot as plt


def drawGraph(H, postalNodes, postalWays):
    G = nx.Graph()
    li = []
    labels = {}

    for posts in postalNodes:
        li.append(posts)
        G.add_node(posts, pos=(postalNodes[posts]["lat"], postalNodes[posts]["lon"]))
        labels[posts] = postalNodes[posts]["post_id"]


    for edge in postalWays:
        for edgeN in postalWays[edge]:
            G.add_edge(edge, edgeN, weight=postalWays[edge][edgeN]['weight'])


        # plt.figure(1)

    #pos = nx.spring_layout(G, k=0.25, iterations=40)
    pos = nx.get_node_attributes(H, 'pos', )
    nx.draw(H, pos=pos, node_size=0.1, node_color='g', edge_color='g',)
    nx.draw_networkx_nodes(G, pos, nodelist=li, node_color='g')
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

def syntic_graph2_constraction():
        import src.modules.create_graph.pojo.search_node as search_node
        nodes_dict = {}
        nodes_dict[0] = search_node.SearchNode(0, "A0", True)
        nodes_dict[1] = search_node.SearchNode(1, None, False)
        nodes_dict[2] = search_node.SearchNode(2, None, False)
        nodes_dict[3] = search_node.SearchNode(3, None, False)
        nodes_dict[4] = search_node.SearchNode(4, None, False)
        nodes_dict[5] = search_node.SearchNode(5, None, False)
        nodes_dict[6] = search_node.SearchNode(6, None, False)
        nodes_dict[7] = search_node.SearchNode(7, "A1", True)
        nodes_dict[8] = search_node.SearchNode(8, None, False)
        nodes_dict[9] = search_node.SearchNode(9, None, False)
        nodes_dict[10] = search_node.SearchNode(10, None, False)
        nodes_dict[11] = search_node.SearchNode(11, "A2", True)
        nodes_dict[12] = search_node.SearchNode(12, "A3", True)
        nodes_dict[13] = search_node.SearchNode(13, "A4", True)
        nodes_dict[14] = search_node.SearchNode(14, None, False)
        nodes_dict[15] = search_node.SearchNode(15, None, False)
        nodes_dict[16] = search_node.SearchNode(16, None, False)
        nodes_dict[17] = search_node.SearchNode(17, None, False)
        nodes_dict[18] = search_node.SearchNode(18, None, False)
        nodes_dict[19] = search_node.SearchNode(19, "A5", True)
        nodes_dict[20] = search_node.SearchNode(20, None, False)
        nodes_dict[21] = search_node.SearchNode(21, None, False)
        nodes_dict[22] = search_node.SearchNode(22, None, False)
        nodes_dict[24] = search_node.SearchNode(24, None, False)
        nodes_dict[23] = search_node.SearchNode(23, None, False)
        nodes_dict[25] = search_node.SearchNode(25, "A6", True)
        nodes_dict[26] = search_node.SearchNode(26, None, False)
        nodes_dict[27] = search_node.SearchNode(27, "A7", True)
        nodes_dict[28] = search_node.SearchNode(28, None, False)
        nodes_dict[29] = search_node.SearchNode(29, None, False)
        nodes_dict[30] = search_node.SearchNode(30, None, False)
        nodes_dict[31] = search_node.SearchNode(31, None, False)
        nodes_dict[32] = search_node.SearchNode(32, None, False)
        nodes_dict[33] = search_node.SearchNode(33, None, False)
        nodes_dict[34] = search_node.SearchNode(34, "A8", True)
        nodes_dict[35] = search_node.SearchNode(35, None, False)
        nodes_dict[36] = search_node.SearchNode(36, None, False)
        nodes_dict[37] = search_node.SearchNode(37, None, False)
        nodes_dict[38] = search_node.SearchNode(38, None, False)
        nodes_dict[39] = search_node.SearchNode(39, None, False)
        nodes_dict[40] = search_node.SearchNode(40, "A9", True)
        nodes_dict[41] = search_node.SearchNode(41, "A10", True)
        nodes_dict[42] = search_node.SearchNode(42, None, False)
        nodes_dict[43] = search_node.SearchNode(43, None, False)
        nodes_dict[44] = search_node.SearchNode(44, None, False)
        nodes_dict[45] = search_node.SearchNode(45, None, False)
        nodes_dict[46] = search_node.SearchNode(46, None, False)
        nodes_dict[47] = search_node.SearchNode(47, None, False)
        nodes_dict[48] = search_node.SearchNode(48, None, False)
        nodes_dict[49] = search_node.SearchNode(49, None, False)
        nodes_dict[50] = search_node.SearchNode(50, None, False)
        nodes_dict[51] = search_node.SearchNode(51, "A11", True)
        nodes_dict[52] = search_node.SearchNode(52, None, False)
        nodes_dict[53] = search_node.SearchNode(53, None, False)
        nodes_dict[54] = search_node.SearchNode(54, None, False)
        nodes_dict[55] = search_node.SearchNode(55, None, False)
        nodes_dict[56] = search_node.SearchNode(56, None, False)
        nodes_dict[57] = search_node.SearchNode(57, "A12", True)

        edges_dict = {
            0: {1: {'weight': 2}, 2: {'weight': 2}, 3: {'weight': 2}, 4: {'weight': 2}, 47: {'weight': 3.5}},
            1: {5: {'weight': 0.5}, 6: {'weight': 2}, 0: {'weight': 2}},
            2: {0: {'weight': 2}, 9: {'weight': 2}, 10: {'weight': 6}},
            3: {0: {'weight': 2}, 19: {'weight': 2}, 20: {'weight': 2}},
            4: {0: {'weight': 2}, 30: {'weight': 0.5}},
            5: {1: {'weight': 0.5}},
            6: {1: {'weight': 2}, 7: {'weight': 2}, 8: {'weight': 1.5}},
            7: {6: {'weight': 2}},
            8: {6: {'weight': 1.5}, 42: {'weight': 2}},
            9: {41: {'weight': 0.5}, 12: {'weight': 2}, 2: {'weight': 2}, 13: {'weight': 0.7}},
            10: {2: {'weight': 6}, 11: {'weight': 2}},
            11: {10: {'weight': 2}, 45: {'weight': 2}},
            12: {9: {'weight': 1.5}},
            13: {9: {'weight': 0.7}, 14: {'weight': 0.5}, 15: {'weight': 0.5}},
            14: {13: {'weight': 0.5}},
            15: {13: {'weight': 0.5}},
            16: {41: {'weight': 0.5}, 17: {'weight': 0.5}},
            17: {16: {'weight': 0.5}, 18: {'weight': 0.5}, 44: {'weight': 0.5}},
            18: {17: {'weight': 0.5}},
            19: {3: {'weight': 2}, 45: {'weight': 0.5}},
            20: {3: {'weight': 2}, 21: {'weight': 0.3}, 27: {'weight': 0.3}},
            21: {20: {'weight': 0.5}, 25: {'weight': 0.3}, 22: {'weight': 0.3}},
            22: {21: {'weight': 0.5}, 24: {'weight': 0.3}, 23: {'weight': 0.3}},
            23: {22: {'weight': 0.5}},
            24: {22: {'weight': 0.5}},
            25: {21: {'weight': 0.5}, 26: {'weight': 0.3}},
            26: {25: {'weight': 0.5}},
            27: {20: {'weight': 0.5}, 28: {'weight': 0.3}, 29: {'weight': 0.3}},
            28: {27: {'weight': 0.65}},
            29: {27: {'weight': 0.65}},
            30: {4: {'weight': 0.5}, 31: {'weight': 0.3}, 32: {'weight': 0.3}, 37: {'weight': 0.3}},
            31: {30: {'weight': 0.5}},
            32: {30: {'weight': 0.3}, 33: {'weight': 0.3}, 34: {'weight': 0.3}},
            33: {32: {'weight': 0.4}},
            34: {35: {'weight': 0.5}, 32: {'weight': 0.3}},
            35: {34: {'weight': 0.5}, 36: {'weight': 0.3}},
            36: {35: {'weight': 0.5}},

            37: {30: {'weight': 0.5}, 38: {'weight': 0.3}},
            38: {37: {'weight': 0.5}, 39: {'weight': 0.3}},
            39: {38: {'weight': 0.5}, 40: {'weight': 3}},
            40: {39: {'weight': 5}},
            41: {9: {'weight': 0.5}, 16: {'weight': 0.5}, 42: {'weight': 0.5}},
            42: {8: {'weight': 0.5}, 41: {'weight': 0.5}, 43: {'weight': 0.5}},
            43: {42: {'weight': 0.5}},
            44: {17: {'weight': 0.5}},
            45: {11: {'weight': 0.5}, 19: {'weight': 0.5}, 46: {'weight': 0.15}},
            46: {45: {'weight': 0.5}},
            47: {0: {'weight': 3.5}, 48: {'weight': 0.45}, 55: {'weight': 0.45}},
            48: {47: {'weight': 0.45}, 49: {'weight': 0.45}},
            49: {48: {'weight': 0.45}, 51: {'weight': 0.45}, 50: {'weight': 0.45}},
            50: {49: {'weight': 0.45}},
            51: {49: {'weight': 0.45}, 52: {'weight': 0.45}},
            52: {51: {'weight': 0.45}, 53: {'weight': 0.45}, 56: {'weight': 0.45}},
            53: {52: {'weight': 0.45}, 54: {'weight': 0.45}},
            54: {53: {'weight': 0.45}, 55: {'weight': 0.45}},
            55: {54: {'weight': 0.45}, 47: {'weight': 0.45}},
            56: {52: {'weight': 0.45}},
            57: {56: {'weight': 0.45}}
        }

        return nodes_dict, edges_dict


def run():

    osmHandler = DataHandler("modules/create_graph/data/split_salvadore.osm",
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
    postEdge = {}
    tmpRes = []

    finder = NeighboursFinder(G)


    for postId, nodeId in map_posts_to_nodes.items():
        res = finder.search_near_posts(roadNodes, roadWays, nodeId, 0.8)
        print('PostID ' + str(postId) + ' Node: ' + str(nodeId) + ' r: ' + str(res))

        tmpRes.append((postId, nodeId, res))
        for res_id, res_dist in res:
                if nodeId in postEdge:
                    tmp = postEdge[nodeId]
                    tmp[roadNodes[map_posts_to_nodes[res_id]].node_id] = {'weight': res_dist}
                    postEdge[nodeId] = tmp
                    print(res_id)
                else:
                    postEdge[nodeId] = {roadNodes[map_posts_to_nodes[res_id]].node_id: {'weight': res_dist}}
    for k, v in roadNodes.items():
        if v.post_id != None:
            postNode[k] = v.__dict__
    for postId, nodeId, res in tmpRes:
        print('PostID ' + str(postId) + ' Node: ' + str(nodeId) + ' r: ' + str(res))
    if len(postEdge) != 0:
        drawGraph(G, postNode, postEdge)

    import json
    edges = []
    for source, value in postEdge.items():
        print(source)
        for dest, w in value.items():
            weight = w['weight']
            edges.append((source, dest, weight))
    graph = {'nodes': postNode,
             'edge': edges}
    f = open("posts.json", "w")
    f.write(json.dumps(graph))
    f.close()



if __name__ == "__main__":

    # osmHandler = DataHandler("data/duplica_dob_test_export.osm",
    #                         'data/List of Postal Offices (geographical location).csv')

    run()

