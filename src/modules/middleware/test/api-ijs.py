from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import asyncio
import requests
from flask_jsonpify import jsonify
import json

SIOT_URL = 'http://151.97.13.227:8080/SIOT-war/SIoT/Server/'


class LocalSioT():
    def retrieve_local_vehicles(self, json):
        with open('vehicles.json', 'r') as f:
            return json.load(f)


siot = LocalSioT()
graphProcessor = None


class Event(Resource):

    def get(self):
        return jsonify({"success": True, "message": "Please use POST request"})

    def post(self):
        json = request.get_json(force=True)
        event = json['event']
        vehicle = json['vehicle']

        siot = LocalSioT()
        vehicle_data = siot.retrieve_local_vehicles(json)

        vehicles = []
        for v in vehicle_data:
            vehicles.append(
                {"id": v["UUID"],
                 "latitude": v["location"]["latitude"],
                 "longitude": v["location"]["longitude"]})

        nearPostMapping = graphProcessor.map_vehicles(vehicles)
        graph = graphProcessor.get_graph()

        


        return jsonify({
            "success": True,
            "message": "Processing event for vehicle {}".format(vehicle['vehicleId'])
        })




class CognitiveAdvisorAPI:
    def __init__(self, port=5000):
        # http://151.97.13.227:8080/SIOT-war/SIoT/Server/proposedPlan
        self._port = port
        self._app = Flask(__name__)
        self._api = Api(self._app)
        self._add_endpoints()

    def _add_endpoints(self):
        self._register_endpoint('/api/adhoc/newEvent', Event)

    def _register_endpoint(self, endpoint_name, class_ref):
        self._api.add_resource(class_ref, endpoint_name)

    def serve(self):
        self._app.run(host='0.0.0.0', port=self._port)

    # ================================
    #  API ENDPOINTS
    # ================================


if __name__ == '__main__':
    server = CognitiveAdvisorAPI()

    server.serve()
