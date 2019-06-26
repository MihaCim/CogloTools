import operator
import numpy as np
import json
import os
from scipy.sparse import linalg
from scipy.sparse import csr_matrix
from scipy.sparse import coo_matrix
from scipy import sparse


# This method calculates neighbourhood from existing P matrices
# first parameter is P matrix, for example dump of wikipedia
# second parameter is a list of initial concepts (knowledge base)
# third parameter is p0 -
# fourth parameter is threshold t
def calc_neighbourhood(matrix_P):
    print len(matrix_P)


# create transition matrix from all concepts
def create_transition_matrix(concept_mappings):
    matrix_dimension = len(concept_mappings)
    print "creating transition matrix P of dimension", matrix_dimension, "x", matrix_dimension
    transition_row = []
    transition_col = []
    transition_values = []

    # go through concept mappings
    id = 0
    for concept_idx in concept_mappings.keys():
        # go through each transition
        for transition in concept_mappings[concept_idx]:
            # add transition a -> b
            transition_values.append(1.0)
            transition_row.append(concept_idx)
            transition_col.append(transition)

            # add transition b -> a
            transition_values.append(1.0)
            transition_row.append(transition)
            transition_col.append(concept_idx)

            id = id + 1
            if id % 1000000 == 0:
                print id

    transition_row = np.array(transition_row).astype(np.int_)
    transition_col = np.array(transition_col).astype(np.int_)

    # create sparse matrix Q that contains ones for each transition from A->B and B->A
    print "creating matrix Q"
    matrix_Q = coo_matrix((transition_values, (transition_row, transition_col)), (matrix_dimension, matrix_dimension)).todok().tocsc()
    print "matrix Q created"

    # column vector of ones
    print "creating vector I"
    vector_I = np.ones((matrix_dimension, 1), dtype=float)
    print "vector I created"

    # 1D vector that contains the number of transitions in each row
    qi = matrix_Q * vector_I

    # create reciprocal matrix and transpose it
    reciprocal_transposed = np.transpose(np.reciprocal(qi))[0, :]

    # create diagonal matrix
    reciprocal_range = range(matrix_dimension)
    print "creating diagonal sparse matrix"
    sparse_diagonal_matrix = csr_matrix((reciprocal_transposed, (reciprocal_range, reciprocal_range)),
                                        (matrix_dimension, matrix_dimension))
    print "diagonal sparse matrix created"

    # get P matrix as a product of Q nad diagonal(inverse(Q * I))
    print "creating P matrix"
    matrix_P = csr_matrix((sparse_diagonal_matrix * matrix_Q), (matrix_dimension, matrix_dimension))
    print "matrix P created"

    return matrix_P


# creates matrices
def create_initial_concept_transition_matrix(initial_concepts, all_concepts):
    print "creating initial concept transition matrix J"
    matrix_dimension = len(concept_mappings)
    transition_row = []
    transition_col = []
    transition_values = []

    # go through every initial concept
    for colN in initial_concepts:
        for rowN in all_concepts:
            transition_values.append(1.0)
            transition_row.append(rowN)
            transition_col.append(colN)

    transition_row = np.array(transition_row).astype(np.int_)
    transition_col = np.array(transition_col).astype(np.int_)

    # create sparse matrix
    sparse = csr_matrix((transition_values, (transition_row, transition_col)), (matrix_dimension, matrix_dimension))
    print "matrix J created"

    return sparse


# normalizes data (0 - 1)
def normalize_data(array):
    return (array - array.min()) / (array.max() - array.min())


