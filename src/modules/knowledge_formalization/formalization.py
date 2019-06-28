import operator
import numpy as np

import os
from scipy.sparse import linalg
from scipy.sparse import csr_matrix
from scipy import sparse
import pickle as pickle

from collections import defaultdict


# create transition matrix from all concepts
def create_transition_matrix(transitions_map, matrix_dimension):
    print("creating transition matrix P of dimension", matrix_dimension, "x", matrix_dimension)
    transition_row = []
    transition_col = []

    # go through concept mappings
    id = 0
    counter = 0
    for concept_idx in transitions_map:
        transitions = transitions_map[concept_idx]
        transition_row.extend([concept_idx] * len(transitions))
        transition_col.extend(transitions)

        id = id + len(transitions)
        counter = counter + 1
        if counter % 10000 == 0:
            print("at counter", counter, "current ID is", id)

    print("creating transition values vector")
    transition_values = np.ones(len(transition_col), dtype=float)
    print("transition values vector created")

    print("transition values length", len(transition_values))
    print("transition row length", len(transition_row))
    print("transition col length", len(transition_col))
    print("matrix dimension", matrix_dimension, "x", matrix_dimension)

    # create sparse matrix Q that contains ones for each transition from A->B and B->A
    print("creating matrix Q")
    matrix_Q = csr_matrix((transition_values, (transition_row, transition_col)), (matrix_dimension, matrix_dimension))
    print(matrix_Q.shape)
    print("matrix Q created")

    # column vector of ones
    print("creating vector I")
    vector_I = np.ones((matrix_dimension, 1), dtype=float)
    print("vector I created")

    # 1D vector that contains the number of transitions in each row
    qi = matrix_Q * vector_I

    for rowN in range(len(qi)):
        value = qi[rowN]
        if value == 0:
            print("Value in row", rowN, "is 0!")

    # create reciprocal matrix and transpose it
    reciprocal_transposed = np.transpose(np.reciprocal(qi))[0, :]

    # create diagonal matrix
    reciprocal_range = range(matrix_dimension)
    print("creating diagonal sparse matrix")
    sparse_diagonal_matrix = csr_matrix((reciprocal_transposed, (reciprocal_range, reciprocal_range)),
                                        (matrix_dimension, matrix_dimension))
    print("diagonal sparse matrix created")

    # get P matrix as a product of Q nad diagonal(inverse(Q * I))
    print("creating P matrix")
    matrix_P = csr_matrix((sparse_diagonal_matrix * matrix_Q), (matrix_dimension, matrix_dimension))
    print("matrix P created")

    return matrix_P


# creates matrices
def create_initial_concept_transition_matrix(initial_concepts, all_concepts, matrix_dimension):
    print("creating initial concept transition matrix J")
    transition_row = []
    transition_col = []

    # go through every initial concept
    for colN in initial_concepts:
        transition_col.extend([colN] * len(all_concepts))
        transition_row.extend(all_concepts)

    print("creating transition values vector")
    transition_values = np.ones(len(transition_col), dtype=float)
    print("transition values vector created")

    print(len(transition_row))
    print(len(transition_col))
    print(len(transition_values))

    # create sparse matrix
    sparse = csr_matrix((transition_values, (transition_row, transition_col)), (matrix_dimension, matrix_dimension))
    print(sparse.shape)
    print("matrix J created")

    return sparse


# normalizes data (0 - 1)
def normalize_data(array):
    return (array - array.min()) / (array.max() - array.min())


