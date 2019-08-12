from flask import Flask
from flask_restful import Api
from flask import request

import json
import time

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
    print(received_request)

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
                              "VALUES (DEFAULT, %s, %s, %s) RETURNING id", (timestamp, alpha, value))
    # error inserting into database
    if row_id is None:
        return "Error processing/storing request into the database."

    # create response as json object
    response = {'result': 'success', 'id': row_id}

    return response


@app.route('/getConceptResult', methods=['POST'])
def get_concept_results():
    # TODO extract task ID and check in the database if operation finished (database has result with this ID)
    # TODO if operation is done, return result, otherwise return -1 or json with message "done": false
    return "-1"


if __name__ == '__main__':
    # get instance of database connection
    db_name = "concepts_db"
    database = Database(db_name)

    # start API
    app.run(debug=True)
