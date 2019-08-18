import operator
import numpy as np

import time
import os
import sys
import signal
import subprocess
import linecache
import psutil
from scipy.sparse import linalg
from scipy.sparse import csc_matrix
from scipy import sparse

import json as json

from collections import defaultdict
from db import Database


def create_matrix_p(transitions_map, matrix_dimension):
    # create transition matrix from all concepts

    print("==================================================================")
    print("                         CREATING MATRIX P")
    print("==================================================================")

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
        if counter % 100000 == 0:
            print("at counter", counter, "current ID is", id)

    print("creating transition values vector")
    transition_values = np.ones(len(transition_col), dtype=float)
    print("transition values vector for matrix Q created")

    # create sparse matrix Q that contains ones for each transition from A->B and B->A
    print("creating matrix Q")
    matrix_Q = csc_matrix((transition_values, (transition_row, transition_col)), (matrix_dimension, matrix_dimension))
    print(matrix_Q.shape)
    print("matrix Q created")

    # column vector of ones
    print("creating vector I")
    vector_I = np.ones((matrix_dimension, 1), dtype=float)
    print("vector I created")

    # 1D vector that contains the number of transitions in each row
    qi = matrix_Q * vector_I

    # create reciprocal matrix and transpose it
    reciprocal_transposed = np.transpose(np.reciprocal(qi))[0, :]

    # create diagonal matrix
    reciprocal_range = range(matrix_dimension)
    print("creating diagonal sparse matrix")
    sparse_diagonal_matrix = csc_matrix((reciprocal_transposed, (reciprocal_range, reciprocal_range)),
                                        (matrix_dimension, matrix_dimension))
    print("diagonal sparse matrix created")

    # get P matrix as a product of Q nad diagonal(inverse(Q * I))
    print("creating P matrix")
    matrix_P = csc_matrix((sparse_diagonal_matrix * matrix_Q), (matrix_dimension, matrix_dimension))
    print("matrix P created")

    # remove resources from memory
    del transitions_map
    del reciprocal_range
    del qi
    del reciprocal_transposed
    del vector_I
    del transition_values
    del sparse_diagonal_matrix
    del matrix_Q

    return matrix_P


def create_matrix_j(initial_concepts, all_concepts, matrix_dimension, recreate=False):
    # creates transition matrix from initial concepts
    matrix_j_file_path = './temp/linkGraph-matrix-J-dump.npz'

    # check if matrix J exists already and we do not need to recreate it because initial concepts are still valid ->
    # just read it from file dump
    if os.path.isfile(matrix_j_file_path) and not recreate:
        print("==================================================================")
        print("                         READING MATRIX J")
        print("==================================================================")
        print("reading file", matrix_j_file_path)
        matrix_J = sparse.load_npz(matrix_j_file_path)
        print("file", matrix_j_file_path, "read")

        return matrix_J

    print("==================================================================")
    print("                      CREATING MATRIX J")
    print("==================================================================")

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

    # create sparse matrix
    matrix_J = csc_matrix((transition_values, (transition_row, transition_col)), (matrix_dimension, matrix_dimension))
    print("matrix J created with shape", matrix_J.shape)

    # remove values for sparse matrix
    del transition_col
    del transition_row
    del transition_values
    del initial_concepts

    print("storing matrix J as sparse npz")
    sparse.save_npz(matrix_j_file_path, matrix_J)
    print("storing matrix J as sparse npz completed")

    return matrix_J


