import json

from flask import Flask, request
from flask_jsonpify import jsonify
from flask_restful import Resource, Api

from modules.middleware.test.vrp import VRP

SIOT_URL = 'http://151.97.13.227:8080/SIOT-war/SIoT/Server/'

class GraphProcessor:
    def map_vehicles(self, data):
        vehicles = []
        for v in data["vehicles"]:
            vehicles.append(
                {"id": v["UUID"],
                 "latitude": v["location"]["latitude"],
                 "longitude": v["location"]["longitude"]})
        return vehicles

    def get_graph(self):
        pass

class LocalSioT:
    def retrieve_local_vehicles(self, payload):
        with open('vehicles.json', 'r') as f:
            return json.load(f)

    def load_demand(self):
        with open('parcels.json', 'r') as f:
            return json.load(f)


class VrpProcessor:
    def __init__(self):
        self.vrp = VRP()

    def process(self, post_mapping, graph, dispatch, capacities):
        start = [x["nodeId"] for x in post_mapping]
        capacity = [x["metadata"]["capacityKg"] for x in capacities]

        return self.vrp.vrp(graph, dispatch, capacity, start)


siot = LocalSioT()
graphProcessor = GraphProcessor()
vrpProcessor = VrpProcessor()


class RecReq(Resource):

    def get(self):
        return jsonify({"success": True, "message": "Please use POST request"})

    def post(self):
        data = request.get_json(force=True)
        event = data['event']
        vehicle = data['vehicle']
        v_metadata = data["vehicles"]

        v_locs = siot.retrieve_local_vehicles(data)

        near_post_map = graphProcessor.map_vehicles(v_locs)
        graph = graphProcessor.get_graph()
        loads = siot.load_demand()


        routes, dispatch, objc = vrpProcessor.process(near_post_map, graph, loads, v_metadata)

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
        self._register_endpoint('/api/adhoc/recRequest', RecReq)

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
