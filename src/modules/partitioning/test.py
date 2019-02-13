import unittest

from scipy.sparse import csr_matrix

from modules.partitioning.recursive_bipart import RecursiveBipart
from modules.partitioning.utils import cut_size_undirected

class TestRecBipartition(unittest.TestCase):

    def test_bipartition(self):
        A = csr_matrix([
            [0, 2, 4, 0, 0, 0],
            [2, 0, 3, 1, 0, 0],
            [4, 3, 0, 0, 0, 0],
            [0, 1, 0, 0, 2, 4],
            [0, 0, 0, 2, 0, 3],
            [0, 0, 0, 4, 3, 0]
        ])

        part = RecursiveBipart()
        partitions = part.partition(A, 2, balance_eps=0.1)
        cut = cut_size_undirected(A, partitions)

        self.assertEqual(cut, 1)

    def test_tripartition(self):
        A = csr_matrix([
            [0, 1, 2, 0, 0, 0, 0, 0, 0, 1, 0],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 1, 0, .5, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, .5, 0, 2, 3, 0, 0, 0, 0, 0],
            [0, 0, 0, 2, 0, 4, 0, 0, 0, 0, 0],
            [0, 0, 0, 3, 4, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 2, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 2, 0, 4, 0, 3],
            [0, 0, 0, 0, 0, 0, 0, 4, 0, 2, 3],
            [1, 0, 0, 0, 0, 0, 3, 0, 2, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0],
        ])

        part = RecursiveBipart()
        partitions = part.partition(A, 3, balance_eps=0.1)

        cut = cut_size_undirected(A, partitions)

        self.assertEqual(cut, 2.5)

    def test_tripartition2(self):
        A = csr_matrix([
            [0, 1, 2, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [2, 1, 0, .5, 0, 0, 0, 0, 0, 0],
            [0, 0, .5, 0, 2, 3, 0, 0, 0, 0],
            [0, 0, 0, 2, 0, 4, 0, 0, 0, 0],
            [0, 0, 0, 3, 4, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 2, 0, 3],
            [0, 0, 0, 0, 0, 0, 2, 0, 4, 0],
            [0, 0, 0, 0, 0, 0, 0, 4, 0, 2],
            [1, 0, 0, 0, 0, 0, 3, 0, 2, 0]
        ])

        part = RecursiveBipart()
        partitions = part.partition(A, 3, balance_eps=0.1)

        cut = cut_size_undirected(A, partitions)

        self.assertEqual(cut, 2.5)


if __name__ == "__main__":
    unittest.main()
