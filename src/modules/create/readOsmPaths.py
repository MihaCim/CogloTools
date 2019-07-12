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
            labels[i] = nodes[posts].post_id + "("+str(posts)+")"
        else:
            labels[i] = posts
            color_map.append('green')

        li.append(posts)
        G.add_node(posts)

        i = i +1


    for key, value in ways.items():
        for kc, vc in value.items():
            print(value)
            print(vc)

            G.add_edge(key, kc, weight=vc['weight'])


    import matplotlib.pyplot as plt

            # plt.figure(1)
    pos = nx.spring_layout(G, k=0.25, iterations=40)
    nx.draw_networkx_nodes(G, pos, node_color= color_map, nodelist=li)
    nx.draw_networkx_edges(G, pos, nodelist=li, node_color='g')


    nx.draw_networkx_labels(G, pos, labels, font_size=16)

    plt.show()


class SearchNode:

    def __init__(self, node_id, post_id=None, is_post=False):
        self.node_id = node_id
        self.post_id = post_id
        self.is_post = is_post


class FrontData:

    def __init__(self, origin_dist, prev_posts, eps_history):
        self.origin_dist = origin_dist
        self.prev_posts = prev_posts
        self.eps_history = eps_history

    def has_traversed(self, n_id):
        """
        Checks if node_id is in the history of this node.
        """
        for hist_node_id, hist_node_dist_origin in self.eps_history:
            if hist_node_id == n_id:
                return True
        return False


