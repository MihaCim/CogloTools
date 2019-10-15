import numpy as np
from modules.partitioning.k_means_sphere import kMeansSphere
from mpl_toolkits.mplot3d import Axes3D #must be included to support 3D scatter
import matplotlib.pyplot as plt

eps_rel = 1.5
threshold = 1
eps = threshold * eps_rel
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
shapes = ['.', 'v', '+', 'p', '*', 'p', '1', 'D']

sizes = [200, 200, 100, 100, 100]

draw_sphere = False

n = sum(sizes)
k = 3

A_orig = np.random.rand(n, n)
print(A_orig.shape)

prev_end = 0

for clusterN in range(len(sizes)):
    ni = sizes[clusterN]
    A_orig[prev_end:(ni + prev_end), prev_end:(ni + prev_end)] += threshold - 0.5 * eps
    prev_end = prev_end + ni

for i in range(n):
    A_orig[i, i] = 0

A = A_orig + eps * np.random.rand(n, n)
A = A - np.diag(np.diag(A))

A = 0.5 * (A + A.T)
A_norm = A / np.sum(A, 1, keepdims=True)  # for broadcast fix

L = np.eye(n) - A_norm

del A_orig, A, A_norm

[v, V] = np.linalg.eig(L)

I = np.argsort(v)
v = v[I]
V = V[:, I]
del I

X = V[:, 0:k]
Y = X[:, 1:]

Y_mean = np.mean(Y, 0)
norms = np.sqrt(np.sum(Y * Y, 1, keepdims=True))
Y_norm = Y / norms

assignment = kMeansSphere(Y_norm, k)

d = Y.shape[1]  # column count

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

if d == 2:
    offset = 0
    for real_clustN in range(len(sizes)):
        ni = sizes[real_clustN]
        for clustN in range(k):
            idxs_real_clust = np.arange(0, ni) + offset
            I_real_clust = np.full(n, False)
            I_real_clust[idxs_real_clust] = True
            I_clust = assignment == clustN
            I = np.logical_and(I_real_clust, I_clust)

            clr = colors[clustN]
            shape = shapes[clustN]

            Yi = Y[I, :]
            Yi_norm = Y_norm[I, :]

            if draw_sphere:
                ax.scatter(Yi_norm[:, 0], Yi_norm[:, 1], c=clr)
            else:
                ax.scatter(Yi[:, 0], Yi[:, 1], c=clr)

        offset += ni

    ax.scatter(Y_mean[0], Y_mean[1], marker='^')
elif d == 3:
    offset = 0
    for real_clustN in range(len(sizes)):
        ni = sizes[real_clustN]
        for clustN in range(k):
            idxs_real_clust = np.arange(0, ni) + offset
            I_real_clust = np.full(n, False)
            I_real_clust[idxs_real_clust] = True
            I_clust = assignment == clustN
            I = np.logical_and(I_real_clust, I_clust)

            clr = colors[clustN]
            shape = shapes[clustN]

            Yi = Y[I, :]
            Yi_norm = Y_norm[I, :]

            if draw_sphere:
                ax.scatter(Yi_norm[:, 0], Yi_norm[:, 1], Yi_norm[:, 2], c=clr)
            else:
                ax.scatter(Yi[:, 0], Yi[:, 1], Yi[:, 2], c=clr)

        offset += ni

    ax.scatter(Y_mean[0], Y_mean[1], Y_mean[2], marker='^')
else:
    print('Invalid dimension')

plt.show()

print("Done")
