import numpy as np
from modules.partitioning.k_means_sphere import k_means_sphere
from mpl_toolkits.mplot3d import Axes3D  # must be included to support 3D scatter
import matplotlib.pyplot as plt
from modules.partitioning.spectral import spectral_part
from modules.demo.mockup_graph import MockupGraph, Node, Edge
import json
import time

eps_rel = 1
threshold = 15
eps = threshold * eps_rel
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
shapes = ['.', 'v', '+', 'p', '*', 'p', '1', 'D']


class GraphParser:
    def __init__(self, path):
        self.path = path
        self.nodes = []
        self.edges = []
        self.raw_edges = []
        self._load_graph(path)
        self.matrix = []

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
        n  = len(self.nodes)
        self.matrix = np.zeros((n, n))
        node_map = {}
        for i in range(len(self.nodes)):
            node_map[self.nodes[i].id] = i

        for i in range(len(self.edges)):
            e = self.edges[i]
            idxA = node_map[e.start]
            idxB = node_map[e.end]
            if (e.start == 'A1' and e.end == 'A4') or (e.start == 'A4' and e.end == 'A1'):
                # print(e)
                print(e.start, e.end, e.cost)
            self.matrix[idxA, idxB] +=1
            self.matrix[idxB, idxA] +=1

            if self.matrix[idxA, idxB] > 2:
                self.matrix[idxA, idxB] = 2

            if self.matrix[idxB, idxA] > 2:
                self.matrix[idxB, idxA] = 2







graph = GraphParser('/home/mikroman/dev/ijs/coglo/src/modules/demo/data/slovenia.json')
graph.adjacency_matrix()
start_time = time.time()
A = graph.matrix


draw_sphere = False

k = 4

print(A.shape)
A = A - np.diag(np.diag(A))

#partition graph
assignment, Y = spectral_part(A, k)
Y_mean = np.mean(Y, 0)
norms = np.sqrt(np.sum(Y * Y, 1, keepdims=True))
Y_norm = Y / norms

d = Y.shape[1]  # column count

# plot graphs
print("Computation took {:3f}".format(time.time()-start_time))
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
if d == 2:
    for clustN in range(k):
        I_clust = np.full(len(graph.nodes), False)
        I_clust = assignment == int(clustN)


        clr = colors[clustN]
        shape = shapes[clustN]

        Yi = Y[I_clust, :]
        Yi_norm = Y_norm[I_clust, :]

        if draw_sphere:
            ax.scatter(Yi_norm[:, 0], Yi_norm[:, 1], c=clr)
        else:
            ax.scatter(Yi[:, 0], Yi[:, 1], c=clr)


    ax.scatter(Y_mean[0], Y_mean[1], marker='^')
elif d > 2:
    offset = 0

    for clustN in range(k):
        I_clust = np.full(len(graph.nodes), False)
        I_clust = assignment == int(clustN)


        clr = colors[clustN]
        shape = shapes[clustN]

        Yi = Y[I_clust, :]

        if draw_sphere:
            Yi_norm = Y_norm[I_clust, :]
            ax.scatter(Yi_norm[:, 0], Yi_norm[:, 1], Yi_norm[:, 2], c=clr)
        else:
            ax.scatter(Yi[:, 0], Yi[:, 1], Yi[:, 2], c=clr)


    ax.scatter(Y_mean[0], Y_mean[1], Y_mean[2], marker='^')
else:
    print('Invalid dimension')

plt.show()

print("Done")
