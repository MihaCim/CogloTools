import numpy as np


def discretesample(p, n):
    """independently draws n samples (with replacement) from the
        distribution specified by p, where p is a probability array
        whose elements sum to 1."""
    return np.random.choice(len(p), n, p=p)


def similarity(x1, x2):
    norm_x1 = np.linalg.norm(x1)
    norm_x2 = np.linalg.norm(x2)
    return np.dot(x1, x2) / (norm_x1 * norm_x2)


def calc_centroid(X):
    return np.mean(X, 0)


def count_diff(a, prev_a):
    diff = np.abs(a - prev_a)
    diff[diff > 1] = 1

    return np.sum(diff)


def k_means_sphere(X, k, max_iter=100):
    #kmeans++ init
    n = X.shape[0]
    d = X.shape[1]

    def kmeanspp(_X, _k):
        n_inst = _X.shape[0]
        dim = _X.shape[1]

        #select initial centroids
        C = np.zeros((_k, dim))  # k++ means
        rands = np.random.randint(0, n_inst)
        C[0, :] = _X[rands]

        probs = np.zeros(n_inst)

        for centroidN in range(1, _k):
            # compute probabilities for new ctroid
            for recN in range(0, n_inst):
                rec = _X[recN, :]

                # compute distance to nearest centroid
                nearest_dist = np.inf
                for exist_centroidN in range(0, centroidN):
                    centroid = C[exist_centroidN, :]
                    clust_rec_sim = similarity(rec, centroid)
                    clust_rec_dist = 0.5 * (1 - clust_rec_sim)

                    if clust_rec_dist < nearest_dist:
                        nearest_dist = clust_rec_dist
                # the probability is proportional to d^2
                probs[recN] = nearest_dist * nearest_dist
            norm_factor = 1.0 / np.sum(probs)
            probs = probs * norm_factor

            chosenN = discretesample(probs, 1)[0]
            C[centroidN, :] = _X[chosenN, :]

            print('Chosen centroid {}, probability: {}, max probability: {} '.format(chosenN, probs[centroidN],
                                                                                     probs.max()))
        return C

    C = kmeanspp(X, k)
    prev_assignment = np.zeros(n)
    assignment = np.zeros(n)

    change = True
    iterN = 0

    while change and iterN < max_iter:
        iterN += 1

        lost_centroid = True

        while lost_centroid:
            lost_centroid = False

            # assign vectors
            for recN in range(0, n):
                xi = X[recN, :]

                best_idx = -1
                best_sim = np.NINF

                for clustN in range(0, k):
                    sim = similarity(xi, C[clustN, :])

                    if sim > best_sim:
                        best_idx = clustN
                        best_sim = sim

                assignment[recN] = best_idx

            # recompute centroids
            for clustN in range(0, k):

                assigned_idxs = assignment == clustN

                if assigned_idxs.astype(dtype=int).sum() > 0:
                    Yn = X[assigned_idxs, :]
                    C[clustN, :] = calc_centroid(Yn)
                else:
                    C = kmeanspp(X, k)
                    lost_centroid = True
                    print("Lost a centroid, reinitialized at {}".format(iterN))

        diff = count_diff(assignment, prev_assignment)
        change = diff > 0
        tmp = prev_assignment
        prev_assignment = assignment
        assignment = tmp

    return assignment