# check if value is close enough to given value (used for comparing float values)
def is_close(a, b, rel_tol=1e-07, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


# method calculates neighbourhood based on concept mappings and initial concepts
def calc_neighbourhood(concept_old_id_to_new_id_mapping,
                       id_to_concept_mapping,
                       concept_mappings,
                       initial_concepts,
                       matrix_P,
                       number_of_wanted_concepts,
                       alfa):
    # create matrix that contains transition probabilities from each concept back to initial concept
    matrix_J = create_initial_concept_transition_matrix(initial_concepts, concept_mappings)

    k = len(initial_concepts)  # number of initial concepts

    print "creating P1 matrix from matrix P and matrix J"
    matrix_P1 = csr_matrix(((1 - alfa) * matrix_P) + ((alfa / float(k)) * matrix_J))
    print "matrix P1 created"

    # simulation
    # extract EigenValues and EigenVectors
    print "extracting eigenvalues and eigenvectors"
    [eigenvalues, vectors] = linalg.eigs(matrix_P1.transpose(), k, None, None, 'LM')

    # extract only the column where EigenValue is 1.0
    print "extracting column of eigenvectors where eigenvalue is 1"
    resultArrayIdx = -1
    for eigenValueIdx in range(len(eigenvalues)):
        value = eigenvalues[eigenValueIdx].real

        if is_close(value, 1.0):
            resultArrayIdx = eigenValueIdx
            break
    if resultArrayIdx == -1:
        print "No EigenValue 1.0 in received eigenvalues. Exiting program..."
        exit(3)
    print "extracted eigenvectors successfully"

    # only keep real value
    print "converting vectors to keep only real values"
    resultArray = vectors.real

    # normalize data from column with index resultArrayIdx because that column represents our results
    print "normalizing data"
    normalizedArray = normalize_data(resultArray.T[resultArrayIdx])
    print "data normalized"

    print "creating array of similar concepts"
    similar_concepts = {}
    for concept_id in range(len(normalizedArray.T)):
        value = normalizedArray.T[concept_id]

        # if ID is not the same as initial concept, extract the value
        if concept_id not in initial_concepts:
            similar_concepts[concept_id] = value

    # sort descending - most similar concept is the highest
    print "sorting array of similar concepts descdending by probability"
    sorted_similar_concepts = sorted(similar_concepts.items(), key=operator.itemgetter(1), reverse=True)
    print sorted_similar_concepts

    # TODO extract a word from wikipedia dictionary that was build in the beginning of the program


# method extracts concepts IDs and creates new dictionary from them, if dump doesn't exist yet. if dump exists,
# it just reads it from a dump file
def create_concept_ids(DEFAULT_CONCEPT_FILE, OLD_NEW_ID_CONCEPT_MAPPING_DUMP_PATH, ID_CONCEPT_MAPPING_JSON_DUMP_PATH):
    # try opening concepts file dump and if it doesn't exist, try opening the file and construct dump from it
    concept_old_id_to_new_id_mapping = {}
    id_to_concept_mapping = {}
    if os.path.isfile(OLD_NEW_ID_CONCEPT_MAPPING_DUMP_PATH) and os.path.isfile(ID_CONCEPT_MAPPING_JSON_DUMP_PATH):
        print "concept file json dumps exist"
        print "opening file", OLD_NEW_ID_CONCEPT_MAPPING_DUMP_PATH
        with open(OLD_NEW_ID_CONCEPT_MAPPING_DUMP_PATH, 'r') as fp1:
            concept_old_id_to_new_id_mapping = json.load(fp1)
        fp1.close()
        print "file", OLD_NEW_ID_CONCEPT_MAPPING_DUMP_PATH, "read"

        print "opening file", ID_CONCEPT_MAPPING_JSON_DUMP_PATH
        with open(ID_CONCEPT_MAPPING_JSON_DUMP_PATH, 'r') as fp2:
            id_to_concept_mapping = json.load(fp2)
        fp2.close()
        print "file", ID_CONCEPT_MAPPING_JSON_DUMP_PATH, "read"

    elif os.path.isfile(DEFAULT_CONCEPT_FILE):
        print "using default concept file path", DEFAULT_CONCEPT_FILE
        print "opening concepts file"
        key = 0
        with open(DEFAULT_CONCEPT_FILE) as concepts_file:
            for lineN, line in enumerate(concepts_file.xreadlines()):
                line = line.strip()
                split = line.split("\t")

                if len(split) < 3:
                    print "Skipping line because it doesn't have at least 3 columns..."
                else:
                    if not split[0].isdigit():
                        continue

                    concept_old_id_to_new_id_mapping[key] = split[0]
                    id_to_concept_mapping[key] = split[2]
                    key = key + 1
        # close file
        concepts_file.close()
        print "created own dictionary of old to new indices and index to word mapping"

        print "storing own dictionary to json dump"
        with open(OLD_NEW_ID_CONCEPT_MAPPING_DUMP_PATH, 'w') as fp1:
            json.dump(concept_old_id_to_new_id_mapping, fp1)
        fp1.close()
        with open(ID_CONCEPT_MAPPING_JSON_DUMP_PATH, 'w') as fp2:
            json.dump(id_to_concept_mapping, fp2)
        fp2.close()
        print "storing own dictionary to json dump completed"
    else:
        print "no concept id file or json dump, cannot proceed"
        exit(1)

    return concept_old_id_to_new_id_mapping, id_to_concept_mapping


# method creates concept mapping if it doesn't exist yet. If it does, it just reads if from a dump file
def create_concept_mappings_dict(DEFAULT_CONCEPT_MAPPING_FILE, DEFAULT_CONCEPT_MAPPING_JSON_DUMP_PATH, concept_old_id_to_new_id_mapping):
    # go through each line and build concept mapping
    concept_mappings = {}
    if os.path.isfile(DEFAULT_CONCEPT_MAPPING_JSON_DUMP_PATH):
        print "concept mapping json dump exists"
        print "reading file", DEFAULT_CONCEPT_MAPPING_JSON_DUMP_PATH
        with open(DEFAULT_CONCEPT_MAPPING_JSON_DUMP_PATH, 'r') as fp:
            concept_mappings = json.load(fp)
        fp.close()
        print "file", DEFAULT_CONCEPT_MAPPING_JSON_DUMP_PATH, "read"

    elif os.path.isfile(DEFAULT_CONCEPT_MAPPING_FILE):
        print "concept file dump doesnt exist. building new one from file", DEFAULT_CONCEPT_MAPPING_FILE

        count = 0
        print "counting the number of rows in concept mapping file"
        with open(DEFAULT_CONCEPT_MAPPING_FILE) as test:
            for line in test:
                count = count + 1
            print "number of lines in mapping is", count
        test.close()
        print "count completed"

        print "opening file for creating concept transition dictionary"
        #  go through each line and build a dictionary of indices
        with open(DEFAULT_CONCEPT_MAPPING_FILE) as concept_mappings_file:
            for lineN, line in enumerate(concept_mappings_file.xreadlines()):
                line = line.strip()
                split = line.split("\t")

                if len(split) < 2:
                    print "Skipping line because it doesn't have at least 2 columns (concept ID and connection)"
                else:
                    # skip a line if it doesnt contain a number
                    if not split[0].isdigit() or not split[1].isdigit():
                        continue

                    key = split[0]
                    id = concept_old_id_to_new_id_mapping[split[1]]
                    if key in concept_mappings:
                        array = concept_mappings.get(key)
                        # append new value to array
                        array.append(id)
                    else:
                        concept_mappings[key] = [id]

                # print progress every 10M
                if lineN % 1000000 == 0:
                    print lineN, "/", count

        # close file
        concept_mappings_file.close()
        print "created concept transition dictionary"

        print "storing own concept mapping dictionary to json dump"
        with open(DEFAULT_CONCEPT_MAPPING_JSON_DUMP_PATH, 'w') as fp:
            json.dump(concept_mappings, fp)
        fp.close()
        print "storing own concept mapping dictionary to json dump completed"
    else:
        print "no concept mapping file or json dump, cannot proceed"
        exit(2)

    return concept_mappings


# create matrix only if its dump is not stored in the file system yet. If it is, we just read the dump
def create_matrix_P(filePath, concept_mappings):
    if os.path.isfile(filePath):
        print "matrix P file path exists"
        print "reading file", filePath
        matrix = sparse.load_npz(filePath)
        print "file", filePath, "read"
    else:
        matrix = create_transition_matrix(concept_mappings)
        print "storing matrix P as sparse npz"
        sparse.save_npz(filePath, matrix)
        print "storing matrix P as sparse npz completed"

    return matrix


if __name__ == '__main__':
    DEFAULT_CONCEPT_FILE = './linkGraph-en-verts.txt'
    DEFAULT_CONCEPT_MAPPING_FILE = './linkGraph-en-edges.txt'
    OLD_NEW_ID_CONCEPT_MAPPING_DUMP_PATH = './temp/linkGraph-en-verts-old-new-concept-mapping-dump.json'
    ID_CONCEPT_MAPPING_JSON_DUMP_PATH = './temp/linkGraph-en-verts-id-concept-mapping-dump.json'
    DEFAULT_CONCEPT_MAPPING_JSON_DUMP_PATH = './temp/linkGraph-en-edges-dump.json'
    MATRIX_P_FILE_PATH = './temp/linkGraph-matrix-P-dump.npz'

    NUMBER_OF_NEW_CONCEPTS = 20
    ALFA = 0.2

    if ALFA < 0 or ALFA > 1:
        print "alfa parameter should be between 0 and 1"
        exit(1)

    concept_old_id_to_new_id_mapping, id_to_concept_mapping = create_concept_ids(
        DEFAULT_CONCEPT_FILE,
        OLD_NEW_ID_CONCEPT_MAPPING_DUMP_PATH,
        ID_CONCEPT_MAPPING_JSON_DUMP_PATH)

    concept_mappings = create_concept_mappings_dict(
        DEFAULT_CONCEPT_MAPPING_FILE,
        DEFAULT_CONCEPT_MAPPING_JSON_DUMP_PATH,
        concept_old_id_to_new_id_mapping)

    # concept_old_id_to_new_id_mapping = {}
    # concept_old_id_to_new_id_mapping[33] = 7
    # id_to_concept_mapping = {}
    #
    # concept_mappings = {}
    # concept_mappings[0] = [1]
    # concept_mappings[1] = [1, 4, 6]
    # concept_mappings[2] = [1, 3]
    # concept_mappings[3] = [5, 4, 1]
    # concept_mappings[4] = [11, 4, 5]
    # concept_mappings[5] = [5, 4, 1, 3]
    # concept_mappings[6] = [12, 4]
    # concept_mappings[7] = [11, 4,6]
    # concept_mappings[8] = [12, 4,]
    # concept_mappings[9] = [1, 4,]
    # concept_mappings[10] = [1, 4]
    # concept_mappings[11] = [1, 9]
    # concept_mappings[12] = [7]
    # concept_mappings[13] = [33]
    # concept_mappings[14] = [11]
    # concept_mappings[15] = [1]

    # create transition matrix
    matrix_P = create_matrix_P(MATRIX_P_FILE_PATH, concept_mappings)
    print matrix_P.shape

    # TODO create parser for initial concepts
    # TODO fake concepts
    initial_concepts = [3, 4, 5]

    calc_neighbourhood(concept_old_id_to_new_id_mapping,
                       id_to_concept_mapping,
                       concept_mappings,
                       initial_concepts,
                       matrix_P,
                       NUMBER_OF_NEW_CONCEPTS,
                       ALFA)
