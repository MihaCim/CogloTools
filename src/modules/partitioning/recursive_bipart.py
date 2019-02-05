import scipy
import numpy as np
import scipy.sparse.linalg as sla
from scipy.sparse import csr_matrix
from math import floor, ceil

from modules.partitioning.module import Partitioning
from modules.partitioning.constants import tol_la
import modules.partitioning.utils as utils

class RecursiveBipart(Partitioning):

    def init(self):
        pass

    def partition(self, adj_spmat, k, balance_eps):
        return self._bipartition(adj_spmat, balance_eps)

    def _bipartition(self, adj_spmat, balance_eps):
        nvert = adj_spmat.get_shape()[0]
        print('adj spmat: ' + str(adj_spmat))

        # check edge cases
        if nvert <= 2:
            return [[partN] for partN in range(nvert)]

        laplace_spmat = utils.laplace_mat(adj_spmat)

        # compute the eigenvectors and eigenvalues
        eigvals, eigvec_mat = sla.eigsh(laplace_spmat, which="SM", k=2)
        print('eigenvals: ' + str(eigvals))
        assert abs(eigvals[0]) < tol_la

        # check all thresholds in range and select the best one
        eigvec2 = eigvec_mat[:, 1]
        thresholds = [val for val in eigvec2]
        thresholds.sort()

        print("eigvec2: " + str(eigvec2))

        minN = -1
        min_cut = float('inf')

        expected_part_size = 0.5*float(nvert)
        min_part_size = floor((1 - balance_eps)*expected_part_size)
        max_part_size = ceil((1 + balance_eps)*expected_part_size)

        print('min part size: ' + str(min_part_size) + ", max_part_size: " + str(max_part_size))

        startN = int(max(1, min_part_size))
        endN = int(min(nvert-1, max_part_size))
        for thresholdN in range(startN, endN+1):
            threshold = thresholds[thresholdN]
            part_vec = scipy.array([-1 if val < threshold else 1 for val in eigvec2])
            cut_size = RecursiveBipart._calc_cutX4(laplace_spmat, part_vec)

            print('tn: ' + str(thresholdN) + ", t: " + str(threshold) + ", x: " + str(part_vec) + " cut size: " + str(cut_size / 4))

            if cut_size < min_cut:
                min_cut = cut_size
                minN = thresholdN

        assert minN != -1
        threshold = thresholds[minN]
        partitions = [[], []]
        for valN, val in enumerate(eigvec2):
            if val < threshold:
                partitions[0].append(valN)
            else:
                partitions[1].append(valN)

        return partitions

    @staticmethod
    def _calc_cutX4(laplace_spmat, part_vec):
        '''
        The method calculates and returns 4 times the size of the cut from
        a partition vector.
        '''
        # x'Lx = 4w(E(P1, P2))
        Lx = csr_matrix.dot(laplace_spmat, part_vec)
        cut_x4 = np.dot(part_vec, Lx)
        return cut_x4

    @staticmethod
    def cut_size(A_spmat, partitions):
        nvert = A_spmat.get_shape()[0]
        L = utils.laplace_mat(A_spmat)
        # TODO: for now only two partitions are supported
        assert len(partitions) == 2
        part_sets = [set(part) for part in partitions]
        x = scipy.array([-1 if val in part_sets[0] else 1 for val in range(nvert)])
        cut_x4 = RecursiveBipart._calc_cutX4(L, x)
        return 0.25*cut_x4
