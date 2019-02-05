from scipy.sparse import csr_matrix

from modules.partitioning.recursive_bipart import RecursiveBipart

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

cut_size = RecursiveBipart.cut_size(A, partitions)
assert cut_size == 1

print("partitions: " + str(partitions))

# TODO: convert to unit test
