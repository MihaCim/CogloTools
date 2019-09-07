import json
from math import inf

from flask import Flask, request
from flask_jsonpify import jsonify
from flask_restful import Resource, Api
import random as ran
from modules.cvrp.vrp import VRP
from modules.demo.mockup_graph import MockupGraph
import time

SIOT_URL = 'http://151.97.13.227:8080/SIOT-war/SIoT/Server/'


class GraphProcessor:
    def __init__(self):
        self.g = MockupGraph('modules/demo/data/9node.json')

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
        with open('modules/demo/data/vehicles.json', 'r') as f:
            data = json.load(f)["vehicles"]
            vehicles = []
            for i in range(len(payload)):
                d = data[i]
                d['UUID'] = payload[i]["UUID"]
                vehicles.append(d)
            return {"vehicles": vehicles}

    def load_demand(self):
        with open('modules/demo/data/parcels.json', 'r') as f:
            return json.load(f)


siot = LocalSioT()
graphProcessor = GraphProcessor()


class VrpProcessor:
    def __init__(self):
        self.vrp = VRP()

    def process(self, post_mapping, graph, capacities, nodes, edges):

        start = [nodes.index(x) for x in post_mapping]
        capacity = [int(x["metadata"]["capacityKg"]) for x in capacities]
        # generate random load demands
        load_demand = [ran.random() * sum(capacity) for i in range(0, len(nodes))]
        load_demand = [int(i * 100.0 / sum(load_demand)) for i in load_demand]
        costs = [e.cost for e in edges]
        return self.vrp.vrp(graph, load_demand, capacity, start, costs)

    def find_closest_post(self, loads, start, nodes):
        min_dist = inf
        min_idx = -1
        for post_idx, load in enumerate(loads):
            if load > 0:
                cur_dist = graphProcessor.g.distance(start, nodes[post_idx])
                if cur_dist < min_dist:
                    min_dist = cur_dist
                    min_idx = post_idx
        return min_idx

    def make_route(self, graph_routes, loads, start_nodes, nodes, edges):
        routes = []
        print("Building route from VRP output...")
        print(len(edges))
        start_time = time.time()
        routes = []

        for i, vehicle in enumerate(loads):
            route = []
            start_node = start_nodes[i]
            current_node = start_node
            vehicle[nodes.index(current_node)] -= vehicle[nodes.index(current_node)]
            cost_astar = 0
            old = vehicle.copy()

            while sum(vehicle) > 1:
                post_idx = self.find_closest_post(vehicle, current_node, nodes)
                target = nodes[post_idx]
                vehicle[post_idx] -= vehicle[post_idx]
                partial_path = graphProcessor.g.get_path(current_node, target)
                for node in partial_path.path:
                    for idx, val in enumerate(vehicle):
                        if val > 0 and nodes.index(node) == idx:
                            vehicle[idx] -= vehicle[idx]

                current_node = target
                cost_astar += partial_path.cost

                #avoid adding duplicate node on start of route
                route += partial_path.path if len(partial_path.path) == 1 else partial_path.path[1:]

            edges_vrp = sum(graph_routes[i])
            edges_astar = len(route)
            print("VRP: {}, A*:{}".format(edges_vrp, edges_astar))
            cost_vrp = 0
            for i,c in enumerate(graph_routes[i]):
                cost_vrp += c * edges[i].cost

            print("Cost VRP: {}, Cost A*:{}".format(cost_vrp, cost_astar))
            graphProcessor.g.print_path(route)
            print([item if x > 0 else -1 for item,x in enumerate(old)])
            print(old)

            routes.append(route)

        print("Route build took: {}s".format(time.time() - start_time))
        return {}


vrpProcessor = VrpProcessor()


class RecReq(Resource):

    def get(self):
        return jsonify({"success": True, "message": "Please use POST request"})

    def post(self):
        data = request.get_json(force=True)
        print(data)

        v_metadata = data['vehicles']

        if len(v_metadata) < 1:
            return jsonify({"msg": "No vehicles"})

        near_post_map = graphProcessor.map_vehicles(v_metadata)
        nodes, edges, incident_matrix = graphProcessor.get_graph()

        print("Processing VRP data.")
        routes, dispatch, objc = vrpProcessor.process(near_post_map, incident_matrix, v_metadata, nodes, edges)

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
