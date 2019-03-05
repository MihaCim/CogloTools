import numpy as np


def get_graph():
    return np.array([[0, 2, 0, 0, 0],
                     [0, 0, 3, 0.2, 0],
                     [1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 2, 0]])


def make_symmetric(A):
    return 0.5 * (A + A.T)


def make_laplace_matrix(A):
    return np.diag(A.sum(axis=1))


if __name__ == '__main__':
    A = get_graph()
    print(A)

    A_sim = make_symmetric(A)

    print(A_sim)

    L_mat = make_laplace_matrix(A_sim)

    print(L_mat)

    e_vals, e_vecs = np.linalg.eigh(L_mat)

    print(e_vals)
    print(e_vecs)
