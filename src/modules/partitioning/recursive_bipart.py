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
        nvert = adj_spmat.get_shape()[0]
        return self._partition(adj_spmat, range(nvert), k, balance_eps)

    def _partition(self, adj_spmat, vert_ids, k, balance_eps):
        if k == 1:
            return [vert_ids]

        bi_part = self._bipartition(adj_spmat, vert_ids, balance_eps)

        partN_large = 0 if len(bi_part[0]) >= len(bi_part[1]) else 1
        partN_small = 1 - partN_large

        vert_ids_large = bi_part[partN_large]
        vert_ids_small = bi_part[partN_small]

        k_large = ceil(0.5*k)
        k_small = floor(0.5*k)

        part_large = self._partition(adj_spmat, vert_ids_large, k_large, balance_eps)
        part_small = self._partition(adj_spmat, vert_ids_small, k_small, balance_eps)

        return part_large + part_small

    def _bipartition(self, graph_adj_spmat, vert_ids, balance_eps):
        nvert = len(vert_ids)

        # check edge cases
        if nvert <= 2:
            return [[partN] for partN in range(nvert)]

        # extract the submatrix
        adj_spmap = graph_adj_spmat[vert_ids, :][:, vert_ids]

        laplace_spmat = utils.laplace_mat(adj_spmap)

        # compute the eigenvectors and eigenvalues
        eigvals, eigvec_mat = sla.eigsh(laplace_spmat, which="SM", k=2)
        assert abs(eigvals[0]) < tol_la

        # check all thresholds in range and select the best one
        eigvec2 = eigvec_mat[:, 1]
        thresholds = [val for val in eigvec2]
        thresholds.sort()

        minN = -1
        min_cut = float('inf')

        expected_part_size = 0.5*float(nvert)
        min_part_size = floor((1 - balance_eps)*expected_part_size)
        max_part_size = ceil((1 + balance_eps)*expected_part_size)

        startN = int(max(1, min_part_size))
        endN = int(min(nvert-1, max_part_size))
        for thresholdN in range(startN, endN+1):
            threshold = thresholds[thresholdN]
            part_vec = scipy.array([-1 if val < threshold else 1 for val in eigvec2])
            cut_size = RecursiveBipart._calc_cutX4(laplace_spmat, part_vec)

            if cut_size < min_cut:
                min_cut = cut_size
                minN = thresholdN

        assert minN != -1
        threshold = thresholds[minN]
        partitions = [[], []]
        for valN, val in enumerate(eigvec2):
            vertex_id = vert_ids[valN]
            if val < threshold:
                partitions[0].append(vertex_id)
            else:
                partitions[1].append(vertex_id)

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
