import pickle
import os
import time
from math import inf
from flask import Flask, request
from flask_jsonpify import jsonify
from flask_restful import Resource, Api
import random
from modules.cvrp.vrp import VRP
from waitress import serve
import argparse
from modules.partitioning.post_partitioning import GraphPartitioner
from modules.demo.graph_processing import GraphProcessor
JSON_GRAPH_DATA_PATH = 'modules/demo/data/graph_final.json'

MSB_FWD = 'http://116.203.13.198/api/postRecommendation'

"""
Example POST MSG:
{
	"eventType": "pickupRequest",
	"CLOS": [{
			"UUID": "UUID-1",
			"currentLocation": "A416",
			"capacity": 200,
			"parcels": [{
				"UUIDParcel": "ABCD",
				"weight": 2,
				"destination": "A89"
			}]
		}
	],
	"orders": [{
			"UUIDParcel": "Parcel UUID1",
			"UUIDRequest": "Request UUID1",
			"weight": 15,
			"destination": "A89",
			"pickup": "A2",
			"timestamp": 123456679
		},
		{
			"UUIDParcel": "Parcel UUID2",
			"UUIDRequest": "Request UUID2",
			"weight": 15,
			"destination": "A239",
			"pickup": "A2",
			"timestamp": 123456679
		}
	]
}
"""



class Vehicle:
    """
    This class stores information about single vehicle
    name is usually uuid
    start_node is name/matching UUID
    """

    def __init__(self, name, start_node, capacity=200):
        self.capacity = capacity
        self.name = name
        self.start_node = start_node


class Parcel:
    """
    Stores parcel information for single delivery
    Target is a destination Node
    Default package volume for poc is 1, for easier UUID unpacking
    """

    def __init__(self, uuid, target, volume):
        self.volume = volume
        self.target = target
        self.uuid = uuid


class Plan:
    """
    Information that are input to produce plan of routing for one partition
    vehicles in this partition, all deliveries in this partition and
    the partition object, which is a GraphProcessor object
    """

    def __init__(self, vehicles, deliveries, partition):
        self.vehicles = vehicles
        self.deliveries = deliveries
        self.partition = partition


