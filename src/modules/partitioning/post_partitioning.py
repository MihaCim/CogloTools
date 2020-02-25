import numpy as np
from modules.partitioning.k_means_sphere import k_means_sphere
from mpl_toolkits.mplot3d import Axes3D  # must be included to support 3D scatter
import matplotlib.pyplot as plt
from modules.partitioning.spectral import spectral_part
from modules.demo.mockup_graph import Node, Edge
import json
import time


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


class GraphParser:
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
        start_time = time.time()
        A = self.matrix

        n_parts = 10
        A = A - np.diag(np.diag(A))

        # partition graph
        assignments, Y = spectral_part(A, n_parts)

        # plot graphs
        print("Partitioning took {:3f}".format(time.time() - start_time))
        partitions = [[] for _ in range(n_parts)]

        if show_plot:
            self.cluster_renderer.render(self.nodes, assignments)

        for i in range(len(graph.nodes)):
            clustN = int(assignments[i])
            node = graph.nodes[i]
            node.cluster = clustN
            partitions[clustN].append(node)

        assert sum([len(x) for x in partitions]) == len(graph.nodes)
        return partitions


if __name__ == '__main__':
    graph = GraphParser('/home/mikroman/dev/ijs/coglo/src/modules/demo/data/slovenia.json')

    partitions = graph.partition(5, True)
