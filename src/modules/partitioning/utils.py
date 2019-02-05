import scipy
from scipy.sparse import csr_matrix

def laplace_mat(A_spmat):
    '''
    Returns the Laplace matrix of the given adjacency matrix A.
    '''
    nvert = A_spmat.get_shape()[0]

    range_n = scipy.array(range(nvert))
    ones_n = scipy.array([1 for _ in range_n])

    # d <- A*1
    diag_vec = csr_matrix.dot(A_spmat, ones_n)
    print('diag vec: ' + str(diag_vec))
    print('diag len: ' + str(len(diag_vec)))
    # D <- diag(d)
    deg_spmat = csr_matrix((diag_vec, (range_n, range_n)), shape=(nvert, nvert))
    print('deg spmat: ' + str(deg_spmat))

    # L <- D - A
    laplace_spmat = (deg_spmat - A_spmat)
    # convert L doubles (if the matrix is already
    # a floating point type, the call only returns a reference
    # to self)
    laplace_spmat = laplace_spmat.asfptype()
    print('laplace matrix: ' + str(laplace_spmat.todense()))

    return laplace_spmat