class VrpProcessor:
    """Processes a request for routing
        Many operations on lists in this code can be replaced with dicts or similar, to remove list iteration with
        dict lookup.
    """

    def __init__(self, graphs):
        self.vrp = VRP()
        self.graphs = graphs

    def map_vehicles(self, vehicles):
        """Assign vehicles to partitions"""
        map_v = [[] for _ in self.graphs]

        for v in vehicles:
            for i in range(len(self.graphs)):
                graph = self.graphs[i]
                for node in graph.nodes:
                    if v.start_node == node.id:
                        map_v[i].append(v)

        return map_v

    def map_deliveries(self, deliveries):
        """Assign deliveries to partitions"""
        delivery_parts = [[] for _ in self.graphs]
        for d in deliveries:
            for i in range(len(self.graphs)):
                graph = self.graphs[i]
                nodes = graph.nodes
                for n in nodes:
                    if n.id == d.target:
                        delivery_parts[i].append(d)
        print(sum([len(x) for x in delivery_parts]), len(deliveries))
        assert sum([len(x) for x in delivery_parts]) == len(deliveries)
        return delivery_parts

    def map_dropoff(self, graph, deliveries):
        """Computer VRP input vector, how much volume will be dropped off on each node"""
        dropoff = [0] * len(graph.nodes)
        for d in deliveries:
            node = graph.node_from_id(d.target)
            idx = graph.nodes.index(node)
            dropoff[idx] += d.volume
        return dropoff

    def map_start_nodes(self, graph, vehicles):
        """Compute VRP input vector, where do the vehicles start"""
        indexes = []
        for v in vehicles:
            for i in range(len(graph.nodes)):
                if graph.nodes[i].id == v.start_node:
                    indexes.append(i)

        return indexes

    def process(self, vehicles, deliveries):
        """Process routing request with N vehicles and M deliveries, to produce a list of routing plans"""

        delivery_map = self.map_deliveries(deliveries)
        vehicle_map = self.map_vehicles(vehicles)

        plans = [Plan(vehicle_map[i], delivery_map[i], self.graphs[i]) for i in range(len(self.graphs))]
        routes = []

        for i, plan in enumerate(plans):
            partition = plan.partition
            if len(plan.deliveries) == 0 or len(plan.vehicles) == 0:
                print('Skipping plan {}, no deliveries or vehicles assigned'.format(i))
                continue
            else:
                print("Computing routing for plan", i)
            print('Starting planning for {} vehicles to deliver {} packages. Node len: {}'.format(len(plan.vehicles),
                                                                                                  len(plan.deliveries),
                                                                                                  len(partition.nodes)))
            # compute input vectors
            dropoff = self.map_dropoff(plan.partition, plan.deliveries)
            capacity = [v.capacity for v in plan.vehicles]
            start = self.map_start_nodes(partition, plan.vehicles)
            costs = [e.cost for e in partition.edges]

            computed_routes, dispatch, objc = self.vrp.vrp(partition.incident_matrix, dropoff, capacity, start, costs)
            # compute routes based on dispatch vectors from VRP. Since VRP output is incomplete/not best,
            # we add A* routing on top
            plan_routes = self.make_route(computed_routes, dispatch, partition, plan.vehicles, plan.deliveries)
            routes += plan_routes
        return routes

    def find_closest_post(self, loads, start, graph):
        nodes = graph.nodes
        min_dist = inf
        min_idx = -1
        for post_idx, load in enumerate(loads):
            if load > 0:
                cur_dist = graph.distance(start, nodes[post_idx])
                if cur_dist < min_dist:
                    min_dist = cur_dist
                    min_idx = post_idx
        return min_idx

    def make_route(self, graph_routes, loads, graph, vehicles, deliveries):
        nodes = graph.nodes
        edges = graph.edges
        print("Building route from VRP output...")
        print(len(edges))
        start_nodes = [graph.node_from_id(x.start_node) for x in vehicles]
        start_time = time.time()
        routes = []
        converted_routes = []

        for i, vehicle_load in enumerate(loads):
            start_node = start_nodes[i]
            route = [start_node]
            current_node = start_node
            vehicle_load[nodes.index(current_node)] -= vehicle_load[nodes.index(current_node)]
            cost_astar = 0
            original_vehicle_load = vehicle_load.copy()

            # always find closest post with parcels to pick/drop off.
            # start at closest node
            # get route and clear up any packages on this route
            while sum(vehicle_load) > 1:  # run until all parcels have been delivered
                post_idx = self.find_closest_post(vehicle_load, current_node,
                                                  graph)  # idx of closest post with parcel demand
                target = nodes[post_idx]  # convert idx to node object
                vehicle_load[post_idx] -= vehicle_load[post_idx]  # take/drop all parcels
                partial_path = graph.get_path(current_node,
                                              target)  # get path from current to next dropoff node
                for node in partial_path.path:  # drop off parcels along the way to targer
                    for idx, val in enumerate(vehicle_load):
                        if val > 0 and nodes.index(node) == idx:
                            vehicle_load[idx] -= vehicle_load[idx]

                current_node = target  # we are now at new node
                cost_astar += partial_path.cost

                # merge existing and new route, avoid adding duplicate node on start of route
                route += partial_path.path if len(partial_path.path) == 1 else partial_path.path[1:]

            # debug info
            print("Vehicle: {}".format(vehicles[i].name))
            print("Edges: VRP: {}, A*:{}".format(sum(graph_routes[i]), len(route)))

            # calculate theoretical cost of all visited edges in vrp, to compare to A*
            cost_vrp = sum([count * edges[j].cost for j, count in enumerate(graph_routes[i])])

            print("Cost VRP: {}, Cost A*:{}".format(cost_vrp, cost_astar))
            graph.print_path(route)
            print([item if x > 0 else -1 for item, x in enumerate(original_vehicle_load)])
            print(original_vehicle_load)

            routes.append(route)
            converted_routes.append({
                "UUID": vehicles[i].name,
                "route": self.route_to_sumo_format(route, original_vehicle_load, nodes, deliveries)})

        print("Route build took: {}s".format(time.time() - start_time))
        return converted_routes

    def route_to_sumo_format(self, route, loads, nodes, deliveries):
        """Transform output route to route according to what we discussed with Salvo.
        Should be modified for final POC"""
        converted_route = []

        if len(route) == 1 and loads[nodes.index(route[0])] == 0:
            return []

        for idx, node in enumerate(route):
            node_idx = nodes.index(node)

            parcels = [x.uuid for x in deliveries if x.target == node.id]

            converted_route.append({
                "locationId": node.id,
                "dropoffWeightKg": int(loads[node_idx]),
                "dropoffVolumeM3": int(loads[node_idx] / 10),
                "parcels": parcels,
                "info": "This parcel must be delivered to location " + str(node.id),
                "position": "{},{}".format(node.lon, node.lat)
            })

        return converted_route

    def parse_vehicles(self, clos):
        """Create a list of Vehicle objects from JSON input"""
        vehicles = []
        for clo in clos:
            vehicles.append(Vehicle(clo["UUID"], clo["currentLocation"], clo["capacity"]))
        return vehicles