def search_near_posts(node_id_node_map, node_id_edge_map, start_node_id, eps_km):
    # front = [(start_node_id, 0, [])]
    front = {
        start_node_id: FrontData(0, [], [])
    }
    visited_node_ids = set()
    results = []

    visited_node_ids.add(0)

    while len(front) != 0:

        active_node_id = None
        prev_node_id = None
        current_visited_points = None  # TODO: do we need this in the loop??
        min_distance = math.inf

        for node_id, node_data in front.items():
            #print(node_id)
            #print(node_data)

            if node_id not in node_id_edge_map:
                continue

            node_dist = node_data.origin_dist
            neigbours = node_id_edge_map[node_id]  # get neighbors od te tocke
            print("Neighbours of "+str(node_id))
            for neigbour in neigbours:
                print("===============================================================================")
                print("Nei of "+str(neigbour))
                edge_dist = neigbours[neigbour]["weight"]

                print(neigbours)
                print(node_dist + edge_dist )
                print(min_distance)
                print(neigbour)
                print(visited_node_ids)
                print("===============================================================================")
                if ((node_dist + edge_dist) < min_distance) and (neigbour not in visited_node_ids):
                    min_distance = node_dist + edge_dist
                    active_node_id = neigbour
                    current_visited_points = [val for val in node_data.prev_posts]
                    prev_node_id = node_id

        #print(active_node_id)
        #print(min_distance)
        #print(current_visited_points)
        #print(prev_node_id)

        if active_node_id is None:
            # we were unable to find any new neighbours to extend the front
            # that means that we have searched through the entire graph
            # we can safely exit the loop
            print('Cannot extend the front. No neigbours available. Finishing search.')
            break

        if active_node_id not in node_id_node_map:
            raise ValueError('WTF!? Found an invalid node: ' + str(active_node_id))

        # check if the active node is a post office. if so, add it to the results
        is_post = node_id_node_map[active_node_id].post_id is not None
        if is_post:
            current_visited_points += [active_node_id]
            print("Active node id: "+str(active_node_id))
            print(current_visited_points)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            if len(current_visited_points) == 1:
                results += [node_id_node_map[active_node_id].post_id]

        # if active_node_id in nodes and nodes[active_node_id].get("post"):
        #    current_visited_points.append(prev_node_id)
        #    ##prestavi ..............
        #    print(current_visited_points)
        #    if len(current_visited_points) == 1:
        #        results.append(active_node_id)

        # extend the front with the active node

        prev_node_data = front[prev_node_id]

        # compute the history of the new node
        active_node_history = prev_node_data.eps_history + [(prev_node_id, prev_node_data.origin_dist)]

        active_node_dist_origin = min_distance
        while len(active_node_history) > 0:
            oldest_node_id, oldest_node_dist_origin = active_node_history[0]
            #newest_node_id, newest_node_dist_origin = active_node_history[-1]
            dist_diff = active_node_dist_origin - oldest_node_dist_origin
            if dist_diff <= eps_km:
                break
            active_node_history.pop(0)

        front[active_node_id] = FrontData(
            min_distance,
            current_visited_points,
            active_node_history
        )

        '''

        for f in front:
            print(f)
            current_origin_distance = front[f].origin_dist
            current_eps_history = front[f].eps_history
            while True:
                if current_eps_history is None or len(current_eps_history) == 0:
                    break
                oldest_node_id, oldest_node_dist_origin = current_eps_history[0]
                dist_diff = current_origin_distance - oldest_node_dist_origin

                if dist_diff <= eps_km:
                    break
                current_eps_history.pop(0)
            front[f].eps_history = current_eps_history
            '''


        #front.append((active_node_id, min_distance, current_visited_points))
        # add the active node to the list of visited nodes

        visited_node_ids.add(active_node_id)
        print("Front: "+str(front.keys()))
        print("Visited: "+str(visited_node_ids))
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


        # check if we need to snap the current post back to the intersection
        if is_post:
            snap_node_id = active_node_id
            snap_node_history = [node_id for node_id in reversed(active_node_history)]  # TODO: optimize
            #TODO check if all the naighbors of previous point were visited
            #if not snap the node back

            found_intersec = True
            while found_intersec:
                # if there is no more history to traverse the procedure is finished (we have already
                # searched for eps kilometers back)
                if len(snap_node_history) == 0:
                    break

                found_intersec = False

                snap_node = node_id_node_map[snap_node_id]
                for hist_nodeN, hist_node_data in enumerate(snap_node_history):
                    hist_node_id, hist_node_dist_origin = hist_node_data
                    hist_node = node_id_node_map[hist_node_id]
                    is_hist_node_post = hist_node.post_id is not None
                    if is_hist_node_post:
                        # we have found a post office when searching through the history
                        # that means that this procedure was already run on that post office
                        # and we were unable to snap it to an intersection. Hence, there is
                        # no need to run the procedure again.
                        break

                    intersects_node_ids = []
                    for front_node_id in front:
                        front_node_data = front[front_node_id]
                        if front_node_data.has_traversed(hist_node_id):
                            intersects_node_ids.append(front_node_id)

                    found_intersec = len(intersects_node_ids) > 1
                    if found_intersec:
                        # swap the historical node with the current node

                        # swap the post_id of the historical node with the post_id
                        # of the current node
                        hist_node.post_id = snap_node.post_id
                        hist_node.is_post = True
                        snap_node.is_post = False
                        snap_node.post_id = None

                        # add hist_node_id into prev_posts for all the found nodes
                        # hist_node_id can be added as the last post office visited
                        # if this was not the case that other post would have already
                        # been visited and would have been snapped back to the same
                        # intersection we are snapping the current post to. Hence, we would
                        # have terminated in the is_hist_node_post check
                        for intersec_node_id in intersects_node_ids:
                            intersec_node_data = front[intersec_node_id]
                            intersec_node_data.prev_posts += [hist_node_id]

                        # update the snap node and history
                        snap_node_id = hist_node_id
                        snap_node_history = snap_node_history[hist_nodeN + 1:]

        print(front)


        # if all the neighbours of the previous point have been visited, remove it
        # from the front

        tmpD = []
        for node_id, node_data in front.items():
            tmpD.append(node_id)
            prev_node_edges = node_id_edge_map[node_id]
            for prev_neighbour_id in prev_node_edges:
                if prev_neighbour_id not in visited_node_ids:
                    tmpD.pop()
                    break

        for node_id in tmpD:
            del front[node_id]

        print("visited:" + str(visited_node_ids))
        print("results:" + str(results))

    print("done")
    print(results)
    return results


