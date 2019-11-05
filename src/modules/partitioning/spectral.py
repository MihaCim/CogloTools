import numpy as np
from modules.partitioning.k_means_sphere import k_means_sphere

def spectral_part(Q, k):
    n = Q.shape[1]
    ones_n = np.ones((n, 1))

    Q = 0.5 * (Q + Q.T)
    Q_norm = Q / np.sum(Q, 1, keepdims=True)  # for broadcast fix

    L = np.eye(n) - Q_norm
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

    best_part = 0
    best_cut = np.inf

    total_intensity = ones_n.T * Q * ones_n
    total_edges = ones_n.T * (Q > 0).astype(dtype=int) * ones_n

    mean_rnd_cut_intens = 0

    total_tries = 10
    for _ in range(total_tries):
        part = k_means_sphere(Y_norm, k, 200)
        return part, Y