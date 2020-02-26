import time
from math import inf
from flask import Flask, request
from flask_jsonpify import jsonify
from flask_restful import Resource, Api
import random
from modules.cvrp.vrp import VRP
from modules.partitioning.post_partitioning import GraphPartitioner
from modules.demo.mockup_graph import MockupGraph

MSB_FWD = 'http://116.203.13.198/api/postRecommendation'


class Vehicle:
    def __init__(self, name, start_node, capacity=200):
        self.capacity = capacity
        self.name = name
        self.start_node = start_node


class Delivery:
    def __init__(self, target, volume):
        self.volume = volume
        self.target = target


class Plan:
    def __init__(self, vehicles, deliveries, partition):
        self.vehicles = vehicles
        self.deliveries = deliveries
        self.partition = partition


class VrpProcessor:
    def __init__(self, graphs):
        self.vrp = VRP()
        self.graphs = graphs

    def map_vehicles(self, vehicles):
        map_v = [[] for _ in self.graphs]

        for v in vehicles:
            for i in range(len(self.graphs)):
                graph = self.graphs[i]
                for node in graph.nodes:
                    if v.start_node == node.id:
                        map_v[i].append(v)

        return map_v

    def map_deliveries(self, deliveries):
        delivery_parts = [[] for _ in self.graphs]
        for d in deliveries:
            for i in range(len(self.graphs)):
                graph = self.graphs[i]
                nodes = graph.nodes
                for n in nodes:
                    if n.id == d.target:
                        delivery_parts[i].append(d)

        assert sum([len(x) for x in delivery_parts]) == len(deliveries)
        return delivery_parts

    def map_dropoff(self, graph, deliveries):
        dropoff = [0] * len(graph.nodes)
        for d in deliveries:
            node = graph.node_from_id(d.target)
            idx = graph.nodes.index(node)
            dropoff[idx] += d.volume
        return dropoff

    def map_start_nodes(self, graph, vehicles):
        indexes = []
        for v in vehicles:
            for i in range(len(graph.nodes)):
                if graph.nodes[i].id == v.start_node:
                    indexes.append(i)

        return indexes

    def process(self, vehicles, deliveries):

        delivery_map = self.map_deliveries(deliveries)
        vehicle_map = self.map_vehicles(vehicles)

        plans = [Plan(vehicle_map[i], delivery_map[i], self.graphs[i]) for i in range(len(self.graphs))]
        routes = [[] for _ in self.graphs]

        for i, plan in enumerate(plans):
            if len(plan.deliveries) == 0 or len(plan.vehicles) == 0:
                print('Skipping plan, no deliveries or vehicles assigned')
                continue
            else:
                pass
            partition = plan.partition
            print('Starting planning for {} vehicles to deliver {} packages. Node len: {}'.format(len(plan.vehicles),
                                                                                                  len(plan.deliveries),
                                                                                                  len(partition.nodes)))
            dropoff = self.map_dropoff(plan.partition, plan.deliveries)
            capacity = [v.capacity for v in plan.vehicles]
            start = self.map_start_nodes(partition, vehicles)
            costs = [e.cost for e in partition.edges]

            try:
                computed_routes, dispatch, objc = self.vrp.vrp(partition.incident_matrix, dropoff, capacity, start, costs)
            except:
                print('Error')
            # paths = partition._calculate_shortest_paths()
            plan_routes = self.make_route(computed_routes, dispatch, partition, vehicles)
            routes.append(plan_routes)
        return routes

        # return self.make_route(routes, dispatch, nodes, edges, non_broken_vehicles)

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

    def make_route(self, graph_routes, loads, graph, vehicles):
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
                "route": self.route_to_sumo_format(route, original_vehicle_load, nodes)})

        print("Route build took: {}s".format(time.time() - start_time))
        return converted_routes

    def route_to_sumo_format(self, route, loads, nodes):
        converted_route = []

        if len(route) == 1 and loads[nodes.index(route[0])] == 0:
            return []

        for idx, node in enumerate(route):
            node_idx = nodes.index(node)

            converted_route.append({
                "locationId": node.id,
                "dropoffWeightKg": int(loads[node_idx]),
                "dropoffVolumeM3": int(loads[node_idx] / 10),
                "info": "This parcel must be delivered to location " + str(node.id),
                "position": "{},{}".format(node.lon, node.lat)
            })

        return converted_route

    def parse_vehicles(self, clos):
        vehicles = []
        for clo in clos:
            lat = clo["currentLocation"]["latitude"]
            lon = clo["currentLocation"]["longitude"]
            closest_node = None
            closest_dist = inf
            for part in self.graphs:
                for n in part.nodes:
                    if closest_node is None or closest_dist > part.arbitrary_distance(lat, lon, closest_node.lat, closest_node.lon):
                        closest_node = n

            vehicles.append(Vehicle(clo["UUID"], closest_node.id, clo["capacity"]))
        return vehicles