def synticGraph():
    nodesDict = {}
    nodesDict[0] = SearchNode(0, "A0", True)
    nodesDict[1] = SearchNode(1, None, False)
    nodesDict[2] = SearchNode(2, None, False)
    nodesDict[3] = SearchNode(3, None, False)
    nodesDict[4] = SearchNode(4, None, False)
    nodesDict[5] = SearchNode(5, None, False)
    nodesDict[6] = SearchNode(6, None, False)
    nodesDict[7] = SearchNode(7, "A1", True)
    nodesDict[8] = SearchNode(8, None, False)
    nodesDict[9] = SearchNode(9, None, False)
    nodesDict[10] = SearchNode(10, None, False)
    nodesDict[11] = SearchNode(11, "A2", True)
    nodesDict[12] = SearchNode(12, "A3", True)
    nodesDict[13] = SearchNode(13, "A4", True)
    nodesDict[14] = SearchNode(14, None, False)
    nodesDict[15] = SearchNode(15, None, False)
    nodesDict[16] = SearchNode(16, None, False)
    nodesDict[17] = SearchNode(17, None, False)
    nodesDict[18] = SearchNode(18, None, False)
    nodesDict[19] = SearchNode(19, "A5", True)
    nodesDict[20] = SearchNode(20, None, False)
    nodesDict[21] = SearchNode(21, None, False)
    nodesDict[22] = SearchNode(22, None, False)
    nodesDict[24] = SearchNode(24, None, False)
    nodesDict[23] = SearchNode(23, None, False)
    nodesDict[25] = SearchNode(25, "A6", True)
    nodesDict[26] = SearchNode(26, None, False)
    nodesDict[27] = SearchNode(27, "A7", True)
    nodesDict[28] = SearchNode(28, None, False)
    nodesDict[29] = SearchNode(29, None, False)
    nodesDict[30] = SearchNode(30, None, False)
    nodesDict[31] = SearchNode(31, None, False)
    nodesDict[32] = SearchNode(32, None, False)
    nodesDict[33] = SearchNode(33, None, False)
    nodesDict[34] = SearchNode(34, "A8", True)
    nodesDict[35] = SearchNode(35, None, False)
    nodesDict[36] = SearchNode(36, None, False)
    nodesDict[37] = SearchNode(37, None, False)
    nodesDict[38] = SearchNode(38, None, False)
    nodesDict[39] = SearchNode(39, None, False)
    nodesDict[40] = SearchNode(40, "A9", True)
    nodesDict[41] = SearchNode(41, "A10", True)
    nodesDict[42] = SearchNode(42, None, False)
    nodesDict[43] = SearchNode(43, None, False)
    nodesDict[44] = SearchNode(44, None, False)
    nodesDict[45] = SearchNode(45, None, False)
    nodesDict[46] = SearchNode(46, None, False)

    edgesDict = {
        0: {1: {'weight': 2}, 2: {'weight': 2}, 3: {'weight': 2}, 4: {'weight': 2}},
        1: {5: {'weight': 0.5}, 6: {'weight': 2}, 0: {'weight': 2}},
        2: {0: {'weight': 2}, 9: {'weight': 2}, 10: {'weight': 6}},
        3: {0: {'weight': 2}, 19: {'weight': 2}, 20: {'weight': 0.5}},
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
        20: {3: {'weight': 0.5}, 21: {'weight': 0.3}, 27: {'weight': 0.3}},
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
        46: {45: {'weight': 0.5}}
        }

    return nodesDict, edgesDict

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

    #print(len(roadNodes))
    #print(len(edgesDict))

    nodesDict,edgesDict = synticGraph()

   # for n in nodesNode:
    algPostalWays = []
    #for posts in postsNodes:
        # posts = 401868937
    posts = 0
    # drawStaticGraph(nodesDict, edgesDict, [])
    #posts = 2244725770
    results = search_near_posts(nodesDict, edgesDict, posts, 1)
    drawStaticGraph(nodesDict, edgesDict, results)
    #drawStaticGraph(nodesDict, edgesDict)

    '''
    for result in results:
            tmp = parseOsm.Way()
            tmp.addPath(result, posts)
            tmp.addDistance(utils.calcDistance(roadNodes[result].lat, roadNodes[result].lon, roadNodes[posts].lat,
                                               roadNodes[posts].lon))
            algPostalWays.append(tmp)

    '''
    drawGraph(algPostalWays, G, roadNodesAnotated, postsNodes)

