import json

from flask import Flask, request
from flask_jsonpify import jsonify
from flask_restful import Resource, Api
import random as ran
from modules.demo.vrp import VRP
from modules.demo.mockup_graph import MockupGraph

SIOT_URL = 'http://151.97.13.227:8080/SIOT-war/SIoT/Server/'

class GraphProcessor:
    def __init__(self):
        self.g = MockupGraph()

    def map_vehicles(self, data):
        vehicles = []
        for v in data:
            loc = v["currlocation"]["currentPosition"]
            loc = loc.split(',')

            vehicles.append(
                {"id": v["vehicleId"],
                 "latitude": float(loc[1]),
                 "longitude": float(loc[0])})
        print("Mapping vehicles to posts")
        return self.g.map_vehicles(vehicles)

    def get_graph(self):
        return self.g.get_graph()


class LocalSioT:
    def retrieve_local_vehicles(self, payload):
        print("Loading vehicle data from local file")
        with open('modules/middleware/test/vehicles.json', 'r') as f:
            data = json.load(f)["vehicles"]
            vehicles = []
            for i in range(len(payload)):
                d = data[i]
                d['UUID'] = payload[i]["UUID"]
                vehicles.append(d)
            return {"vehicles": vehicles}

    def load_demand(self):
        with open('modules/middleware/test/parcels.json', 'r') as f:
            return json.load(f)


class VrpProcessor:
    def __init__(self):
        self.vrp = VRP()

    def process(self, post_mapping, graph, dispatch, capacities, nodes):

        start = [nodes.index(x[1]) for x in post_mapping]
        capacity = [int(x["metadata"]["capacityKg"]) for x in capacities]
        r = [ran.random() * sum(capacity) for i in range(0, 7)]
        r = [i * 100.0 / sum(r) for i in r]
        print(r)
        return self.vrp.vrp(graph, r, capacity, start)

    def make_route(self, v_routes, loads, mapping, nodes, edges):
        routes = []
        for i in range(len(v_routes)):
            route_edges = v_routes[i]
            route = []
            startend = int(mapping[i][1])
            curr_node = int(mapping[i][1])

            # run until all loads have been picked up
            while sum(route_edges) != 0.0:
                # check all edges
                for j in range(len(route_edges)):
                    edge_start = int(edges[j].split('_')[0])
                    edge_end = int(edges[j].split('_')[1])

                    # are we on this edge and do we need to pick up anything?
                    if edge_start == curr_node and route_edges[j] > 0:
                        if route_edges[j] == 1.0 and sum(route_edges) != 1.0 and startend == edge_end:
                            continue
                        route_edges[j] -= 1  # decrement edge visit counter
                        # create route node
                        route.append(
                            {"locationId": curr_node, "dropoffWeightKg": round(loads[i][nodes.index(curr_node)], 3),
                             "dropoffVolumeM3": round(loads[i][nodes.index(curr_node)], 3) / 10})
                        # reset load weight on node, since we visited it
                        loads[i][nodes.index(curr_node)] = 0
                        # set current node to opposite from where we came on this node
                        curr_node = edge_end
                        break
                    # are we on this edge and do we need to pick up anything?
                    if edge_end == curr_node and route_edges[j] > 0:
                        if route_edges[j] == 1.0 and sum(route_edges) != 1.0 and startend == edge_start:
                            continue
                        route_edges[j] -= 1
                        route.append(
                            {"locationId": curr_node, "dropoffWeightKg": round(loads[i][nodes.index(curr_node)], 3),
                             "dropoffVolumeM3": round(loads[i][nodes.index(curr_node)], 3) / 10})
                        loads[i][nodes.index(curr_node)] = 0
                        curr_node = edge_start
                        break

            # append end location
            route.append({"locationId": startend, "dropoffWeightKg": 0, "dropoffVolumeM3": 0})
            routes.append({"UUID": mapping[i][0], "route": route})
        return routes


siot = LocalSioT()
graphProcessor = GraphProcessor()
vrpProcessor = VrpProcessor()


class RecReq(Resource):

    def get(self):
        return jsonify({"success": True, "message": "Please use POST request"})

    def post(self):
        data = request.get_json(force=True)
        print(data)

        dummy_resp = {
            "vehicles": [
                {
                    "UUID": "352003092913241",
                    "route": [
                        {
                            "locationId": 17906,
                            "dropoffVolumeM3": 1.5981999999999998,
                            "dropoffWeightKg": 15.982
                        },
                        {
                            "locationId": 175,
                            "dropoffVolumeM3": 1.5608,
                            "dropoffWeightKg": 15.608
                        },
                        {
                            "locationId": 17906,
                            "dropoffVolumeM3": 0,
                            "dropoffWeightKg": 0,
                        }
                    ]
                },
                {
                    "UUID": "truck4F0",
                    "route": [
                        {
                            "locationId": 11560,
                            "dropoffVolumeM3": 1.1644999999999999,
                            "dropoffWeightKg": 11.645,
                        },
                        {
                            "locationId": 36151,
                            "dropoffVolumeM3": 1.4777,
                            "dropoffWeightKg": 14.777,
                        },
                        {
                            "locationId": 8525,
                            "dropoffVolumeM3": 1.3255000000000001,
                            "dropoffWeightKg": 13.255,
                        },
                        {
                            "locationId": 74,
                            "dropoffVolumeM3": 1.3006,
                            "dropoffWeightKg": 13.006,
                        },
                        {
                            "locationId": 53,
                            "dropoffVolumeM3": 1.5727,
                            "dropoffWeightKg": 15.727,
                        },
                        {
                            "locationId": 11560,
                            "dropoffVolumeM3": 0,
                            "dropoffWeightKg": 0,
                        }
                    ]
                }
            ]
        }

        return jsonify(dummy_resp)

        v_metadata = data['vehicles']

        if len(v_metadata) < 1:
            return jsonify({"msg": "No vehicles"})

        near_post_map = graphProcessor.map_vehicles(v_metadata)
        nodes, edges, incident_matrix = graphProcessor.get_graph()
        loads = siot.load_demand()

        print("Processing VRP data.")
        routes, dispatch, objc = vrpProcessor.process(near_post_map, incident_matrix, loads, v_metadata, nodes)

        route = vrpProcessor.make_route(routes, dispatch, near_post_map, nodes, edges)

        return jsonify({"vehicles": route})


class CognitiveAdvisorAPI:
    def __init__(self, port=5000):
        # http://151.97.13.227:8080/SIOT-war/SIoT/Server/proposedPlan
        self._port = port
        self._app = Flask(__name__)
        self._api = Api(self._app)
        self._add_endpoints()

    def _add_endpoints(self):
        self._register_endpoint('/api/adhoc/recommendationRequest', RecReq)

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
