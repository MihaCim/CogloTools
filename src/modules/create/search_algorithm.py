import networkx as nx
import matplotlib.pyplot as plt
import math

nodes = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {"post": True}, 7: {"post": True}, 8: {}, 9: {}, 10: {},
         11: {}, 12: {"post": True}, 13: {}, 14: {"post": True}, 15: {}, 16: {}, 17: {}, 18: {}, 19: {}, 20: {},
         21: {}, 22: {}, 23: {"post": True}, 24: {}, 25: {}, 26: {}, 27: {}, 28: {}, 29: {}, 30: {}}

edges = {0: {1: {"weight": 0.5}, 2: {"weight": 0.2}, 20: {"weight": 0.3}, 21: {"weight": 0.6}},
         1: {7: {"weight": 0.5}, 0: {"weight": 0.5}},
         2: {0: {"weight": 0.5}, 3: {"weight": 0.5}, 6: {"weight": 0.5}},
         3: {2: {"weight": 0.5}, 4: {"weight": 0.5}, 5: {"weight": 0.5}},
         4: {3: {"weight": 0.5}},
         5: {3: {"weight": 0.5}},
         6: {2: {"weight": 0.5}, 7: {"weight": 0.5}, 16: {"weight": 0.5}},
         7: {8: {"weight": 0.5}, 11: {"weight": 0.5}, 15: {"weight": 0.5}, 6: {"weight": 0.5}, 1: {"weight": 0.5}},
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
        import time
        time.sleep(2)
    print("aa")
    print(results)

lenEdges = len(edges)

G = nx.Graph()

color_map = []
nodel = []
for node in nodes:
    nodel.append(node)
    if nodes[node].get("post") == None:
        color_map.append('blue')
    elif nodes[node].get("post") == True:
        color_map.append('red')

edgel = []
for edge in edges:
    for connection in edges[edge]:
        edgel.append((connection, edge))
        G.add_edge(connection, edge, weight=1)

search_near_posts(nodes, edges, 0)
G.add_nodes_from(range(lenEdges))

# use one of the edge properties to control line thickness
edgewidth = [d['weight'] for (u, v, d) in G.edges(data=True)]

# layout
pos = nx.spring_layout(G, iterations=50)
# pos = nx.random_layout(G)

# rendering
plt.figure(1)
plt.axis('off')
nx.draw_networkx_nodes(G, pos,
                       nodelist=nodel,
                       node_color=color_map,
                       alpha=0.8)
nx.draw_networkx_edges(G, pos, width=edgewidth, )
nx.draw_networkx_labels(G, pos)
plt.show()
