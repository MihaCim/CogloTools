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

    def has_traversed(self, node_id):
        """
        Checks if node_id is in the history of this node.
        """
        for hist_node_id, hist_node_dist_origin in self.eps_history:
            if hist_node_id == node_id:
                return True
        return False


def search_near_posts(node_id_node_map, node_id_edge_map, start_node_id, eps_km):
    # front = [(start_node_id, 0, [])]
    front = {
        start_node_id: FrontData(0, [], [])
    }
    visited_node_ids = set()
    results = []

    visited_node_ids.add(start_node_id)

    while len(front) != 0:
        active_node_id = None
        prev_node_id = None

        current_visited_points = []  # TODO: do we need this in the loop??

        min_distance = math.inf
        for node_id, node_data in front.items():
            if node_id not in node_id_edge_map:
                continue

            node_dist = node_data.origin_dist
            neigbours = node_id_edge_map[node_id]  # get neighbors od te tocke
            for neigbour in neigbours:
                edge_dist = neigbours[neigbour]["weight"]
                if node_dist + edge_dist < min_distance and (neigbour not in visited_node_ids):
                    min_distance = node_dist + edge_dist
                    active_node_id = neigbour
                    current_visited_points = [val for val in visited_node_ids]
                    prev_node_id = node_id

        print(active_node_id)
        print(min_distance)
        print(current_visited_points)
        print(prev_node_id)

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
            # check the history of this node to find a common intersection with
            # other nodes. If such an intersection is found, then move this post
            # to the intersection
            for node_id in front:
                node_data = front[node_id]

                pass

            current_visited_points += [active_node_id]
            if len(current_visited_points) == 1:
                results += [active_node_id]

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
        while True:
            oldest_node_id, oldest_node_dist_origin = active_node_history[0]
            newest_node_id, newest_node_dist_origin = active_node_history[-1]
            dist_diff = newest_node_dist_origin - oldest_node_dist_origin

            if dist_diff <= eps_km:
                break
            active_node_history.pop(0)

        front[active_node_id] = FrontData(
            min_distance,
            current_visited_points,
            active_node_history
        )
        # front.append((active_node_id, min_distance, current_visited_points))
        # add the active node to the list of visited nodes
        visited_node_ids.add(active_node_id)

        # check if we need to snap the current post back to the intersection
        if is_post:
            snap_node_id = active_node_id
            snap_node_history = [node_id for node_id in reversed(active_node_history)]  # TODO: optimize

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

                    found_intersec = len(intersects_node_ids) > 0
                    if found_intersec:
                        # swap the historical node with the current node

                        # swap the post_id of the historical node with the post_id
                        # of the current node
                        hist_node.post_id = snap_node.post_id
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
        prev_node_edges = node_id_edge_map[prev_node_id]
        all_visited = True
        for prev_neighbour_id in prev_node_edges:
            if prev_neighbour_id not in visited_node_ids:
                all_visited = False
                break

        if all_visited:
            del front[prev_node_id]

        print("visited:" + str(visited_node_ids))
        print("results:" + str(results))

    print("done")
    print(results)
    return results


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

    print(len(roadNodes))
    print(len(edgesDict))

    # edgeDict = {52622985: {353909925: {'weight': 0.15231763655473493}}, 353909925: {52623451: {'weight': 0.07337890027916426}}, 52623451: {4811392298: {'weight': 0.01964318956492365}}, 4811392298: {601582830: {'weight': 0.02062556272846447}}, 601582830: {307808176: {'weight': 0.05147979196677748}}, 307808176: {52623452: {'weight': 0.09546112854728007}}, 52623452: {4811392297: {'weight': 0.02284372864859456}}, 4811392297: {4576807405: {'weight': 0.018138793276397468}}, 4576807405: {307808171: {'weight': 0.04334250770526844}}, 307808171: {4576807403: {'weight': 0.023035458235654834}}, 4576807403: {52623454: {'weight': 0.04572161720477462}}, 52623454: {4811392296: {'weight': 0.05238365470062196}}, 4811392296: {601582833: {'weight': 0.029505255938167222}}, 601582833: {2559240816: {'weight': 0.047330445476829956}}, 2559240816: {4576807235: {'weight': 0.017666997223947503}}, 4576807235: {4576807225: {'weight': 0.013882681789838503}}, 4576807225: {4811392295: {'weight': 0.01719987493884642}}, 4811392295: {52623455: {'weight': 0.025928477199895026}}, 52623455: {601582834: {'weight': 0.10024997559695574}}, 601582834: {52623458: {'weight': 0.03403565103151516}}, 52623458: {4576807234: {'weight': 0.019780642002129808}}, 4576807234: {4811392294: {'weight': 0.01656489743030932}}, 4811392294: {2559240818: {'weight': 0.014613698043944518}}, 2559240818: {4811392293: {'weight': 0.041589187083856574}}, 4811392293: {4576807226: {'weight': 0.04474689669261864}}, 4576807226: {4576807245: {'weight': 0.012705779927321876}}, 4576807245: {52623459: {'weight': 0.04011210314229261}}, 52623459: {4811392292: {'weight': 0.022019892737680753}}, 4811392292: {52623461: {'weight': 0.014091480601974784}}, 52623461: {4811392291: {'weight': 0.01609690627165437}}, 4811392291: {4811392290: {'weight': 0.012336352226221}}, 4811392290: {52623462: {'weight': 0.014862758647383635}}, 52623462: {4811392289: {'weight': 0.014916309238560951}}, 4811392289: {4811392288: {'weight': 0.0142080016658224}}, 4811392288: {2559240820: {'weight': 0.02337188445494937}}, 2559240820: {596494728: {'weight': 0.027133932554022386}}, 596494728: {4811392287: {'weight': 0.023514567553248114}}, 4811392287: {596494729: {'weight': 0.0168730712026512}}, 596494729: {4811392286: {'weight': 0.01845382298651885}}, 4811392286: {4490093830: {'weight': 0.00936598850462634}}, 4490093830: {52623464: {'weight': 0.04322230175413446}}, 52623464: {2559240822: {'weight': 0.022754227831941757}}, 2559240822: {52623467: {'weight': 0.05048283329905171}}, 52623467: {4811392285: {'weight': 0.01999960860430806}}, 4811392285: {4490093831: {'weight': 0.03338954024438705}}, 4490093831: {52623469: {'weight': 0.019402939669473842}}, 52623469: {4490093832: {'weight': 0.02746136149530023}}, 4490093832: {4811392284: {'weight': 0.046642269888301634}}, 4811392284: {243511383: {'weight': 0.025725475793426555}}, 243511383: {4811392283: {'weight': 0.01721669506613568}}, 4811392283: {601582848: {'weight': 0.031305404934779756}}, 601582848: {52623470: {'weight': 0.10123561803127018}}, 52623470: {601582849: {'weight': 0.033056976708588225}}, 601582849: {4227722002: {'weight': 0.014766138130737218}}, 4227722002: {596494730: {'weight': 0.03131984039865943}}, 596494730: {4811392282: {'weight': 0.019322596015228243}}, 4811392282: {52623473: {'weight': 0.014913593416455137}}, 52623473: {4490094615: {'weight': 0.01802563875831372}}, 4490094615: {52623476: {'weight': 0.01833024774375529}}, 52623476: {4811392280: {'weight': 0.0021223429570728244}}, 4811392280: {4490094616: {'weight': 0.014821482379942219}}, 4490094616: {4811392279: {'weight': 0.016889292286405556}}, 4811392279: {2559240823: {'weight': 0.010486776619393987}}, 2559240823: {4227722001: {'weight': 0.012960387921750168}}, 4227722001: {596494738: {'weight': 0.015989513862500623}}, 596494738: {601582851: {'weight': 0.02189388370905597}}, 601582851: {4490094617: {'weight': 0.022757413232997622}}, 4490094617: {4811392278: {'weight': 0.012254379353697938}}, 4811392278: {601582852: {'weight': 0.018268801927815614}}, 601582852: {4811392277: {'weight': 0.024426548096511857}}, 4811392277: {52623479: {'weight': 0.012765861389552513}}, 52623479: {4811392276: {'weight': 0.06187773223925837}}, 4811392276: {4451957103: {'weight': 0.02575988315468027}}, 4451957103: {4227722000: {'weight': 0.032011207398087736}}, 4227722000: {52623480: {'weight': 0.07789959099264325}}, 52623480: {596494741: {'weight': 0.10788644527257805}}, 596494741: {4490094619: {'weight': 0.031382403341776194}}, 4490094619: {601582853: {'weight': 0.017894464493789033}}, 601582853: {4451956783: {'weight': 0.013524663934115144}}, 4451956783: {4451956779: {'weight': 0.015048009924293337}, 4451956784: {'weight': 0.01645247016291188}}, 4451956779: {601582857: {'weight': 0.06640022994153862}, 4451956780: {'weight': 0.018108939888578732}}, 601582857: {4227721964: {'weight': 0.04588778100818405}}, 4227721964: {4490094620: {'weight': 0.03007361428263911}}, 4490094620: {596494743: {'weight': 0.05918889311634176}}, 596494743: {53422656: {'weight': 0.061987548567938755}}, 53422656: {4451956759: {'weight': 0.02550270267229046}}, 95939434: {2242836846: {'weight': 0.028451521612240797}, 4488671381: {'weight': 0.01067860263790344}, 618840763: {'weight': 0.014770153358561527}}, 2242836846: {292263289: {'weight': 0.03768584373548411}}, 292263289: {292263290: {'weight': 0.02106986805484481}}, 292263290: {4537856905: {'weight': 0.01846378268323346}}, 4537856905: {292263291: {'weight': 0.012755304855402437}}, 292263291: {4537856906: {'weight': 0.008361469131224776}}, 4537856906: {4537856907: {'weight': 0.020165221839781478}}, 4537856907: {596494806: {'weight': 0.0059077326507021785}}, 596494806: {292263292: {'weight': 0.023583928436854588}}, 292263292: {292263293: {'weight': 0.02164833785336622}}, 292263293: {292263294: {'weight': 0.05233553082610441}}, 292263294: {292263295: {'weight': 0.032714263542725754}}, 292263295: {292263297: {'weight': 0.03759304422469743}})
    # roadNodes = <class 'dict'>: {52622985: <__main__.SearchNode object at 0x7f6efa1e6f28>, 353909925: <__main__.SearchNode object at 0x7f6edd941f28>, 52623451: <__main__.SearchNode object at 0x7f6edd9418d0>, 4811392298: <__main__.SearchNode object at 0x7f6edd941a20>, 601582830: <__main__.SearchNode object at 0x7f6edd9419b0>, 307808176: <__main__.SearchNode object at 0x7f6edd941f98>, 52623452: <__main__.SearchNode object at 0x7f6edd941940>, 4811392297: <__main__.SearchNode object at 0x7f6edd941b38>, 4576807405: <__main__.SearchNode object at 0x7f6edc8c4128>, 307808171: <__main__.SearchNode object at 0x7f6edc8c42b0>, 4576807403: <__main__.SearchNode object at 0x7f6edc8c4400>, 52623454: <__main__.SearchNode object at 0x7f6edc8c4630>, 4811392296: <__main__.SearchNode object at 0x7f6edc8c4668>, 601582833: <__main__.SearchNode object at 0x7f6edc8c4550>, 2559240816: <__main__.SearchNode object at 0x7f6edc8c4710>, 4576807235: <__main__.SearchNode object at 0x7f6edc8c4780>, 4576807225: <__main__.SearchNode object at 0x7f6edc8c4898>, 4811392295: <__main__.SearchNode object at 0x7f6edc8c47f0>, 52623455: <__main__.SearchNode object at 0x7f6edc8c4198>, 601582834: <__main__.SearchNode object at 0x7f6edc8c40f0>, 52623458: <__main__.SearchNode object at 0x7f6edc8c4320>, 4576807234: <__main__.SearchNode object at 0x7f6edc8c44a8>, 4811392294: <__main__.SearchNode object at 0x7f6edc8c46a0>, 2559240818: <__main__.SearchNode object at 0x7f6edc8c4828>, 4811392293: <__main__.SearchNode object at 0x7f6edc8c4860>, 4576807226: <__main__.SearchNode object at 0x7f6edc8c48d0>, 4576807245: <__main__.SearchNode object at 0x7f6edc8c4908>, 52623459: <__main__.SearchNode object at 0x7f6edc8c4940>, 4811392292: <__main__.SearchNode object at 0x7f6edc8c4978>, 52623461: <__main__.SearchNode object at 0x7f6edc8c49b0>, 4811392291: <__main__.SearchNode object at 0x7f6edc8c49e8>, 4811392290: <__main__.SearchNode object at 0x7f6edc8c4a20>, 52623462: <__main__.SearchNode object at 0x7f6edc8c4a58>, 4811392289: <__main__.SearchNode object at 0x7f6edc8c4a90>, 4811392288: <__main__.SearchNode object at 0x7f6edc8c4ac8>, 2559240820: <__main__.SearchNode object at 0x7f6edc8c4b00>, 596494728: <__main__.SearchNode object at 0x7f6edc8c4b38>, 4811392287: <__main__.SearchNode object at 0x7f6edc8c4b70>, 596494729: <__main__.SearchNode object at 0x7f6edc8c4ba8>, 4811392286: <__main__.SearchNode object at 0x7f6edc8c4be0>, 4490093830: <__main__.SearchNode object at 0x7f6edc8c4c18>, 52623464: <__main__.SearchNode object at 0x7f6edc8c4c50>, 2559240822: <__main__.SearchNode object at 0x7f6edc8c4c88>, 52623467: <__main__.SearchNode object at 0x7f6edc8c4cc0>, 4811392285: <__main__.SearchNode object at 0x7f6edc8c4cf8>, 4490093831: <__main__.SearchNode object at 0x7f6edc8c4d30>, 52623469: <__main__.SearchNode object at 0x7f6edc8c4d68>, 4490093832: <__main__.SearchNode object at 0x7f6edc8c4da0>, 4811392284: <__main__.SearchNode object at 0x7f6edc8c4dd8>, 243511383: <__main__.SearchNode object at 0x7f6edc8c4e10>, 4811392283: <__main__.SearchNode object at 0x7f6edc8c4e48>, 601582848: <__main__.SearchNode object at 0x7f6edc8c4e80>, 52623470: <__main__.SearchNode object at 0x7f6edc8c4eb8>, 601582849: <__main__.SearchNode object at 0x7f6edc8c4ef0>, 4227722002: <__main__.SearchNode object at 0x7f6edc8c4f28>, 596494730: <__main__.SearchNode object at 0x7f6edc8c4f60>, 4811392282: <__main__.SearchNode object at 0x7f6edc8c4f98>, 52623473: <__main__.SearchNode object at 0x7f6edc8c4fd0>, 4490094615: <__main__.SearchNode object at 0x7f6edc8c9048>, 52623476: <__main__.SearchNode object at 0x7f6edc8c9080>, 4811392280: <__main__.SearchNode object at 0x7f6edc8c90b8>, 4490094616: <__main__.SearchNode object at 0x7f6edc8c90f0>, 4811392279: <__main__.SearchNode object at 0x7f6edc8c9128>, 2559240823: <__main__.SearchNode object at 0x7f6edc8c9160>, 4227722001: <__main__.SearchNode object at 0x7f6edc8c9198>, 596494738: <__main__.SearchNode object at 0x7f6edc8c91d0>, 601582851: <__main__.SearchNode object at 0x7f6edc8c9208>, 4490094617: <__main__.SearchNode object at 0x7f6edc8c9240>, 4811392278: <__main__.SearchNode object at 0x7f6edc8c9278>, 601582852: <__main__.SearchNode object at 0x7f6edc8c92b0>, 4811392277: <__main__.SearchNode object at 0x7f6edc8c92e8>, 52623479: <__main__.SearchNode object at 0x7f6edc8c9320>, 4811392276: <__main__.SearchNode object at 0x7f6edc8c9358>, 4451957103: <__main__.SearchNode object at 0x7f6edc8c9390>, 4227722000: <__main__.SearchNode object at 0x7f6edc8c93c8>, 52623480: <__main__.SearchNode object at 0x7f6edc8c9400>, 596494741: <__main__.SearchNode object at 0x7f6edc8c9438>, 4490094619: <__main__.SearchNode object at 0x7f6edc8c9470>, 601582853: <__main__.SearchNode object at 0x7f6edc8c94a8>, 4451956783: <__main__.SearchNode object at 0x7f6edc8c94e0>, 4451956779: <__main__.SearchNode object at 0x7f6edc8c9518>, 601582857: <__main__.SearchNode object at 0x7f6edc8c9550>, 4227721964: <__main__.SearchNode object at 0x7f6edc8c9588>, 4490094620: <__main__.SearchNode object at 0x7f6edc8c95c0>, 596494743: <__main__.SearchNode object at 0x7f6edc8c95f8>, 53422656: <__main__.SearchNode object at 0x7f6edc8c9630>, 95939434: <__main__.SearchNode object at 0x7f6edc8c9668>, 2242836846: <__main__.SearchNode object at 0x7f6edc8c96a0>, 292263289: <__main__.SearchNode object at 0x7f6edc8c96d8>, 292263290: <__main__.SearchNode object at 0x7f6edc8c9710>, 4537856905: <__main__.SearchNode object at 0x7f6edc8c9748>, 292263291: <__main__.SearchNode object at 0x7f6edc8c9780>, 4537856906: <__main__.SearchNode object at 0x7f6edc8c97b8>, 4537856907: <__main__.SearchNode object at 0x7f6edc8c97f0>, 596494806: <__main__.SearchNode object at 0x7f6edc8c9828>, 292263292: <__main__.SearchNode object at 0x7f6edc8c9860>, 292263293: <__main__.SearchNode object at 0x7f6edc8c9898>, 292263294: <__main__.SearchNode object at 0x7f6edc8c98d0>, 292263295: <__main__.SearchNode object at 0x7f6edc8c9908>, 292263297: <__main__.SearchNode object at 0x7f6edc8c9940>...
    # for n in nodesNode:
    nodesDict[0] = SearchNode(0, 0, True)
    nodesDict[1] = SearchNode(1, None, False)
    nodesDict[2] = SearchNode(2, None, False)
    nodesDict[3] = SearchNode(3, None, False)
    nodesDict[4] = SearchNode(4, None, False)
    nodesDict[5] = SearchNode(5, None, False)
    nodesDict[6] = SearchNode(6, None, False)
    nodesDict[7] = SearchNode(7, None, False)
    nodesDict[8] = SearchNode(8, None, False)
    nodesDict[9] = SearchNode(9, None, False)
    nodesDict[10] = SearchNode(10, None, False)
    nodesDict[11] = SearchNode(11, None, False)
    nodesDict[12] = SearchNode(12, 1, True)
    nodesDict[13] = SearchNode(13, 2, True)
    nodesDict[14] = SearchNode(14, None, False)
    nodesDict[15] = SearchNode(15, None, False)
    nodesDict[16] = SearchNode(16, None, False)
    nodesDict[17] = SearchNode(17, None, False)
    nodesDict[18] = SearchNode(18, None, False)
    nodesDict[19] = SearchNode(19, None, False)
    nodesDict[20] = SearchNode(20, None, False)
    nodesDict[21] = SearchNode(21, None, False)
    nodesDict[22] = SearchNode(22, None, False)
    nodesDict[24] = SearchNode(24, None, False)
    nodesDict[23] = SearchNode(23, None, False)
    nodesDict[25] = SearchNode(25, 3, True)
    nodesDict[26] = SearchNode(26, None, False)
    nodesDict[27] = SearchNode(27, 4, True)
    nodesDict[28] = SearchNode(28, None, False)
    nodesDict[29] = SearchNode(29, None, False)
    nodesDict[30] = SearchNode(30, None, False)
    nodesDict[31] = SearchNode(31, None, False)
    nodesDict[32] = SearchNode(32, None, False)
    nodesDict[33] = SearchNode(33, None, False)
    nodesDict[34] = SearchNode(34, 5, True)
    nodesDict[35] = SearchNode(35, None, False)
    nodesDict[36] = SearchNode(36, None, False)
    nodesDict[37] = SearchNode(37, None, False)
    nodesDict[38] = SearchNode(38, None, False)
    nodesDict[39] = SearchNode(39, None, False)
    nodesDict[40] = SearchNode(40, 6, True)
    nodesDict[41] = SearchNode(41, 7, True)

    edgesDict = {
        0: {1: {'weight': 0.15}, 2: {'weight': 0.15}, 3: {'weight': 0.15}, 4: {'weight': 0.15}},
        1: {5: {'weight': 0.15}, 6: {'weight': 0.15}, 0: {'weight': 0.15}},
        2: {7: {'weight': 0.15}, 8: {'weight': 0.15}, 1: {'weight': 0.15}},
        3: {0: {'weight': 0.15}, 19: {'weight': 0.15}, 20: {'weight': 0.15}},
        4: {0: {'weight': 0.15}, 30: {'weight': 0.15}},
        5: {1: {'weight': 0.15}},
        6: {1: {'weight': 0.15}, 7: {'weight': 0.15}, 8: {'weight': 0.15}},
        7: {6: {'weight': 0.15}},
        8: {6: {'weight': 0.15}},
        9: {41: {'weight': 0.5}, 12: {'weight': 1.5}, 2: {'weight': 0.15}, 13: {'weight': 0.7}},
        10: {2: {'weight': 0.15}, 11: {'weight': 0.15}, 12: {'weight': 0.15}},
        11: {10: {'weight': 0.15}},
        12: {10: {'weight': 0.15}},
        13: {9: {'weight': 0.7}, 14: {'weight': 0.15}, 15: {'weight': 0.15}},
        14: {13: {'weight': 0.15}},
        15: {13: {'weight': 0.15}},
        16: {41: {'weight': 0.15}},
        17: {16: {'weight': 0.15}},
        18: {16: {'weight': 0.15}},
        19: {3: {'weight': 0.15}},
        20: {3: {'weight': 0.15}},
        21: {20: {'weight': 0.15}},
        22: {21: {'weight': 0.15}},
        23: {22: {'weight': 0.15}},
        24: {22: {'weight': 0.15}},
        25: {21: {'weight': 0.15}},
        26: {25: {'weight': 0.15}},
        27: {20: {'weight': 0.5}},
        28: {27: {'weight': 0.65}},
        29: {27: {'weight': 0.65}},

        30: {4: {'weight': 0.15}},
        31: {30: {'weight': 0.15}},
        32: {30: {'weight': 0.3}},
        33: {32: {'weight': 0.4}},
        35: {34: {'weight': 0.15}},
        36: {35: {'weight': 0.15}},
        37: {30: {'weight': 0.15}},
        38: {37: {'weight': 0.15}},
        39: {38: {'weight': 0.15}},
        40: {39: {'weight': 0.15}},
        41: {40: {'weight': 0.15}}

        }
    algPostalWays = []
    #for posts in postsNodes:
        # posts = 401868937
    posts = nodesDict[0]
    results = search_near_posts(nodesDict, edgesDict, posts, 1)
    for result in results:
            tmp = parseOsm.Way()
            tmp.addPath(result, posts)
            tmp.addDistance(utils.calcDistance(roadNodes[result].lat, roadNodes[result].lon, roadNodes[posts].lat,
                                               roadNodes[posts].lon))
            algPostalWays.append(tmp)

    drawGraph(algPostalWays, G, roadNodesAnotated, postsNodes)
