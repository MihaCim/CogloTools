#!/usr/bin/python3


from src.modules.create_graph.utils import utils
from src.modules.create_graph.data_parser.data_handler import DataHandler
import networkx as nx
from src.modules.create_graph.pojo.front_data import FrontData
from src.modules.create_graph.pojo.search_node import SearchNode
import src.modules.create_graph.neighbours_finder as neighbourAlg


def drawGraph(algPostalWays, H, nodes, postalNodes):
    G = nx.Graph()
    li = []

    for posts in postalNodes:
        li.append(posts)
        G.add_node(posts, pos=(nodes[posts].lat, nodes[posts].lon))

    for edge in algPostalWays:
        l = edge.get_all_nodes()
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

    osmHandler = DataHandler("data/test_export.osm",
                             'data/List of Postal Offices (geographical location).csv')
    G = osmHandler.graph_viz()

    roadNodes = osmHandler.modified_nodes
    roadWays = osmHandler.modified_ways




    # nodesDict,edgesDict = synticGraph()
    # drawStaticGraph(nodesDict, edgesDict, results)
    finder = neighbourAlg.NeighboursFinder()
    finder.search_near_posts(roadNodes, roadWays, 4576807226, 1)
    '''
    for posts in postsNodes:
        results = finder.search_near_posts(nodesDict, edgesDict, posts, 1)
        for result in results:
            tmp = parse_osm.Way()
            tmp.add_path(result, posts)
            tmp.add_distance(utils.calcDistance(roadNodes[result].lat, roadNodes[result].lon, roadNodes[posts].lat,
                                                roadNodes[posts].lon))
            # algPostalWays.append(tmp)
            
    '''

    # drawGraph(algPostalWays, G, roadNodesAnotated, postsNodes)