class RecReq(Resource):

    def get(self):
        return jsonify({"success": True, "message": "Please use POST request"})

    def msb_forward(self, payload, key):
        pass

    # check api_ijs.py for this code

    def process_pickup_requests(self, clos, requests):
        print("Processing Pickup Delivery Request for ", len(clos), 'vehicles')
        vehicles = vrpProcessor.parse_vehicles(clos)
        deliveries = [Parcel(x["UUIDParcel"], x["destination"], x["weight"]) for x in requests]
        for clo in clos:
            for parcel in clo["parcels"]:
                deliveries.append(Parcel(parcel["UUIDParcel"], parcel["destination"], parcel["weight"]))

        return vrpProcessor.process(vehicles, deliveries)

    def process_broken_clo(self, clos, broken_clo):
        print("Processing Broken CLO for ", len(clos), 'vehicles')
        vehicles = vrpProcessor.parse_vehicles(clos)
        deliveries = [Parcel(x["UUIDParcel"], x["destination"], x["weight"]) for x in broken_clo["parcels"]]
        for clo in clos:
            for parcel in clo["parcels"]:
                deliveries.append(Parcel(parcel["UUIDParcel"], parcel["destination"], parcel["weight"]))

        return vrpProcessor.process(vehicles, deliveries)

    def post(self):
        """Main entry point for HTTP request"""
        data = request.get_json(force=True)
        evt_type = data["eventType"]
        if evt_type == "brokenVehicle":
            clos = data["CLOS"]
            broken_clo = data["BrokenVehicle"]
            recommendations = self.process_broken_clo(clos, broken_clo)
            return jsonify(recommendations)
        elif evt_type == "pickupRequest":
            clos = data["CLOS"]
            requests = data["orders"]
            recommendations = self.process_pickup_requests(clos, requests)
            return jsonify(recommendations)
        else:
            return jsonify({"message": "Invalid event type: {}".format(evt_type)})


class CognitiveAdvisorAPI:
    def __init__(self, port=5000):
        self._port = port
        self._app = Flask(__name__)
        self._api = Api(self._app)
        self._add_endpoints()

    def _add_endpoints(self):
        self._register_endpoint('/api/adhoc/recommendationRequest', RecReq)

    def _register_endpoint(self, endpoint_name, class_ref):
        self._api.add_resource(class_ref, endpoint_name)

    def start(self):
        serve(self._app, host='0.0.0.0', port=self._port)

##############################
pickle_path = './' + JSON_GRAPH_DATA_PATH.replace('/', '_') + '.graphs.pickle'
partitioner = None
print('Checking if data from', JSON_GRAPH_DATA_PATH, 'exists.')
if os.path.exists(pickle_path):
    with open(pickle_path, 'rb') as loadfile:
        partitioner = pickle.load(loadfile)
    print('Loaded pickled graph data')
else:
    # make 25 partitions, so our VRP can do the work in reasonable time,
    # even then small or even-sized partitions are not guaranteed
    K = 2
    # instance partitioner object, partition input graph, create graph processors
    # for all partitions and then create instance of vrp proc
    print('No data found, runing load and partition procedure')
    partitioner = GraphPartitioner(JSON_GRAPH_DATA_PATH)
    partitioner.partition(K)
    with open(pickle_path, 'wb') as dumpfile:
        pickle.dump(partitioner, dumpfile)
        print('Stored pickled dump for future use')

vrpProcessor = VrpProcessor(partitioner.graphProcessors)

if __name__ == '__main__':

    # this is an example code that demoes input and computation of routing
    min_graph = partitioner.graphProcessors[0]
    for g in partitioner.graphProcessors:
        if len(g.nodes) < len(min_graph.nodes):
            min_graph = g

    available_vehicles = []
    dispatch_node = random.choice(min_graph.nodes).id
    for i in range(3):
        available_vehicles.append(Vehicle('Vehicle' + str(i), start_node=dispatch_node))

    requested_deliveries = []
    for i in range(15):
        requested_deliveries.append(
            Parcel(random.randint(100, 300), random.choice(min_graph.nodes).id, random.randint(1, 30)))

    print(['Vehicle {} at {}'.format(x.name, x.start_node) for x in available_vehicles])
    print(['Delivery of {} to {}'.format(x.volume, x.target) for x in requested_deliveries])

    vrpProcessor.process(available_vehicles, requested_deliveries)

    # this starts flask server
    server = CognitiveAdvisorAPI()
    server.start()
