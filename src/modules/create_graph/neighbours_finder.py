import math
import copy
from modules.create_graph.pojo.front_data import FrontData
import time
import networkx as nx
import matplotlib.pyplot as plt


class NeighboursFinder():

    def __init__(self, G=None):
        self.G = G


    def drawGraph(self, H_roads, front, postsRes, node_id_node_map_tmp):
        plt.clf()
        plt.cla()
        plt.close()

        G_front = nx.Graph()
        K_posts = nx.Graph()
        li = []
        for k, v in front.items():
            li.append(k)
            G_front.add_node(k, pos=(node_id_node_map_tmp[k].lat, node_id_node_map_tmp[k].lon))

        color_map = []
        posts = []
        if len(postsRes) != 0:
            for k, v in node_id_node_map_tmp.items():
                if v.post_id != None and not (v.post_id in postsRes[0]):
                    posts.append(k)
                    K_posts.add_node(k, pos=(node_id_node_map_tmp[k].lat, node_id_node_map_tmp[k].lon))
                    color_map.append('blue')
                elif v.post_id != None and v.post_id in postsRes[0]:
                    posts.append(k)
                    K_posts.add_node(k, pos=(node_id_node_map_tmp[k].lat, node_id_node_map_tmp[k].lon))
                    color_map.append('red')

        # pos = nx.spring_layout(G, k=0.25, iterations=40)
        pos = nx.get_node_attributes(H_roads, 'pos', )

        nx.draw(H_roads, pos=pos, node_size=0.1, node_color='g', edge_color='g', )
        nx.draw_networkx_nodes(G_front, pos, node_size=100, nodelist=li, node_color='rosybrown')
        nx.draw_networkx_nodes(K_posts, pos, nodelist=posts, node_color=color_map)

        plt.show()
        G_front.clear()
        K_posts.clear()
        # H_roads.clear()


    def __second_step_alg(self, node_id_node_map_tmp, node_id_edge_map, f, visited_node, eps_km):
        # front = [(start_node_id, 0, [])]
        node_id_node_map = copy.deepcopy(node_id_node_map_tmp)
        node_id_edge_map = copy.deepcopy(node_id_edge_map)
        front = f

        visited_node_ids = set()
        results = []
        posts_in_front_count = 0

        visited_node_ids = visited_node

        i = 0
        start_time = time.time()

        exhausted_paths_count = 0

        # the counter is increased when have aleready one post office and than increase to the 3
        # if there are already two or more we are not touch it
        # also we have to decrese counter only if it has more or exactly 2 post offices in list
        counter_added = 0
        counter_modified = 0
        counter_snapped = 0
        counter_deleted = 0

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
                print(str(front))
                break

            print('active node: ' + str(active_node_id))

            if active_node_id not in node_id_node_map:
                raise ValueError('WTF!? Found an invalid node: ' + str(active_node_id))

            # check if the active node is a post office. if so, add it to the results
            is_post = node_id_node_map[active_node_id].post_id is not None
            if is_post:
                current_visited_points += [active_node_id]
                if len(current_visited_points) == 1:
                    results += [(node_id_node_map[active_node_id].post_id, min_distance)]

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

            # add the active node to the list of visited nodes
            visited_node_ids.add(active_node_id)

            # only add the active node to the front if it has any
            # non-visited neighbours
            active_node_neigh_ids = node_id_edge_map[active_node_id]
            all_neighbours_visited = True
            for neigh_id in active_node_neigh_ids:
                if neigh_id not in visited_node_ids:
                    all_neighbours_visited = False
                    break

            # if all the neighbours of the active node are visited, we need
            # to check if we can delete them now after one of their neighbours
            # (the active node) has been visited
            for neigh_id in active_node_neigh_ids:
                if neigh_id == prev_node_id or neigh_id not in front:
                    continue
                all_neigh_of_neigh_visited = True
                neigh_of_neigh_ids = node_id_edge_map[neigh_id]
                for neigh_of_neigh_id in neigh_of_neigh_ids:
                    if neigh_of_neigh_id not in visited_node_ids:
                        all_neigh_of_neigh_visited = False
                        break
                if all_neigh_of_neigh_visited:
                    if len(front[neigh_id].prev_posts) >= 2:
                        print('decreased cnt')
                        exhausted_paths_count -= 1
                        counter_deleted += 1
                    del front[neigh_id]
                    print('deleted neighbour of neighbour: ' + str(neigh_of_neigh_id))

            if not all_neighbours_visited:
                # add the node to the front
                front[active_node_id] = FrontData(
                    min_distance,
                    current_visited_points,
                    active_node_history
                )
                print("Added : "+ str(active_node_id) + " n_posts: " + str(len(current_visited_points)))
                if len(current_visited_points) >= 2:
                    print('increased cnt')
                    exhausted_paths_count += 1
                    counter_added += 1

            # front.append((active_node_id, min_distance, current_visited_points))



            # check if we need to snap the current post back to the intersection
            if is_post:
                snap_node_id = active_node_id
                snap_node_history = [node_id for node_id in reversed(active_node_history)]  # TODO: optimize
                # TODO check if all the naighbors of previous point were visited

                all_visited = False
                snap_back_to = None
                if len(snap_node_history) != 0:
                    snap_back_to = snap_node_history[-1][0]
                    for node_id, eps_distance in snap_node_history:
                        # print(node_id_node_map[node_id])
                        if node_id_node_map[node_id].post_id is not None:
                            all_visited = True
                            break

                if not all_visited and snap_back_to is not None and node_id_node_map[snap_back_to].post_id is None:
                    # we have encountered a post office, but the paths from the intersection
                    # have not been exhausted. We need to snap the post back to the intersection
                    node_id_node_map[snap_back_to].post_id = node_id_node_map[snap_node_id].post_id
                    node_id_node_map[snap_back_to].is_post = True
                    print('snap variant 1 to: ' + str(snap_back_to))

                    for front_node_id in front:
                        for hist_node_id, dist in front[front_node_id].eps_history:
                            ratio = dist / eps_km
                            if snap_back_to == hist_node_id and front_node_id != snap_node_id: #and ratio >= 1:
                                front_node_prev_posts = front[front_node_id].prev_posts
                                if snap_node_id in front_node_prev_posts:
                                    print('adding duplicate!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                                front_node_prev_posts.append(snap_node_id)
                                print('currection, post: ' + str(snap_node_id))
                                if len(front_node_prev_posts) == 2:
                                    print('increased cnt')
                                    exhausted_paths_count += 1
                                    counter_modified += 1
                                break
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
                                    ratio = front_node_data.origin_dist / eps_km
                                    #if ratio >= 1:
                                    intersects_node_ids.append(front_node_id)

                            found_intersec = len(intersects_node_ids) > 1
                            if found_intersec:
                                # swap the historical node with the current node

                                # swap the post_id of the historical node with the post_id
                                # of the current node
                                hist_node.post_id = snap_node.post_id
                                hist_node.is_post = True
                                print('snap variant 2 to: ' + str(hist_node_id))

                                # add hist_node_id into prev_posts for all the found nodes
                                # hist_node_id can be added as the last post office visited
                                # if this was not the case that other post would have already
                                # been visited and would have been snapped back to the same
                                # intersection we are snapping the current post to. Hence, we would
                                # have terminated in the is_hist_node_post check
                                for intersec_node_id in intersects_node_ids:
                                    intersec_node_data = front[intersec_node_id]
                                    if snap_node_id in intersec_node_data.prev_posts:
                                        print('adding duplicate!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                                    intersec_node_data.prev_posts += [snap_node_id]
                                    if len(intersec_node_data.prev_posts) == 2:
                                        print('increased cnt')
                                        exhausted_paths_count += 1
                                        counter_modified += 1

                                # update the snap node and history
                                snap_node_id = hist_node_id
                                snap_node_history = snap_node_history[hist_nodeN + 1:]

            # if all the neighbours of the previous point have been visited, remove it
            # from the front
            # TODO: optimize this - have a counter in each node that counts
            # TODO: how many neighbours have been visited

            prev_node_neighbour_ids = node_id_edge_map[prev_node_id]
            all_neighbours_visited = True
            for neighbour_id in prev_node_neighbour_ids:
                if neighbour_id not in visited_node_ids:
                    all_neighbours_visited = False
                    break

            prev_node_visited = [(neigh_id, neigh_id in visited_node_ids) for neigh_id in prev_node_neighbour_ids]
            print('checking if node exhausted: ' + str(prev_node_id) + ', neigh: ' + str(prev_node_visited) + ': ' + str(all_neighbours_visited))
            if all_neighbours_visited:
                if len(front[prev_node_id].prev_posts) >= 2:
                    print('decreased cnt')
                    exhausted_paths_count -= 1
                    counter_deleted += 1
                print('Node deleted: ' + str(prev_node_id) + ' n_posts: '+ str(len(front[prev_node_id].prev_posts)))
                del front[prev_node_id]
            print('node in front ' + str(prev_node_id) + ': ' + str(prev_node_id in front))


            #  check if the algorithm is finished
            print('total paths: ' + str(len(front)) + ', exhausted paths: ' + str(exhausted_paths_count))
            print('added: ' + str(counter_added) + ' Deleted:  ' + str(counter_deleted) +
                  ' Modified : ' + str(counter_modified) + ' Snapped : ' + str(counter_snapped))

            if exhausted_paths_count == len(front):
                print("All paths exhausted! Terminating the algorithm!")
                break

            # if time.time() - start_time >= 0.001:
            #      print("results:" + str(results))
            #      self.drawGraph(self.G, front, results, node_id_node_map)
            #      start_time = time.time()
            #      print("visited:" + str(visited_node_ids))


        print("Runtime: {}".format(time.time() - start_time))

        return results


    def __fist_step_alg(self, node_id_node_map_tmp, node_id_edge_map, start_node_id, eps_km):
        # front = [(start_node_id, 0, [])]
        node_id_node_map = copy.deepcopy(node_id_node_map_tmp)
        node_id_edge_map = copy.deepcopy(node_id_edge_map)
        front = {
            start_node_id: FrontData(0, [], [])
        }
        visited_node_ids = set()
        results = []
        start_time = time.time()

        visited_node_ids.add(start_node_id)


        while len(front) != 0:

            active_node_id = None
            prev_node_id = None
            current_visited_points = None  # TODO: do we need this in the loop??
            min_distance = math.inf

            for node_id, node_data in front.items():

                if node_id not in node_id_edge_map:
                    continue

                node_dist = node_data.origin_dist
                neigbours = node_id_edge_map[node_id]  # get neighbors od te tocke

                for neigbour in neigbours:
                    edge_dist = neigbours[neigbour]["weight"]
                    # najdi najblizjega soseda, ki se ni bil obiskan in je znotraj epsilona
                    if ((node_dist + edge_dist) < min_distance) and (neigbour not in visited_node_ids) and (node_dist + edge_dist) < eps_km and node_id_node_map[neigbour].post_id is None:
                        min_distance = node_dist + edge_dist
                        active_node_id = neigbour
                        current_visited_points = [val for val in node_data.prev_posts]
                        prev_node_id = node_id


            if active_node_id is None:
                # we were unable to find any new neighbours to extend the front
                # that means that we have searched through the entire graph
                # we can safely exit the loop
                print('Cannot extend the front. No neigbours available. Finishing search.')
                print(str(front))
                break

            if active_node_id not in node_id_node_map:
                raise ValueError('WTF!? Found an invalid node: ' + str(active_node_id))

            # check if the active node is a post office. if so, add it to the results
            is_post = node_id_node_map[active_node_id].post_id is not None
            if is_post:
                current_visited_points += [active_node_id]
                if len(current_visited_points) == 1:
                    results += [(node_id_node_map[active_node_id].post_id, min_distance)]


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

            # add the active node to the list of visited nodes
            visited_node_ids.add(active_node_id)

            # only add the active node to the front if it has any
            # non-visited neighbours
            active_node_neigh_ids = node_id_edge_map[active_node_id]
            all_neighbours_visited = True
            for neigh_id in active_node_neigh_ids:
                if neigh_id not in visited_node_ids:
                    all_neighbours_visited = False
                    break

            # if all the neighbours of the active node are visited, we need
            # to check if we can delete them now after one of their neighbours
            # (the active node) has been visited
            for neigh_id in active_node_neigh_ids:
                if neigh_id == prev_node_id or neigh_id not in front:
                    continue
                all_neigh_of_neigh_visited = True
                neigh_of_neigh_ids = node_id_edge_map[neigh_id]
                for neigh_of_neigh_id in neigh_of_neigh_ids:
                    if neigh_of_neigh_id not in visited_node_ids:
                        all_neigh_of_neigh_visited = False
                        break
                if all_neigh_of_neigh_visited:
                    if len(front[neigh_id].prev_posts) >= 2:
                        print('decreased cnt')
                    del front[neigh_id]
                    print('deleted neighbour of neighbour: ' + str(neigh_of_neigh_id))

            if not all_neighbours_visited:
                # add the node to the front
                front[active_node_id] = FrontData(
                    min_distance,
                    current_visited_points,
                    active_node_history
                )
                print("Added : "+ str(active_node_id) + " n_posts: " + str(len(current_visited_points)))


            # from the front
            # TODO: optimize this - have a counter in each node that counts
            # TODO: how many neighbours have been visited

            prev_node_neighbour_ids = node_id_edge_map[prev_node_id]
            all_neighbours_visited = True
            for neighbour_id in prev_node_neighbour_ids:
                if (node_id_node_map_tmp[neighbour_id].is_post and node_id_node_map_tmp[neighbour_id].node_id != start_node_id) or neighbour_id not in visited_node_ids:
                    all_neighbours_visited = False
                    break

            prev_node_visited = [(neigh_id, neigh_id in visited_node_ids) for neigh_id in prev_node_neighbour_ids]
            print('checking if node exhausted: ' + str(prev_node_id) + ', neigh: ' + str(prev_node_visited) + ': ' + str(all_neighbours_visited))
            if all_neighbours_visited:
                print('Node deleted: ' + str(prev_node_id) + ' n_posts: '+ str(len(front[prev_node_id].prev_posts)))
                del front[prev_node_id]
            print('node in front ' + str(prev_node_id) + ': ' + str(prev_node_id in front))



        print("Runtime: {}".format(time.time() - start_time))

        return (front, visited_node_ids)




    def search_near_posts(self, node_id_node_map_tmp, node_id_edge_map, start_node_id, eps_km):
        (front, visited_node_ids) = self.__fist_step_alg(node_id_node_map_tmp, node_id_edge_map, start_node_id, eps_km)
        return self.__second_step_alg(node_id_node_map_tmp, node_id_edge_map, front, visited_node_ids, eps_km/2)