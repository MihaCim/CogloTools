import math
import copy
from src.modules.create_graph.pojo.front_data import FrontData

class NeighboursFinder():

    def search_near_posts(self, node_id_node_map_tmp, node_id_edge_map, start_node_id, eps_km):
        # front = [(start_node_id, 0, [])]
        node_id_node_map = copy.deepcopy(node_id_node_map_tmp)
        node_id_edge_map = copy.deepcopy(node_id_edge_map)
        front = {
            start_node_id: FrontData(start_node_id, [], [])
        }
        visited_node_ids = set()
        results = []


        visited_node_ids.add(start_node_id)

        while len(front) != 0:

            active_node_id = None
            prev_node_id = None
            current_visited_points = None  # TODO: do we need this in the loop??
            min_distance = math.inf

            for node_id, node_data in front.items():
                # print(node_id)
                # print(node_data)

                if node_id not in node_id_edge_map:
                    continue

                node_dist = node_data.origin_dist
                neigbours = node_id_edge_map[node_id]  # get neighbors od te tocke

                for neigbour in neigbours:
                    edge_dist = neigbours[neigbour]["weight"]
                    if ((node_dist + edge_dist) < min_distance) and (neigbour not in visited_node_ids):
                        min_distance = node_dist + edge_dist
                        active_node_id = neigbour
                        current_visited_points = [val for val in node_data.prev_posts]
                        prev_node_id = node_id

            # print(active_node_id)
            # print(min_distance)
            # print(current_visited_points)
            # print(prev_node_id)

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
                # newest_node_id, newest_node_dist_origin = active_node_history[-1]
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

            # front.append((active_node_id, min_distance, current_visited_points))
            # add the active node to the list of visited nodes

            visited_node_ids.add(active_node_id)

            # check if we need to snap the current post back to the intersection
            if is_post:
                snap_node_id = active_node_id
                snap_node_history = [node_id for node_id in reversed(active_node_history)]  # TODO: optimize
                # TODO check if all the naighbors of previous point were visited
                # if not snap the node back

                #print(snap_node_id)
                #print(snap_node_history)
                all_visited = True
                snap_back_to = -1
                for node_id, eps_distance in snap_node_history:
                    #print(node_id_node_map[node_id])
                    for id in node_id_edge_map[node_id]:
                        if id not in visited_node_ids:
                            all_visited = False
                            snap_back_to = node_id
                            break

                if all_visited == False and node_id_node_map[snap_back_to].post_id is None:
                    node_id_node_map[snap_back_to].post_id = node_id_node_map[snap_node_id].post_id
                    node_id_node_map[snap_back_to].is_post = True
                    node_id_node_map[snap_node_id].is_post = False
                    node_id_node_map[snap_node_id].post_id = None
                    ##snap_node_id je node na katerem smo in katerega zelimo prestavit
                    ## snop_back_to je lokacija nove lokacije

                    for f in front:
                        for id, dist in front[f].eps_history:
                            if snap_back_to == id and f != snap_node_id:
                                #print("nasel")
                                #print(front[f].eps_history)
                                front[snap_back_to].prev_posts.append(snap_back_to)
                    if snap_back_to in front:
                        front[snap_back_to].prev_posts.append(snap_back_to)


                else:

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

            #print(front)

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

           # print("visited:" + str(visited_node_ids))
           # print("results:" + str(results))

        #print("done")
        #print(results)
        return results
