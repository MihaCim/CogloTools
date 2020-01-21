import copy
import math
import time

import matplotlib.pyplot as plt
import networkx as nx
from pojo.front_data import FrontData


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

    #return self.__second_step_alg(node_id_node_map_tmp, node_id_edge_map, origin_node_id)
    def __second_step_alg(self, node_id_node_map_temp, node_id_edge_map, origin_node_id):
        front = {
            origin_node_id: FrontData(0, [] )
        }
        node_id_node_map = copy.deepcopy(node_id_node_map_temp)
        node_id_edge_map = copy.deepcopy(node_id_edge_map)


        visited_node_ids = set()
        results = []

        visited_node_ids.add(origin_node_id)
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
            current_visited_post_ids = None  # TODO: do we need this in the loop??
            min_distance = math.inf

            # The FRONT: this loop finds the node that is closest to the front
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
                        current_visited_post_ids = [val for val in node_data.prev_posts]
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
            #print('active node: ' + str(active_node_id))

            if active_node_id not in node_id_node_map:
                raise ValueError('Found an invalid node: ' + str(active_node_id))

            # check if the active node is a post office. if so, add it to the results

             #is_post = node_id_node_map[active_node_id].post_id is not None      ##check the
             #is_post = active_node_id.isTagged is not None  ##check the
             #if is_post:
             #   current_visited_post_ids += [active_node_id]
             #   if len(current_visited_post_ids) == 1:
             #       results += [(node_id_node_map[active_node_id].post_id, min_distance)]

            # check if the active node is a post office. if so, add it to the results
            is_post = node_id_node_map[active_node_id].is_empty_tagged()
            if is_post and not  node_id_node_map[active_node_id].isTaggedby(origin_node_id):
                current_visited_post_ids += [active_node_id]

                if len(current_visited_post_ids) == 1:
                    results += [(node_id_node_map[node_id_node_map[active_node_id].tag_filter()].post_id, min_distance)]

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
            # (the active node) has been visited - Handling the use case when cycle/loop has been reached for two edges

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

            # adding nodes to the front
            if not all_neighbours_visited:
                # add the node to the front
                front[active_node_id] = FrontData(
                    min_distance,
                    current_visited_post_ids
                )
                print("Added : " + str(active_node_id) + " n_posts: " + str(len(current_visited_post_ids)))
                if len(current_visited_post_ids) >= 2:
                    print('increased cnt')
                    exhausted_paths_count += 1
                    counter_added += 1

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

            # delete the nodes that have all the neighbours visited
            if all_neighbours_visited:
                if len(front[prev_node_id].prev_posts) >= 2:
                    print('decreased cnt')
                    exhausted_paths_count -= 1
                    counter_deleted += 1
                print('Node deleted: ' + str(prev_node_id) + ' n_posts: ' + str(len(front[prev_node_id].prev_posts)))
                del front[prev_node_id]

            #  check if the algorithm is finished
            # print('total paths: ' + str(len(front)) + ', exhausted paths: ' + str(exhausted_paths_count))
            # print('added: ' + str(counter_added) + ' Deleted:  ' + str(counter_deleted) +
            #      ' Modified : ' + str(counter_modified) + ' Snapped : ' + str(counter_snapped))

            # when there is more than one post office on in all direction, the search can be terminated
            if exhausted_paths_count == len(front):
                print("All paths exhausted! Terminating the algorithm!")
                break

        print("Runtime: {}".format(time.time() - start_time))
        return results

    def __fist_step_alg(self, node_id_node_map, node_id_edge_map, start_node_id, origin_node_id, eps_km):
        # front = [(start_node_id, 0, [])]
        F = [(start_node_id, 0)]
        visited_ids = set()

        while len(F) > 0:
            current_tup = F.pop(0)
            current_id = current_tup[0]
            current_dist = current_tup[1]
            edge_map = node_id_edge_map[current_id]  # get neighbors od te tocke
            for neighbour_id in edge_map:
                current_neighbour_dist = node_id_edge_map[current_id][neighbour_id]['weight']
                if neighbour_id in visited_ids:
                    continue
                if current_dist + current_neighbour_dist > eps_km:
                    continue
                F.append((neighbour_id, current_dist + current_neighbour_dist))
            visited_ids.add(current_id)
            current_node = node_id_node_map[current_id]
            if not current_node.isTaggedby(origin_node_id):
                current_node.addTag((start_node_id, current_dist))
            ##potrebno še pobrisati vse tage razen najbližjega
            # node_tags = current_node
            print(current_node)

    def search_near_posts(self, node_id_node_map, node_id_edge_map, origin_node_id,map_posts_to_nodes, eps_km):
        self.__fist_step_alg(node_id_node_map, node_id_edge_map, origin_node_id, origin_node_id, eps_km)
        for node_id in map_posts_to_nodes:
            if map_posts_to_nodes[node_id]!= origin_node_id:
                self.__fist_step_alg(node_id_node_map, node_id_edge_map, map_posts_to_nodes[node_id], origin_node_id, eps_km)
        return self.__second_step_alg(node_id_node_map, node_id_edge_map, origin_node_id)
