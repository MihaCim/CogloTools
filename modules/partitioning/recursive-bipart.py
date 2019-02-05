import numpy as np
import scikit.sparse.linalg as spla
from scikit.sparse import csr_matrix


from partitioning.module import Partitioning

class RecursiveBipart(Partitioning):

    def init(self):
        pass

    def partition(self, adj_spmat):
        n_vert = adj_spmat.get_shape()[0]

        range_n = np.array(range(n_vert))
        ones_n = np.array([1 for _ in range_n])

        diag_vec = adj_spmat.multiply(ones_n)
        deg_spmat = csr_matrix((diag_vec, (range_n, range_n)))

        laplace_spmat = deg_spmat - adj_spmat
        print('laplace matrix: ' + str(laplace_spmat.toarray()))

        # compute the eigenvectors and eigenvalues
        eigvals, eigvec_mat = spla.eigs(laplace_spmat, 2)
        print('eigenvals: ' + str(eigvals))

        # TODO: check different thresholds to find the best partition

        eigvec = eigvec_mat[:, 1]
        thresholds = [val for val in eigvec]
        thresholds.sort()

        print('thresholds: ' + str(thresholds))

        pass
