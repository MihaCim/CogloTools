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
    received_json = json.dumps(request.json)
    if received_json == 'null':
        return 'Error parsing request. It should be in JSON format'
    print(received_json)

    if 'alpha' not in received_json:
        return 'JSON object in request must contain key "alpha".'

    if 'number' not in received_json and 'percentage' not in received_json:
        return 'JSON object in request must contain key "number" or "percentage", ' \
               'representing number of new concepts wanted or percentage of new concepts respectfully.'

    # alpha = received_json['alpha']
    # print("alpha")

    # TODO extract number of concepts or percentage and alpha parameter, check if both are OK
    # TODO generate ID for this task, store request into database and return generated ID as response
    return "0"


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
