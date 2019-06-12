import scipy

from scipy.sparse import csr_matrix
import numpy as np

def laplace_mat(A_spmat):
    '''
    Returns the Laplace matrix of the given adjacency matrix A.
    '''
    nvert = A_spmat.get_shape()[0]

    range_n = scipy.array(range(nvert))
    ones_n = scipy.array([1 for _ in range_n])

    # d <- A*1
    diag_vec = csr_matrix.dot(A_spmat, ones_n)
    # D <- diag(d)
    deg_spmat = csr_matrix((diag_vec, (range_n, range_n)), shape=(nvert, nvert))

    # L <- D - A
    laplace_spmat = (deg_spmat - A_spmat)
    # convert L doubles (if the matrix is already
    # a floating point type, the call only returns a reference
    # to self)
    laplace_spmat = laplace_spmat.asfptype()

    return laplace_spmat

def cut_size(A_spmat, partitions):
    nvert = A_spmat.get_shape()[0]

    cut = 0.0
    for part1 in partitions:
        p1 = np.zeros(nvert)
        for vert_id in part1:
            p1[vert_id] = 1
        not_p1 = np.ones(nvert) - p1

        Ay = csr_matrix.dot(A_spmat, not_p1)
        cut += np.dot(p1, Ay)

    return cut

def cut_size_undirected(A_spmat, partitions):
    return 0.5*cut_size(A_spmat, partitions)
