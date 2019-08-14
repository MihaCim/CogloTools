import numpy as np
import os

if __name__ == '__main__':

    ######################################################################################
    #   MAKE EIXSTING CONCEPT ID AND CONCEPT STRING FILES FOR TESTTING PURPOSES.
    #   THAT MEANS THAT ONLY FIRST MAX_INDEX INDICES WILL BE VALID
    ######################################################################################

    MAX_INDEX = 15000

    # the following lines extract only first MAX_INDEX strings and ids
    default_concept_string_file = './linkGraph-en-verts.txt'
    default_concept_string_file_test = './linkGraph-en-verts-test.txt'

    if not os.path.isfile(default_concept_string_file_test):
        ids = []
        revisions = []
        strings = []
        with open(default_concept_string_file, 'r') as file_1:
            for lineN, line in enumerate(file_1):
                line = line.strip()
                split = line.split("\t")

                if len(split) < 3:
                    print("Skipping line because it doesn't have at least 3 columns...")
                else:
                    if not split[0].isdigit():
                        continue

                    # print progress every 100000 lines
                    if lineN % 100000 == 0:
                        print(lineN)

                    # append each element after previous one. indices are new IDs, values are old IDs
                    old_id = int(split[0])

                    if old_id > MAX_INDEX:
                        continue

                    # append new values to both arrays
                    ids.append(old_id)
                    revisions.append(split[1])
                    strings.append(split[2])

        print("IDs len", len(ids))
        print("Strings len", len(strings))

        # create arrays and store the data to text file
        data = np.array([ids, revisions, strings])
        data = data.T

        print("Storing dictionary of new ID -> string concept...")
        with open(default_concept_string_file_test, 'w') as fp1:
            np.savetxt(fp1, data, delimiter='\t', fmt=['%s', '%s', '%s'])

    # the following lines extract only first 1000 mappings
    default_concept_mapping_file = './linkGraph-en-edges.txt'
    default_concept_mapping_file_test = './linkGraph-en-edges-test.txt'

    if not os.path.isfile(default_concept_mapping_file_test):
        old_ids = []
        transition_ids = []
        with open(default_concept_mapping_file, 'r') as file_2:
            for lineN, line in enumerate(file_2):
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

                    # print progress every 10000 lines
                    if lineN % 100000 == 0:
                        print(lineN, "old_id:", old_id, "transition to", value)

                    if old_id > MAX_INDEX or value > MAX_INDEX:
                        continue

                    old_ids.append(old_id)
                    transition_ids.append(value)

        print("Ids len", len(old_ids))
        print("Transitions len", len(transition_ids))

        # create arrays and store the data to text file
        new_data = np.array([old_ids, transition_ids])
        new_data = new_data.T

        print("Storing dictionary of new ID -> string concept...")
        with open(default_concept_mapping_file_test, 'w') as fp2:
            np.savetxt(fp2, new_data, delimiter='\t', fmt=['%s', '%s'])