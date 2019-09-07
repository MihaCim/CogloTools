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
        return self.g.nodes, self.g.edges, self.g.incident_matrix


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

    def process(self, post_mapping, graph, metadata, nodes, edges):
        dropoff = [0] * len(nodes)
        for v in metadata:
            for loc in v['dropOffLocations']:
                target = graphProcessor.g.node_from_id(loc['locationId'])
                idx = nodes.index(target)
                dropoff[idx] += loc['dropoffWeightKg']

        start = [nodes.index(x) for x in post_mapping]
        capacity = [int(x["metadata"]["capacityKg"]) for x in metadata]
        # generate random load demands

        costs = [e.cost for e in edges]
        return self.vrp.vrp(graph, dropoff, capacity, start, costs)

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

    def make_route(self, graph_routes, loads, start_nodes, nodes, edges, vehicles):
        print("Building route from VRP output...")
        print(len(edges))
        start_time = time.time()
        routes = []
        converted_routes = []

        for i, vehicle_load in enumerate(loads):
            route = []
            start_node = start_nodes[i]
            current_node = start_node
            vehicle_load[nodes.index(current_node)] -= vehicle_load[nodes.index(current_node)]
            cost_astar = 0
            original_vehicle_load = vehicle_load.copy()

            # always find closest post with parcels to pick/drop off.
            # start at closest node
            # get route and clear up any packages on this route
            while sum(vehicle_load) > 1:
                post_idx = self.find_closest_post(vehicle_load, current_node, nodes)
                target = nodes[post_idx]
                vehicle_load[post_idx] -= vehicle_load[post_idx]
                partial_path = graphProcessor.g.get_path(current_node, target)
                for node in partial_path.path:
                    for idx, val in enumerate(vehicle_load):
                        if val > 0 and nodes.index(node) == idx:
                            vehicle_load[idx] -= vehicle_load[idx]

                current_node = target
                cost_astar += partial_path.cost

                # avoid adding duplicate node on start of route
                route += partial_path.path if len(partial_path.path) == 1 else partial_path.path[1:]

            # debug info
            print("Vehicle: {}".format(vehicles[i]['vehicleId']))
            edges_vrp = sum(graph_routes[i])
            edges_astar = len(route)
            print("Edges: VRP: {}, A*:{}".format(edges_vrp, edges_astar))
            cost_vrp = 0
            for j, count in enumerate(graph_routes[i]):
                cost_vrp += count * edges[j].cost

            print("Cost VRP: {}, Cost A*:{}".format(cost_vrp, cost_astar))
            graphProcessor.g.print_path(route)
            print([item if x > 0 else -1 for item, x in enumerate(original_vehicle_load)])
            print(original_vehicle_load)

            routes.append(route)
            converted_routes.append({
                "UUID": vehicles[i]["vehicleId"],
                "route": self.route_to_sumo_format(route, original_vehicle_load, nodes)})

        print("Route build took: {}s".format(time.time() - start_time))
        return converted_routes

    def route_to_sumo_format(self, route, loads, nodes):
        converted_route = []

        for idx, node in enumerate(route):
            node_idx = nodes.index(node)

            converted_route.append({
                "locationId": node.id,
                "dropoffWeightKg": int(loads[node_idx]),
                "dropoffVolumeM3": int(loads[node_idx] / 10)
            })

        return converted_route


vrpProcessor = VrpProcessor()


class RecReq(Resource):

    def get(self):
        return jsonify({"success": True, "message": "Please use POST request"})

    def post(self):
        data = request.get_json(force=True)
        print(data)

        vehicle_metadata = data['vehicles']

        if len(vehicle_metadata) < 1:
            return jsonify({"msg": "No vehicles"})

        near_post_map = graphProcessor.map_vehicles(vehicle_metadata)
        nodes, edges, incident_matrix = graphProcessor.get_graph()

        print("Processing VRP data.")
        routes, dispatch, objc = vrpProcessor.process(near_post_map, incident_matrix, vehicle_metadata, nodes, edges)

        route = vrpProcessor.make_route(routes, dispatch, near_post_map, nodes, edges, vehicle_metadata)

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
