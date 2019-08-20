from abc import abstractmethod

class Partitioning:

    def init(self):
        pass

    @abstractmethod
    def partition(self, A_spmat, k, balance_eps):
        '''
        Partitions the graph represented by the adjacency matrix
        A_spmat into k partitions each of which has the number of
        vertices in range floor((1-eps)*n/k) <= n_k <= ceil((1+eps)*n/k).
        '''
        pass