# check if value is close enough to given value (used for comparing float values)
def is_close(a, b, rel_tol=1e-7, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def calc_neighbourhood(matrix_J,
                       entry_concepts,
                       matrix_P,
                       id_string_txt_path,
                       number_of_wanted_concepts,
                       alpha):
    # method calculates neighbourhood based on concept mappings and initial concepts

    print("creating P1 matrix from matrix P and matrix J")
    matrix_P1 = csc_matrix(((1 - alpha) * matrix_P) + ((alpha / float(len(entry_concepts))) * matrix_J))
    print("matrix P1 created")

    print("Transposing matrix P1...")
    transposed = matrix_P1.transpose()
    print("Transposing matrix P1 completed")

    # simulation
    # extract EigenValues and EigenVectors
    print("extracting eigenvalues and eigenvectors")
    [eigenvalues, vectors] = linalg.eigs(transposed, k=1)

    # extract only the column where EigenValue is 1.0
    print("extracting column of eigenvectors where eigenvalue is 1")
    result_array_idx = -1
    for eigenValueIdx in range(len(eigenvalues)):
        value = eigenvalues[eigenValueIdx].real
        print("Eigenvalue", value)
        if is_close(value, 1.0):
            result_array_idx = eigenValueIdx
            break
    if result_array_idx == -1:
        print("No EigenValue 1.0 in received eigenvalues. Exiting program...")

        # return result false with a reason
        json_resp = {}
        json_resp["success"] = False
        json_resp["reason"] = "Eigenvalue calculated from matrix is not 1."
        resp = json.dumps(json_resp)

        return resp

    print("extracted eigenvectors successfully")

    # only keep real value
    print("converting vectors to keep only real values")
    resultArray = vectors.real
    resultArray = resultArray.T[result_array_idx]

    # remove unused variables from memory
    del eigenvalues
    del vectors
    del matrix_P1
    del transposed
    del result_array_idx

    # get rid of possible numerical error -> if value is less than 0, set it to zero
    corrected_array = []
    array_sum = 0
    for value in resultArray:
        if value < 0:
            value = 0
        corrected_array.append(value)
        array_sum = array_sum + value

    # all values should sum up to ONE
    normalizedArray = []
    for value in corrected_array:
        if value == 0:
            normalizedArray.append(value)
        else:
            new_value = value / array_sum
            normalizedArray.append(new_value)

    print("creating array of similar concepts")
    similar_concepts = {}
    for concept_id in range(len(normalizedArray)):
        value = normalizedArray[concept_id]

        # if ID is not the same as initial concept, extract the value
        if concept_id not in entry_concepts:
            similar_concepts[concept_id] = value

    # sort descending - most similar concept is the highest
    print("sorting array of similar concepts descending by probability")
    sorted_similar_concepts = sorted(similar_concepts.items(), key=operator.itemgetter(1), reverse=True)

    # extract as many concepts as wanted by variable number_of_wanted_concepts
    extracted_concepts = sorted_similar_concepts[:number_of_wanted_concepts]

    # print result
    list = []
    for final_concept in extracted_concepts:
        id = final_concept[0]
        probability = final_concept[1]

        # get line from ID + 1 (because readings starts with 1 and our indices start at 0)
        line = linecache.getline(id_string_txt_path, id + 1).strip()
        if not line:
            print("Line at ID", id, "not found. Proceeding with next concept.")
            continue

        split = line.split("\t")
        word = split[1]

        json_object = {}
        json_object["concept_id"] = id
        json_object["probability"] = probability
        json_object["string"] = word

        list.append(json_object)

    # dict to json
    response = json.dumps(list)

    print("Constructed JSON object for response.")

    # return results as a list
    return response


def create_id_string_map(default_concept_file,
                         id_concept_mapping_txt_dump_path,
                         old_new_id_dict):
    # method extracts concepts IDs and creates new dictionary from them, if dump doesn't exist yet. if dump exists,
    # it just reads it from a dump file

    print("==================================================================")
    print("                    CREATING ID -> STRING MAP")
    print("==================================================================")

    new_old_id_dict = {}
    if len(old_new_id_dict) != 0:
        # old_new_id_dict contains the mapping old -> new ID for old concepts that contain transitions
        # the following commands just reverses the dictionary, it transforms keys of old -> new dict to new -> old dict
        new_old_id_dict = {v: k for k, v in old_new_id_dict.items()}

    if os.path.isfile(id_concept_mapping_txt_dump_path):
        # file exists, no need to create new one
        print("concept file txt dump exists")

    elif os.path.isfile(default_concept_file):
        print("using default concept file path", default_concept_file)
        print("opening concepts file")

        # get maximum value of new ID so far if dictionary has any fields
        if len(new_old_id_dict) == 0:
            counter = 0  # start from the beginning
        else:
            counter = int(max(new_old_id_dict, key=int)) + 1  # continue where we left off

        ids = []
        strings = []
        with open(default_concept_file, 'r') as concepts_file:
            for lineN, line in enumerate(concepts_file):
                line = line.strip()
                split = line.split("\t")

                if len(split) < 3:
                    print("Skipping line because it doesn't have at least 3 columns...")
                else:
                    if not split[0].isdigit():
                        continue
                    new_id = counter

                    # append each element after previous one. indices are new IDs, values are old IDs
                    old_id = int(split[0])

                    # old id is already used as a key in old_new dictionary, so new ID is the
                    # value at position old_id in old_new_id_dict
                    if old_id in old_new_id_dict.keys():
                        new_id = old_new_id_dict[old_id]
                    else:
                        # add new key to old -> new dictionary and increment counter
                        old_new_id_dict[old_id] = counter
                        counter += 1

                    # append new values to both arrays
                    ids.append(new_id)
                    strings.append(split[2])

                    # print progress every 10M
                    if lineN % 1000000 == 0:
                        print(lineN / 1000000)

        sorted_ids = [x for _,x in sorted(zip(ids,ids))]
        sorted_strings = [x for _,x in sorted(zip(ids,strings))]

        # create arrays and store the data to text file
        data = np.array([sorted_ids, sorted_strings])
        data = data.T

        print("Storing dictionary of new ID -> string concept...")
        with open(id_concept_mapping_txt_dump_path, 'w') as fp:
            np.savetxt(fp, data, delimiter='\t', fmt=['%s', '%s'])
    else:
        print("no concept id file or json dump, cannot proceed")
        if apiProcess is not None:
            kill(apiProcess.pid)
        exit(1)


def create_concept_mappings_dict(default_concept_mapping_file,
                                 default_concept_mapping_json_both_dump_path,
                                 should_use_both_transitions=False,
                                 should_return_old_new_id_map=True):
    # method creates concept mapping if it doesn't exist yet. If it does, it just reads if from a dump file

    print("==================================================================")
    print("                     CREATING TRANSITION MAP")
    print("==================================================================")

    concept_transition_map = defaultdict(list)
    # contains transitions A -> B (and B -> A with old IDs if should_use_both_transitions flag is set)

    # similar to above (but with new IDs)
    new_id_concept_transition_map = defaultdict(list)

    if os.path.isfile(default_concept_mapping_json_both_dump_path):
        print("concept mapping json dumps exist")
        print("reading file", default_concept_mapping_json_both_dump_path)
        with open(default_concept_mapping_json_both_dump_path, 'r') as fp2:
            new_id_mapping_load = json.load(fp2)
        new_id_concept_transition_map = {int(old_key): val for old_key, val in
                                         new_id_mapping_load.items()}  # convert string keys to integers
        print("file", default_concept_mapping_json_both_dump_path, "read")

        # do not return calculate old_new_id_dict because we don't need it
        if should_return_old_new_id_map:
            print("creating hashmap of old -> new ID")
            # create mapping of old ID to new ID
            old_new_id_dict = {}
            new_id = 0
            for old_id in new_id_concept_transition_map:
                old_new_id_dict[old_id] = new_id
                new_id = new_id + 1
            print("hashmap of old -> new ID created")

    elif os.path.isfile(default_concept_mapping_file):
        print("concept file dump doesnt exist. building new one from file", default_concept_mapping_file)

        # =====================================================================================
        #          GO THROUGH EACH LINE AND EXTRACT ID AND ID TO WHICH IT CAN TRANSIT
        # =====================================================================================

        #  go through each line and build dictionaries for concept transitions
        with open(default_concept_mapping_file, 'r') as concept_mappings_file:
            for lineN, line in enumerate(concept_mappings_file):
                line = line.strip()
                split = line.split("\t")

                if len(split) < 2:
                    print("Skipping line because it doesn't have at least 2 columns (concept ID and connection)")
                else:
                    # skip a line if it doesnt contain a number
                    if not split[0].isdigit() or not split[1].isdigit():
                        continue

                    # declare two variables for start node ID and end node ID
                    old_id = int(split[0])
                    value = int(split[1])

                    # if key already exists in a dict, it appends value to it instead of overriding it
                    concept_transition_map[old_id].append(value)

                    # if this flag is set, old_id points to value and value also points to old_id
                    if should_use_both_transitions and value != old_id:
                        concept_transition_map[value].append(old_id)

                    # print progress every 10M
                    if lineN % 1000000 == 0:
                        print(lineN / 1000000)
        print("created concept transition dictionary")


        # =====================================================================================
        #                           REMOVE IDS WITHOUT TRANSITION
        # =====================================================================================

        # remove concepts from dictionaries that don't have any transitions
        print("removing concepts that don't have any transitions")
        remove_keys = []
        for concept in concept_transition_map.keys():
            transitions = concept_transition_map[concept]
            if len(transitions) == 0:
                remove_keys.append(concept)
        for key in remove_keys:
            # remove elements from both dictionaries
            del concept_transition_map[key]
        print("concepts without transitions and their IDs successfully removed")

        # =====================================================================================
        #               CREATE old_new_id_dict WHICH HAS NEW ID FOR EACH OLD ID
        # =====================================================================================

        print("creating hashmap of old -> new ID")
        # create mapping od old ID to new ID
        # new IDs are from 0 -> N, with step 1
        old_new_id_dict = {}
        new_id = 0
        transitions_array = []
        # go through all OLD ids (keys)
        for old_id in concept_transition_map.keys():
            # get transitions for each key and add them to transition array
            transitions_array.extend(concept_transition_map[old_id])

            # assign new ID to this key which is unique and increment counter
            old_new_id_dict[old_id] = new_id
            new_id = new_id + 1

        # go through all transitions and give them new IDs if they don't have them already
        for transition in transitions_array:
            if transition not in old_new_id_dict.keys():
                new_id += 1
                old_new_id_dict[transition] = new_id

        print("hashmap of old -> new ID created")

        del transitions_array

        # =====================================================================================
        #    FOR EACH NEW ID THAT IS USED AS A KEY, APPEND ALL TRANSITIONS, BUT WITH NEW IDS
        # =====================================================================================

        print("creating hashmap of new ID -> transitions with new ID")
        counter = 0
        for old_id in concept_transition_map.keys():
            # array of transitions but with old ids
            transitions = concept_transition_map[old_id]

            # get new ID for this concept
            new_id = old_new_id_dict[old_id]

            # go through array of transitions
            for transition in transitions:
                # extract new transition ID and append it to the dictionary
                new_transition_id = old_new_id_dict[transition]
                new_id_concept_transition_map[new_id].append(new_transition_id)

                counter = counter + 1
                if counter % 10000000 == 0:
                    print("at counter", counter)
        print("hashmap of new ID -> transitions with new ID created")

        # remove transition map from memory
        del concept_transition_map

        print("storing new ID -> transitions hashmap for both transitions to json dump")
        with open(default_concept_mapping_json_both_dump_path, 'w') as fp2:
            json.dump(new_id_concept_transition_map, fp2)
        print("storing new ID -> transitions hashmap for both transitions to json dump completed")
    else:
        print("no concept mapping file or json dump, cannot proceed")
        if apiProcess is not None:
            kill(apiProcess.pid)
        exit(2)

    if should_return_old_new_id_map:
        return new_id_concept_transition_map, old_new_id_dict
    else:
        return new_id_concept_transition_map


def init_dictionaries(id_string_mapping_txt_path, test=False):
    default_concept_file = './linkGraph-en-verts.txt'
    default_concept_mapping_file = './linkGraph-en-edges.txt'
    default_concept_mapping_json_dump_path = './temp/linkGraph-en-edges-dump.json'
    default_concept_mapping_json_both_transitions_dump_path = './temp/linkGraph-en-edges-both-transitions-dump.json'
    matrix_p_file_path = './temp/linkGraph-matrix-P-dump.npz'

    if test:
        print("======================================================================================")
        print("RUNNING IN TEST MODE! TRANSITION AND MAPPINGS USED WILL BE SMALLER THAN REAL ONES")
        print("======================================================================================")
        default_concept_file = './linkGraph-en-verts-test.txt'
        default_concept_mapping_file = './linkGraph-en-edges-test.txt'

    # check if matrix P exists. If it does, we don't need to calculate concept mappings for both transitions,
    # if it doesn't, we need to calculate it
    if os.path.isfile(matrix_p_file_path):
        print("matrix P file path exists")
        print("reading file", matrix_p_file_path)
        matrix_P = sparse.load_npz(matrix_p_file_path)
        print("file", matrix_p_file_path, "read")
    else:
        # read all concept transitions from a file (or a dump) and create a dictionary with modified IDs
        concept_mappings_both_transitions, old_new_id_temp_dict = create_concept_mappings_dict(
            default_concept_mapping_file,
            default_concept_mapping_json_both_transitions_dump_path,
            should_use_both_transitions=True)

        # indices_array is a 1D array where position presents index (new ID) and value presents old ID value
        create_id_string_map(default_concept_file,
                             id_string_mapping_txt_path,
                             old_new_id_temp_dict)

        # matrix dimension is the length of all transitions
        matrix_dimension = len(concept_mappings_both_transitions)

        # create matrix from both transitions maps
        matrix_P = create_matrix_p(concept_mappings_both_transitions, matrix_dimension)
        print("storing matrix P as sparse npz")
        sparse.save_npz(matrix_p_file_path, matrix_P)
        print("storing matrix P as sparse npz completed")

        del concept_mappings_both_transitions

    # create concept mappings
    concept_mappings = create_concept_mappings_dict(
        default_concept_mapping_file,
        default_concept_mapping_json_dump_path,
        should_return_old_new_id_map=False)

    return concept_mappings, matrix_P, id_string_mapping_txt_path


def extract_concept_ids(id_string_file_path, words):
    # extract concept IDs from strings in an array called 'words'

    # open file and iterate through all the lines
    concept_ids = []
    with open(id_string_file_path, 'r') as concept_id_string_file:
        for lineN, line in enumerate(concept_id_string_file):
            line = line.strip()
            split = line.split("\t")

            if len(concept_ids) >= len(words):
                print("Found IDs for all words (initial concepts)")
                break

            if len(split) < 2:
                print("Skipping line because it doesn't have at least 2 columns (concept ID and string)")
            else:
                # skip a line if it doesnt contain a number
                if not split[0].isdigit():
                    continue

                # second column
                string = split[1]

                # this word is in a list of words, that we received as new initial concepts ->
                # save ID (column 0) to array of IDs
                if string.lower() in words:
                    concept_ids.append(int(split[0]))

    return concept_ids


def handler(signum, frame):
    # catch signal for abort/kill application and also kill API process
    print('Signal handler called with signal', signum, ', killing api process and exiting application')
    if apiProcess is not None:
        kill(apiProcess.pid)
    sys.exit()


def kill(proc_pid):
    # kills process using psutil package
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


if __name__ == '__main__':
    ##################################################################################
    #                       DATABASE AND API INITIALIZATION
    ##################################################################################

    # get instance of database connection
    db_name = "concepts_db"
    database = Database(db_name)
    database.create_database(db_name)

    # create table if it doesn't exist - it will be used for storing/retrieving requests for concepts nearby
    database.create_table("CREATE TABLE IF NOT EXISTS concepts ("
                          "id serial PRIMARY KEY NOT NULL, "
                          "timestamp BIGINT NOT NULL, "
                          "alpha REAL NOT NULL,"
                          "concepts INT NOT NULL,"
                          "result jsonb);")

    # create table that will be used for storing new concepts (used for recreating matrix J)
    database.create_table("CREATE TABLE IF NOT EXISTS initial_concepts ("
                          "id serial PRIMARY KEY NOT NULL, "
                          "timestamp BIGINT NOT NULL, "
                          "processed BOOLEAN NOT NULL DEFAULT FALSE, "
                          "concepts jsonb);")

    # start API as subprocess
    apiProcess = subprocess.Popen(["python", "api.py"])

    # setup handler that will kill api if signal for abort/kill arrives (ctrl+c, ctrl+z)
    signal.signal(signal.SIGABRT, handler)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTSTP, handler)

    ##################################################################################
    #                              SCRIPT INITIALIZATION
    ##################################################################################

    # init dictionaries needed for API and concepts needed for API
    id_string_file_path = './temp/linkGraph-en-verts-id-string-mapping.txt'
    concept_mappings, matrix_P, id_string_txt_path = init_dictionaries(id_string_file_path, True)

    # calculate matrix dimension based on concept mappings length
    matrix_dimension = len(concept_mappings)

    # initial concepts -> hardcoded IDs based on the strings given
    # "car", "motorhome", "bicycle", "truck", "caravan"
    initial_concepts = [59328, 115417, 262446, 382724, 524266]

    # create matrix that contains transition probabilities from each concept back to initial concept
    matrix_J = create_matrix_j(initial_concepts, concept_mappings, matrix_dimension)

    ##################################################################################
    #                            REQUEST PROCESSOR
    ##################################################################################

    print("==================================================================")
    print("                 STARTING REQUEST PROCESSOR")
    print("==================================================================")

    while True:
        ##################################################################################
        #  CHECKING IF NEW CONCEPTS ARE AVAILABLE (for generating new initial concepts)
        ##################################################################################

        # query not processed requests for generating new initial concepts
        available_concepts_result = database.query("SELECT id, concepts FROM initial_concepts WHERE NOT processed;")

        # new request for updating initial concepts
        if available_concepts_result:
            print("==================================================================")
            print("     PROCESSING NEW REQUEST FOR GENERATING NEW INITIAL IDs")
            print("==================================================================")

            id = available_concepts_result[0][0]
            # extract array of concepts, it should like something like ->
            # ['car', 'motorhome', 'ship', 'moon', 'sun', 'idea']
            concepts_arr = available_concepts_result[0][1]

            print("Processing request with ID", id, "new concepts", concepts_arr)

            # extract new concept IDs from given words
            new_concept_ids = extract_concept_ids(id_string_file_path, concepts_arr)

            # new concepts are valid (not an empty list) - make them initial concepts
            if new_concept_ids:
                print("New concept IDs", new_concept_ids)
                initial_concepts = new_concept_ids

                print("==================================================================")
                print("           CREATING NEW MATRIX J FROM NEW CONCEPT IDs")
                print("==================================================================")

                # create matrix that contains transition probabilities from each concept back to initial concept
                matrix_J = create_matrix_j(initial_concepts, concept_mappings, matrix_dimension, True)

                print("==================================================================")
                print("           NEW MATRIX J FROM NEW CONCEPT IDs JUST CREATED")
                print("==================================================================")

                print("Finished processing request with ID", id)

                # update database
                database.execute("UPDATE initial_concepts SET processed = %s where id = %s;", (True, id))

                # remove request older than one day
                # remove requests that are at least 1 day old from the database
                one_day_ago = round(time.time() - (24 * 60 * 60))
                database.execute("DELETE FROM initial_concepts WHERE timestamp < %s;", (one_day_ago,))
        else:
            print("No task for calculating new initial concepts at", round(time.time()))

        ##################################################################################
        #                      CHECKING IF NEW TASK IS AVAILABLE FOR PROCESSING
        ##################################################################################

        # query database for next task
        result = database.query("SELECT id, alpha, concepts FROM concepts WHERE result IS NULL")
        if not result:
            print("No task at for calculating similar concepts at", round(time.time()))
            # no task ahead, just wait for 10 seconds
            time.sleep(10)
            continue

        # extract alpha and number of new concepts and start processing
        id = result[0][0]
        alpha = result[0][1]
        new_concepts_number = result[0][2]

        print("Processing request with ID", id, "alpha", alpha, "number of concepts", new_concepts_number)

        # calculate neighbourhood and store result into database
        result = calc_neighbourhood(matrix_J,
                                  initial_concepts,
                                  matrix_P,
                                  id_string_txt_path,
                                  new_concepts_number,
                                  alpha)

        print("Finished processing request with ID", id)

        # insert result into database
        database.execute("UPDATE concepts SET result = %s WHERE id = %s;", (result, id))

        # remove requests that are at least 1 day old from the database
        one_day_ago = round(time.time() - (24 * 60 * 60))
        database.execute("DELETE FROM concepts WHERE timestamp < %s;", (one_day_ago,))
