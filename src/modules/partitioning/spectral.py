import numpy as np
from modules.partitioning.k_means_sphere import k_means_sphere


def cut_intensity(Q, part, n_part):
    n_vert = Q.shape[0]
    ones_k = np.ones((n_part, 1))
    P = np.zeros((n_vert, n_part))
    for partN in range(n_part):
        P[:, partN] = part == partN

    Q_p = np.dot(np.dot(P.T, Q), P)
    c = np.dot(np.dot(ones_k.T, Q_p), ones_k) - np.trace(Q_p)
    return c

def spectral_part(Q, k):
    """
        % A spectral partitoning algorithm that
    % splits a graph into k partitions by
    % approximating the minimal cut.
    %
    % The graph is represented as an intensity
    % matrix Q. An edge (Q)_ij is the rate of
    % going from node i to node j.
    %
    % The method returns a vector of assignments
    % a where a_i is the index of the parition
    % to which the i-th element was assigned.

    """
    n = Q.shape[0]
    ones_n = np.ones((n, 1))

    # symmetrize to ensure real eigen vals
    Q = 0.5 * (Q + Q.T)
    Q_norm = Q / np.sum(Q, 1, keepdims=True)  # for broadcast fix

    # compute Laplace matrix
    L = np.eye(n) - Q_norm

    # calc eigenvectors
    [v, V] = np.linalg.eig(L)

    # sorting eigenvals and vecs
    I = np.argsort(v)
    V = V[:, I]
    del I

    # create datase Y, each row is a feature vector for associated node in graph
    X = V[:, 0:k]
    Y = X[:, 1:]

    norms = np.sqrt(np.sum(Y * Y, 1, keepdims=True))
    Y_norm = Y / norms

    best_part = 0
    best_cut = np.inf

    total_tries = 10  # attempt multiple tries to get best clustering - due to randomness
    for i in range(total_tries):
        part = k_means_sphere(Y_norm, k, 200)

        # clustering evaluation
        cut_sum = cut_intensity(Q, part, k)

        if cut_sum < best_cut:
            print('Got better clustering in try', i)
            best_cut = cut_sum
            best_part = part

    return best_part, Y
