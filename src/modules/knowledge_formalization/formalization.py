import scipy
import numpy as np
from scipy.sparse import linalg
from scipy.sparse import csr_matrix

# this class is used for extracting additional concepts from array of given concepts which shows extracted additional knowledge

# This method calculates neighbourhood from existing P matrices
# first parameter is P matrix, for example dump of wikipedia
# second parameter is a list of initial concepts (knowledge base)
# third parameter is p0 -
# fourth parameter is threshold t
def calc_neighbourhood(matrix_P):
    print len(matrix_P)


# create transition matrix from all concepts
def create_transition_matrix(concept_mappings):
    transition_row = []
    transition_col = []
    transition_values = []
    # go through concept mappings
    for concept_idx, mapping in concept_mappings.items():
        # possible transitions are in a mapping
        possible_transitions = len(mapping)

        # calculate transition possibility
        transition_possibility = 1.0 / possible_transitions

        # go through each transition
        for transition in mapping:
            transition_values.append(transition_possibility)
            transition_row.append(concept_idx)
            transition_col.append(transition)

    # create sparse matrix
    sparse = csr_matrix((transition_values, (transition_row, transition_col)))

    return sparse


# creates matrices
def create_initial_concept_transition_matrix(initial_concepts, all_concept_indices):
    transition_row = []
    transition_col = []
    transition_values = []

    # go through every initial concept
    for i in range(all_concept_indices):
        for j in range(all_concept_indices):

            if (i in initial_concepts):
                transition_values.append(1.0)
            else:
                transition_values.append(0)
            transition_row.append(j)
            transition_col.append(i)

    # create sparse matrix
    sparse = csr_matrix((transition_values, (transition_row, transition_col)))

    return sparse

if __name__ == '__main__':
    # TODO create parser for concepts
    # TODO fake all concepts
    all_concepts = {}
    all_concepts[1] = "car"
    all_concepts[2] = "house"
    all_concepts[3] = "monitor"
    all_concepts[4] = "mouse"
    all_concepts[5] = "cup"
    all_concepts[6] = "phone"
    all_concepts[7] = "computer"
    all_concepts[8] = "test"
    all_concepts[9] = "headphones"
    all_concepts[11] = "keyboard"

    # TODO create parser for mappings
    # TODO fake mappings
    concept_mappings = {}
    concept_mappings[0] = {1}
    concept_mappings[1] = {3, 1}
    concept_mappings[2] = {3, 5}
    concept_mappings[3] = {1, 2, 4, 5}
    concept_mappings[4] = {3, 11}
    concept_mappings[5] = {3, 8, 11}
    concept_mappings[6] = {11}
    concept_mappings[7] = {11}
    concept_mappings[8] = {5, 9, 11}
    concept_mappings[9] = {8}
    concept_mappings[10] = {8}
    concept_mappings[11] = {4, 5, 6, 7}

    # TODO create parser for initial concepts
    # TODO fake concepts
    initial_concepts = [3]

    # create transition matrix
    matrix_P = create_transition_matrix(concept_mappings)
    # print "===================================="
    # print matrix_P

    # create matrix that contains transition probabilities from each concept back to initial concept
    all_concept_indices = len(concept_mappings)
    matrix_J = create_initial_concept_transition_matrix(initial_concepts, all_concept_indices)
    # print "===================================="
    # print matrix_J.todense()

    alfa = 0.2  # reset probability
    k = 1  # number of initial concepts

    P1 = csr_matrix(((1 - alfa) * matrix_P) + ((alfa / float(k)) * matrix_J))
    # print "===================================="
    print P1.todense()

    # simulation
    # extract eigen values and eigen vectors
    [eigenvalues, vectors] = linalg.eigs(P1.transpose(), k, None, None, 'LM')
    print [eigenvalues, vectors]

    # only keep real value
    real = vectors.real

    t = 0.2  # minimum part of time that walker is in the node, for the node to be considered neighbour

    # check if any EigenVector real value is the same or larger than t - this node is neighbour
