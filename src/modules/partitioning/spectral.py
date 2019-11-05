import numpy as np
from modules.partitioning.k_means_sphere import k_means_sphere

def cut_intensity(Q, part, n_part):
    n_vert = Q.shape[0]
    ones_k = np.ones((n_part, 1))
    P = np.zeros((n_vert, n_part))
    for partN in range(n_part):
        P[:, partN] = part == partN

    Q_p = P.T * Q * P
    c = ones_k.T * Q_p * ones_k - np.trace(Q_p)
    return c

def cut_size(Q, part, n_part):
    return cut_intensity((Q > 0).astype(dtype=int), part, n_part)

def spectral_part(Q, k):
    n = Q.shape[0]
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
        cut_sum = cut_intensity(Q, part, k)
        cut_edges = cut_size(Q, part, k)

        avg_cut_intens = cut_sum / cut_edges

        rnd_part = 1 + np.floor(k*np.random.rand((n,1)))
        rnd_cut_sum = cut_intensity(Q, rnd_part, k)
        avg_rnd_cut_intens = rnd_cut_sum / cut_edges
        rnd_cut_edges = cut_size(Q, rnd_part, k)
        mean_rnd_cut_intens = mean_rnd_cut_intens + (avg_rnd_cut_intens/total_tries)

        if cut_sum < best_cut:
            best_cut = cut_sum
            best_part = part

    return best_part, Y