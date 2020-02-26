from collections import Set
import copy
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # must be included to support 3D scatter
import matplotlib.pyplot as plt
from modules.partitioning.spectral import spectral_part
from modules.demo.mockup_graph import Node, Edge
import json
import time
from tqdm import tqdm


class ClusterRender:
    def __init__(self):
        self.colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'tab:cyan', 'tab:pink', 'tab:purple']

    def render(self, nodes, assignment):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for i in range(len(nodes)):
            clustN = int(assignment[i])
            node = nodes[i]
            clr = self.colors[clustN]
            ax.scatter(node.lat, node.lon, c=clr)

        plt.show()


class GraphPartitioner:
    def __init__(self, path):
        self.path = path
        self.nodes = []
        self.edges = []
        self.raw_edges = []
        self._load_graph(path)
        self.matrix = []
        self.cluster_renderer = ClusterRender()
        self.adjacency_matrix()

    def _load_graph(self, path):
        with open(path, "r", encoding='UTF-8') as read_file:
            data = json.load(read_file)
            nodes = []
            edge_map = {}
            self.raw_edges = data["edge"]
            for n in data['nodes']:
                node = Node(data['nodes'][n])
                nodes.append(node)
                edge_map[node.id] = []

            edges = []
            for e in data["edge"]:
                edge = Edge(e, data["nodes"])
                edge_map[edge.start].append(edge)
                edges.append(edge)

        self.edges = edges
        self.nodes = nodes

    def adjacency_matrix(self):
        n = len(self.nodes)
        self.matrix = np.zeros((n, n))
        node_map = {}
        for i in range(len(self.nodes)):
            node_map[self.nodes[i].id] = i

        for i in range(len(self.edges)):
            e = self.edges[i]
            idxA = node_map[e.start]
            idxB = node_map[e.end]
            self.matrix[idxA, idxB] += 1

    def partition(self, count, show_plot=False):
        print('Running partitioning for', count, 'partitions on', len(self.nodes), 'nodes')
        start_time = time.time()
        A = self.matrix

        n_parts = count
        A = A - np.diag(np.diag(A))

        # partition graph
        assignments, Y = spectral_part(A, n_parts)

        # plot graphs
        print("Partitioning took {:3f}".format(time.time() - start_time))
        node_partitions = [[] for _ in range(n_parts)]
        edge_partitions = [set() for _ in range(n_parts)]

        if show_plot:
            self.cluster_renderer.render(self.nodes, assignments)

        for i in range(len(self.nodes)):
            clustN = int(assignments[i])
            node = self.nodes[i]
            node.cluster = clustN
            node_partitions[clustN].append(node)

        assert sum([len(x) for x in node_partitions]) == len(self.nodes)
        print('Partitions of size: ', [len(x) for x in node_partitions])
        print('Processing', len(self.edges), 'edges')

        copy_edges = self.edges.copy()
        for i, partition in enumerate(node_partitions):
            for edge in tqdm(copy_edges):
                start = edge.start
                end = edge.end
                added = False
                k = 0
                while k < len(partition) and not added:
                    n = partition[k]
                    if n.id == start:
                        start = None
                    elif n.id == end:
                        end = None
                    if start is None and end is None:
                        edge_partitions[i].add(edge)
                        reversed = copy.deepcopy(edge)
                        reversed.start = edge.end
                        reversed.end = edge.start
                        edge_partitions[i].add(reversed)
                        added = True
                    k += 1
            for item in edge_partitions[i]:
                if item in copy_edges:
                    copy_edges.remove(item)
        edge_partitions = [list(x) for x in edge_partitions]
        print('Input', len(self.edges), 'assigned', sum([len(x) for x in edge_partitions]))
        return node_partitions, edge_partitions


if __name__ == '__main__':
    graph = GraphPartitioner('/home/mikroman/dev/ijs/coglo/src/modules/demo/data/slovenia.json')

    node_parts, edge_parts = graph.partition(5, True)