K = 25
partitioner = GraphPartitioner('/home/mikroman/dev/ijs/coglo/src/modules/demo/data/slovenia.json')
node_parts, edge_parts = partitioner.partition(K)
graphProcessors = [MockupGraph(node_parts[i], edge_parts[i]) for i in range(K)]
vrpProcessor = VrpProcessor(graphProcessors)


class RecReq(Resource):

    def get(self):
        return jsonify({"success": True, "message": "Please use POST request"})

    def msb_forward(self, payload, key):
        pass

    # timestamp = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S.000Z")
    # data = {"recommendations": []}
    # counter = 1
    # for clo in payload:
    #     route_plan = {
    #         "clo": clo["UUID"],
    #         "plan": {
    #             "uuid": "{}-plan-{}-{}".format(org_by_name(clo["UUID"]).replace(' ', ""), timestamp, counter),
    #             "organization": org_by_name(clo["UUID"]),
    #             "execution_date": timestamp,
    #             "steps": []
    #         }
    #     }
    #     counter += 1
    #
    #     for step in clo["route"]:
    #         location_split = step["position"].split(',')
    #
    #         transformed_step = {
    #             "location": {
    #                 "lat": float(location_split[1]),
    #                 "lng": float(location_split[0])
    #             },
    #             "station": uuid_by_name(step["locationId"]),
    #             "station_type": "post",
    #             "load": [str(uuid.uuid4()) for _ in range(randint(0, 4))],
    #             "unload": [str(uuid.uuid4()) for _ in range(randint(0, 4))]
    #         }
    #         route_plan["plan"]["steps"].append(transformed_step)
    #
    #     data["recommendations"].append(route_plan)
    #
    # print(data)
    # response = requests.post(MSB_FWD, json=data)
    # print("Posted data to", MSB_FWD)
    # print(response.content)

    def process_pickup_requests(self, clos, requests):
        print("Processing Pickup Delivery Request for ", len(clos), 'vehicles')
        vehicles = vrpProcessor.parse_vehicles(clos)
        deliveries = [Delivery(x["destination"], x["weight"]) for x in requests]
        for clo in clos:
            for parcel in clo["parcels"]:
                deliveries.append(Delivery(parcel["destination"], parcel["weight"]))

        return vrpProcessor.process(vehicles, deliveries)

    def process_broken_clo(self, clos, broken_clo):
        print("Processing Broken CLO for ", len(clos), 'vehicles')
        vehicles = vrpProcessor.parse_vehicles(clos)
        deliveries = [Delivery(x["destination"], x["weight"]) for x in broken_clo["parcels"]]
        for clo in clos:
            for parcel in clo["parcels"]:
                deliveries.append(Delivery(parcel["destination"], parcel["weight"]))

        return vrpProcessor.process(vehicles, deliveries)

    def post(self):
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

    def serve(self):
        self._app.run(host='0.0.0.0', port=self._port)


if __name__ == '__main__':
    server = CognitiveAdvisorAPI()

    server.serve()
    # min_graph = graphProcessors[0]
    # for g in graphProcessors:
    #     if len(g.nodes) < len(min_graph.nodes):
    #         min_graph = g
    #
    # vehicles = []
    # start_node = random.choice(min_graph.nodes).id
    # for i in range(3):
    #     vehicles.append(Vehicle('Vehicle' + str(i), start_node=start_node))
    #
    # deliveries = []
    # for i in range(15):
    #     deliveries.append(Delivery(random.choice(min_graph.nodes).id, random.randint(1, 30)))
    #
    # print(['Vehicle {} at {}'.format(x.name, x.start_node) for x in vehicles])
    # print(['Delivery of {} to {}'.format(x.volume, x.target) for x in deliveries])
    #
    # vrpProcessor.process(vehicles, deliveries)
