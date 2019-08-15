from flask import Flask
from flask_restful import Api
from flask import request

import time
import json

from db import Database

# create Flask instance for an app
app = Flask(__name__)
api = Api(app)


@app.route('/getNewConcepts', methods=['POST'])
def get_new_concepts():
    # received data must be in JSON format
    received_request = request.json
    if received_request == 'null' or received_request is None:
        return 'Error parsing request. It should be in JSON format'

    if 'alpha' not in received_request:
        return 'JSON object in request must contain key "alpha".'

    if 'number' not in received_request and 'percentage' not in received_request:
        return 'JSON object in request must contain key "number" or "percentage", ' \
               'representing number of new concepts wanted or percentage of new concepts respectfully.'

    if 'number' in received_request and 'percentage' in received_request:
        return 'Request must contain only key "number" or "percentage", not both.'

    # parameter for retireving concepts can be given as number of new concepts or as percentage of new
    # concepts in respect to the number of all concepts which is 13500000
    if 'number' in received_request:
        # number value must be an integer
        value = received_request['number']
        if not isinstance(value, int):
            return 'Number parameter should be an integer.'
        if value > 600:
            return 'Number value cannot be larger than 600.'
    else:
        # percentage value can be given as integer or a float
        value = received_request['percentage']
        if not isinstance(value, int) and not isinstance(value, float):
            return 'Percentage parameter should be an integer or a float.'
        if value > 0.005:
            return 'Percentage value cannot be larger than 0.005.'
        value = (value / 100.0) * 13500000

    # extract alpha parameter from request
    alpha = received_request['alpha']
    if alpha < 0 or alpha > 1:
        return 'Alpha parameter must be between 0 and 1.'

    # get current timestamp
    timestamp = int(round(time.time()))
    # round value to integer
    value = int(round(value))

    # store request to the database and return ID of inserted row
    row_id = database.execute("INSERT INTO concepts (id, timestamp, alpha, concepts) "
                              "VALUES (DEFAULT, %s, %s, %s) RETURNING id;", (timestamp, alpha, value), True)
    # error inserting into database
    if row_id is None:
        return "Error processing/storing request into the database."

    # create response as json object
    response = {'stored': 'success', 'id': row_id}

    return response


@app.route('/getConceptResult', methods=['POST'])
def get_concept_results():
    received_request = request.json
    if received_request == 'null' or received_request is None:
        return 'Error parsing request. It should be in JSON format'

    if 'id' not in received_request:
        return 'JSON object in request must contain key "id" which you received when you sent request to getNewConcept.'

    id = received_request['id']
    if not isinstance(id, int):
        return 'id parameter should be an integer.'

    result = database.query("SELECT result FROM concepts WHERE id = %s;", (id,))
    if result is None or not result:
        return {'result': 'null', 'id': id}
    else:
        return {'result': result[0], 'id': id}


@app.route('/generateInitialConcepts', methods=['POST'])
def generate_new_initial_concepts():
    received_request = request.json
    if received_request == 'null' or received_request is None:
        return 'Error parsing request. It should be in JSON format'

    # request should contain 'concepts' key
    if 'concepts' not in received_request:
        return 'JSON object in request must contain key "concepts".'

    # extract payload from concepts
    payload = received_request['concepts']

    # value of key 'concepts' must be an array
    if not isinstance(payload, list) or not payload:
        return 'Value of key concepts should be non empty array'

    # map unicode words to strings
    payload = map(str, payload)

    # store payload as json object
    json_obj = json.dumps(payload)

    # get current timestamp
    timestamp = int(round(time.time()))
    # store to the database and return row_id
    row_id = database.execute("INSERT INTO initial_concepts (id, timestamp, processed, concepts) "
                              "VALUES (DEFAULT, %s, FALSE, %s) RETURNING id;", (timestamp, json_obj), True)

    # create response as json object
    response = {'stored': 'success', 'id': row_id}

    return response


if __name__ == '__main__':
    # get instance of database connection
    db_name = "concepts_db"
    database = Database(db_name)

    # start API
    app.run(debug=True)