# check if value is close enough to given value (used for comparing float values)
def is_close(a, b, rel_tol=1e-07, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


# method calculates neighbourhood based on concept mappings and initial concepts
def calc_neighbourhood(matrix_dimension,
                       new_old_index_array,
                       id_to_concept_mapping,
                       concept_mappings,
                       initial_concepts,
                       matrix_P,
                       number_of_wanted_concepts,
                       alfa):
    # create matrix that contains transition probabilities from each concept back to initial concept
    matrix_J = create_initial_concept_transition_matrix(initial_concepts, concept_mappings, matrix_dimension)

    k = len(initial_concepts)  # number of initial concepts

    print("creating P1 matrix from matrix P and matrix J")
    matrix_P1 = csr_matrix(((1 - alfa) * matrix_P) + ((alfa / float(k)) * matrix_J))
    print("matrix P1 created")

    # simulation
    # extract EigenValues and EigenVectors
    print("extracting eigenvalues and eigenvectors")
    [eigenvalues, vectors] = linalg.eigs(matrix_P1.transpose(), k, None, None, 'LM')

    # extract only the column where EigenValue is 1.0
    print("extracting column of eigenvectors where eigenvalue is 1")
    resultArrayIdx = -1
    for eigenValueIdx in range(len(eigenvalues)):
        value = eigenvalues[eigenValueIdx].real

        if is_close(value, 1.0):
            resultArrayIdx = eigenValueIdx
            break
    if resultArrayIdx == -1:
        print("No EigenValue 1.0 in received eigenvalues. Exiting program...")
        exit(3)
    print("extracted eigenvectors successfully")

    # only keep real value
    print("converting vectors to keep only real values")
    resultArray = vectors.real

    # normalize data from column with index resultArrayIdx because that column represents our results
    print("normalizing data")
    normalizedArray = normalize_data(resultArray.T[resultArrayIdx])
    print("data normalized")

    print("creating array of similar concepts")
    similar_concepts = {}
    for concept_id in range(len(normalizedArray.T)):
        value = normalizedArray.T[concept_id]

        # if ID is not the same as initial concept, extract the value
        if concept_id not in initial_concepts:
            similar_concepts[concept_id] = value

    # sort descending - most similar concept is the highest
    print("sorting array of similar concepts descdending by probability")
    sorted_similar_concepts = sorted(similar_concepts.items(), key=operator.itemgetter(1), reverse=True)
    print(sorted_similar_concepts)

    # TODO extract a word from wikipedia dictionary that was build in the beginning of the program


# method extracts concepts IDs and creates new dictionary from them, if dump doesn't exist yet. if dump exists,
# it just reads it from a dump file
def create_concept_ids(DEFAULT_CONCEPT_FILE,
                       NEW_OLD_ID_MAPPING_DUMP_PATH,
                       OLD_NEW_ID_MAPPING_DUMP_PATH,
                       ID_CONCEPT_MAPPING_PICKLE_DUMP_PATH):
    new_id_to_concept_mapping = {}
    new_old_index_array = []
    old_new_index_dict = {}

    if os.path.isfile(ID_CONCEPT_MAPPING_PICKLE_DUMP_PATH) and os.path.isfile(
            NEW_OLD_ID_MAPPING_DUMP_PATH) and os.path.isfile(OLD_NEW_ID_MAPPING_DUMP_PATH):

        # try opening concepts file dump and if it doesn't exist, try opening the file and construct dump from it
        print("concept file PICKLE dumps exist")

        print("opening file", NEW_OLD_ID_MAPPING_DUMP_PATH)
        new_old_index_array = pickle.load(open(NEW_OLD_ID_MAPPING_DUMP_PATH, "rb"))
        print("file", NEW_OLD_ID_MAPPING_DUMP_PATH, "read")

        print("opening file", ID_CONCEPT_MAPPING_PICKLE_DUMP_PATH)
        new_id_to_concept_mapping = pickle.load(open(ID_CONCEPT_MAPPING_PICKLE_DUMP_PATH, "rb"))
        print("file", ID_CONCEPT_MAPPING_PICKLE_DUMP_PATH, "read")

        print("opening file", OLD_NEW_ID_MAPPING_DUMP_PATH)
        old_new_index_dict = pickle.load(open(OLD_NEW_ID_MAPPING_DUMP_PATH, "rb"))
        print("file", OLD_NEW_ID_MAPPING_DUMP_PATH, "read")

    elif os.path.isfile(DEFAULT_CONCEPT_FILE):
        print("using default concept file path", DEFAULT_CONCEPT_FILE)
        print("opening concepts file")
        key = 0
        with open(DEFAULT_CONCEPT_FILE) as concepts_file:
            for lineN, line in enumerate(concepts_file):
                line = line.strip()
                split = line.split("\t")

                if len(split) < 3:
                    print("Skipping line because it doesn't have at least 3 columns...")
                else:
                    if not split[0].isdigit():
                        continue

                    # append each element after previous one. indices are new IDs, values are old IDs
                    value = int(split[0])
                    new_old_index_array.append(value)
                    old_new_index_dict[value] = key  # old ID -> new ID

                    # maps for example 1 to Anarchism
                    new_id_to_concept_mapping[key] = split[2]
                    key = key + 1

                    # print progress every 10M
                    if lineN % 1000000 == 0:
                        print(lineN / 1000000)
        # close file
        concepts_file.close()
        print("created our own dictionary of old to new and new to old indices and ID to word mappings")

        print("storing our own new-old IDs array to PICKLE dump")
        pickle.dump(new_old_index_array, open(NEW_OLD_ID_MAPPING_DUMP_PATH, "wb"))

        print("storing our own old-id dictionary to PICKLE dump")
        pickle.dump(old_new_index_dict, open(OLD_NEW_ID_MAPPING_DUMP_PATH, "wb"))

        print("storing our own dictionary to PICKLE dump")
        pickle.dump(new_id_to_concept_mapping, open(ID_CONCEPT_MAPPING_PICKLE_DUMP_PATH, "wb"))
    else:
        print("no concept id file or PICKLE dump, cannot proceed")
        exit(1)

    return new_old_index_array, old_new_index_dict, new_id_to_concept_mapping


# method creates concept mapping if it doesn't exist yet. If it does, it just reads if from a dump file
def create_concept_mappings_dict(default_concept_mapping_file,
                                 default_concept_mapping_pickle_dump_path,
                                 default_concept_mapping_pickle_both_transitions_dump_path,
                                 old_new_index_dict):
    id_concept_map = defaultdict(list)  # contains transitions A -> B
    both_transitions_map = defaultdict(list)  # contains transitions A -> B and B -> A

    if os.path.isfile(default_concept_mapping_pickle_dump_path) and os.path.isfile(
            default_concept_mapping_pickle_both_transitions_dump_path):

        print("concept mapping PICKLE dumps exist")
        print("reading file", default_concept_mapping_pickle_dump_path)
        id_concept_map = pickle.load(open(ID_CONCEPT_MAPPING_PICKLE_DUMP_PATH, "rb"))
        print("file", default_concept_mapping_pickle_dump_path, "read")

        print("reading file", default_concept_mapping_pickle_both_transitions_dump_path)
        both_transitions_map = pickle.load(open(default_concept_mapping_pickle_both_transitions_dump_path, "rb"))
        print("file", default_concept_mapping_pickle_both_transitions_dump_path, "read")

    elif os.path.isfile(default_concept_mapping_file):
        print("concept file dump doesnt exist. building new one from file", default_concept_mapping_file)

        print("opening file for creating concept transition dictionary")
        #  go through each line and build a dictionary of indices
        with open(default_concept_mapping_file) as concept_mappings_file:
            for lineN, line in enumerate(concept_mappings_file):
                line = line.strip()
                split = line.split("\t")

                if len(split) < 2:
                    print("Skipping line because it doesn't have at least 2 columns (concept ID and connection)")
                else:
                    # skip a line if it doesnt contain a number
                    if not split[0].isdigit() or not split[1].isdigit():
                        continue

                    try:
                        # declare two variables for start node ID and end node ID
                        key = old_new_index_dict[int(split[0])]
                        value = old_new_index_dict[int(split[1])]

                        id_concept_map[key].append(value)
                        both_transitions_map[key].append(value)
                        both_transitions_map[value].append(key)

                        # print progress every 10M
                        if lineN % 1000000 == 0:
                            print(lineN / 1000000)

                    except KeyError:
                        print("key", split[0], "value", split[1], "max index in array", len(old_new_index_dict) - 1)
                        print("Error extracting from_page_id or to_page_id from id_array")

        # close file
        concept_mappings_file.close()
        print("created concept transition dictionary")

        print("removing concepts that don't have any transitions")
        # remove concepts from dictionaries that don't have any transitions
        remove_keys = []
        for concept in both_transitions_map:
            transitions = both_transitions_map[concept]
            if len(transitions) == 0:
                remove_keys.append(concept)
        for key in remove_keys:
            del id_concept_map[key]
            del both_transitions_map[key]
        print("concepts without transitions successfully removed")

        print("storing own concept mapping dictionary to PICKLE dump")
        pickle.dump(id_concept_map, open(default_concept_mapping_pickle_dump_path, "wb"))
        print("storing own concept mapping dictionary to PICKLE dump completed")

        print("storing own concept mapping dictionary for both transitions to PICKLE dump")
        pickle.dump(both_transitions_map, open(default_concept_mapping_pickle_both_transitions_dump_path, "wb"))
        print("storing own concept mapping dictionary for both transitions to PICKLE dump completed")
    else:
        print("no concept mapping file or PICKLE dump, cannot proceed")
        exit(2)

    return id_concept_map, both_transitions_map


# create matrix only if its dump is not stored in the file system yet. If it is, we just read the dump
def create_matrix_P(filePath, both_transitions_map, matrix_dim):
    if os.path.isfile(filePath):
        print("matrix P file path exists")
        print("reading file", filePath)
        matrix = sparse.load_npz(filePath)
        print("file", filePath, "read")
    else:
        matrix = create_transition_matrix(both_transitions_map, matrix_dim)
        print("storing matrix P as sparse npz")
        sparse.save_npz(filePath, matrix)
        print("storing matrix P as sparse npz completed")

    return matrix


if __name__ == '__main__':
    DEFAULT_CONCEPT_FILE = './linkGraph-en-verts.txt'
    DEFAULT_CONCEPT_MAPPING_FILE = './linkGraph-en-edges.txt'
    NEW_OLD_ID_MAPPING_DUMP_PATH = './temp/linkGraph-en-verts-new-old-id-concept-mapping-dump.pkl'
    OLD_NEW_ID_MAPPING_DUMP_PATH = './temp/linkGraph-en-verts-old-new-id-mapping-dump.pkl'
    ID_CONCEPT_MAPPING_PICKLE_DUMP_PATH = './temp/linkGraph-en-verts-id-concept-mapping-dump.pkl'
    DEFAULT_CONCEPT_MAPPING_PICKLE_DUMP_PATH = './temp/linkGraph-en-edges-dump.pkl'
    DEFAULT_CONCEPT_MAPPING_PICKLE_BOTH_TRANSITIONS_DUMP_PATH = './temp/linkGraph-en-edges-both-transitions-dump.pkl'
    MATRIX_P_FILE_PATH = './temp/linkGraph-matrix-P-dump.npz'

    NUMBER_OF_NEW_CONCEPTS = 20
    ALFA = 0.2

    if ALFA < 0 or ALFA > 1:
        print("alfa parameter should be between 0 and 1")
        exit(1)

    # ========================================================================================================
    # concept mapping values should not be higher than maximum concept ID
    # concept_mappings_both_transitions values should not be higher than maximum concept ID
    # initial concepts values should not be higher than maximum concept ID
    # ========================================================================================================

    # indices_array is a 1D array where position presents index (new ID) and value presents old ID value
    new_old_index_array, old_new_index_dict, id_to_concept_mapping = create_concept_ids(
        DEFAULT_CONCEPT_FILE,
        NEW_OLD_ID_MAPPING_DUMP_PATH,
        OLD_NEW_ID_MAPPING_DUMP_PATH,
        ID_CONCEPT_MAPPING_PICKLE_DUMP_PATH)

    # if matrix_P already exists in a file, we don't need to extract concept_mappings and concept mappings
    # for both transitions
    concept_mappings, concept_mappings_both_transitions = create_concept_mappings_dict(
        DEFAULT_CONCEPT_MAPPING_FILE,
        DEFAULT_CONCEPT_MAPPING_PICKLE_DUMP_PATH,
        DEFAULT_CONCEPT_MAPPING_PICKLE_BOTH_TRANSITIONS_DUMP_PATH,
        old_new_index_dict)

    # old_new_id_mapping = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}
    #
    # new_old_index_array = [0, 1, 2, 3, 4, 5, 6]
    #
    # concept_old_id_to_new_id_mapping = {}
    # concept_old_id_to_new_id_mapping[33] = 3
    # id_to_concept_mapping = {}
    #
    # concept_mappings = {}
    # concept_mappings[0] = [1]
    # concept_mappings[1] = [1, 4, 1]
    # concept_mappings[2] = [1, 3]
    # concept_mappings[3] = [2, 4, 1]
    # concept_mappings[4] = [1, 4, 2]
    # concept_mappings[5] = []
    # concept_mappings[6] = []
    #
    # concept_mappings_both_transitions = {}
    # concept_mappings_both_transitions[0] = [1]
    # concept_mappings_both_transitions[1] = [0, 4, 3]
    # concept_mappings_both_transitions[2] = [1, 3]
    # concept_mappings_both_transitions[3] = [4, 2, 4, 1]
    # concept_mappings_both_transitions[4] = [4, 3, 1]
    # concept_mappings_both_transitions[5] = []
    # concept_mappings_both_transitions[6] = []

    # matrix dimension should be the same for all the matrices (at least one dimension)
    # length is 13504875 for EN-Wikipedia
    matrix_dimension = len(concept_mappings_both_transitions)

    # create transition matrix
    matrix_P = create_matrix_P(MATRIX_P_FILE_PATH, concept_mappings_both_transitions, matrix_dimension)
    print("matrix P shape", matrix_P.shape)

    # TODO create parser for initial concepts
    # TODO fake concepts
    initial_concepts = [3, 4, 2]

    calc_neighbourhood(matrix_dimension,
                       new_old_index_array,
                       id_to_concept_mapping,
                       concept_mappings,
                       initial_concepts,
                       matrix_P,
                       NUMBER_OF_NEW_CONCEPTS,
                       ALFA)
