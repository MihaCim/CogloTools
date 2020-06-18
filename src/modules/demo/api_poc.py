import os
import requests
import json

from flask import Flask, request
from flask_jsonpify import jsonify
from flask_restful import Resource
from waitress import serve
import csv
from ..create_graph.create_graph import JsonGraphCreator
from ..cvrp.processor.vrp_processor import VrpProcessor
from ..partitioning.graph_partitioning_preprocess import GraphPreprocessing
from ..utils.clo_update_handler import CloUpdateHandler
from ..create_graph.methods import methods
from ..create_graph.config.config_parser import ConfigParser
from ..utils.input_output import InputOutputTransformer

app = Flask(__name__)
vrpProcessorReferenceSloCro = None
vrpProcessorReferenceElta = None

config_parser = ConfigParser()
msb_post_url = "https://msb.cog-lo.eu/api/publish"

# Generic message expected to be returned after request to CA arrived
generic_message_received_response = {
    "status": 1,
    "msg": "The CA has received a new request for optimization"
}


def process_new_CLOs_request(data):
    global vrpProcessorReferenceElta
    global vrpProcessorReferenceSloCro

    if "clos" not in data or "useCase" not in data:
        return {"message": "Parameter 'clos' or 'useCase' is missing"}
    clos = data["clos"]  # Extract array of CLOs
    use_case = data["useCase"]
    csv_file = config_parser.get_csv_path(use_case)

    if use_case != "SLO-CRO" and use_case != "ELTA":
        return {"message": "Parameter 'useCase' can have value 'SLO-CRO' or 'ELTA'."}

    needs_rebuild = CloUpdateHandler.handle_new_clo_request(clos, csv_file)
    if needs_rebuild or not os.path.exists(config_parser.get_graph_path(use_case)):
        creator = JsonGraphCreator()
        creator.create_json_graph(use_case)

        # Delete existing pickle file for graph
        pickle_path = config_parser.get_pickle_path(use_case)
        if os.path.exists(pickle_path):
            os.remove(pickle_path)

        # Remove use case specific
        if use_case == "SLO-CRO":
            vrpProcessorReferenceSloCro = None
        else:
            vrpProcessorReferenceElta = None

    return {"success": True}


class RecReq(Resource):

    @staticmethod
    def init_vrp(use_case):
        """" Init VRP processor instance based on use-case defined in parameter"""
        graph_processors = GraphPreprocessing.extract_graph_processors(use_case)
        return VrpProcessor(graph_processors, use_case)

    def msb_forward(self, payload, key):
        pass
        # check api_ijs.py for this code

    @staticmethod
    def process_pickup_requests(evt_type, clos, requests, vrp_processor_ref, use_case):
        print("Processing Pickup Delivery Request for ", len(clos), 'vehicles')
        vehicles = vrp_processor_ref.parse_vehicles(clos)
        deliveries = vrp_processor_ref.parse_deliveries(evt_type, clos, requests, use_case)

        return vrp_processor_ref.process(vehicles, deliveries, evt_type)

    @staticmethod
    def process_broken_clo(evt_type, clos, broken_clo, vrp_processor_ref, use_case):
        print("Processing Broken CLO for ", len(clos), 'vehicles')
        vehicles = vrp_processor_ref.parse_vehicles(clos)
        deliveries = vrp_processor_ref.parse_deliveries(evt_type, clos, broken_clo, use_case)

        return vrp_processor_ref.process(vehicles, deliveries, evt_type)

    @staticmethod
    def process_cross_border_request(evt_type, clos, requests, vrp_processor_ref, use_case):
        print("Processing Cross Border Delivery Request for ", len(clos), 'vehicles')
        vehicles = vrp_processor_ref.parse_vehicles(clos)
        deliveries = vrp_processor_ref.parse_deliveries(evt_type, clos, requests, use_case)

        return vrp_processor_ref.process(vehicles, deliveries, evt_type)

    @staticmethod
    def post_response_msb(UUID, recommendations):
        # default=str set because we want to serialize Date objects also
        json_for_serialization = {
            "request_id": UUID,
            "recommendations": recommendations
        }
        dumped_str = json.dumps(json_for_serialization, indent=4, sort_keys=True, default=str)
        headers = {'Content-type': 'application/json'}
        content = {
            "topic": "RECOMMENDATIONS",
            "sender": "CA",
            "message": dumped_str
        }
        try:
            response = requests.post(msb_post_url, json = content, headers=headers, verify=False)
            print(response)
        except Exception as ex:
            print("Error occurred while posting response to MSB", ex)


@app.route("/api/adhoc/getRecommendation", methods=['POST'])
def handle_recommendation_request():
    # TODO: Make generic_message_received_response synchronous and all other operations asynchronous
    """
    Message received will always be in the following format. This info was given by company IntraSoft,
    integration work-package leader on 5.6.2020.
    {
        organization: "ELTA"
        clos: http://app.cog-lo.eu/getCLOs?org=ELTA,
        parcels: http://app.cog-lo.eu/getParcels?org=ELTA,
        event: null (for the daily plan),
        request: "request UUID"
    }
    :return:
    """

    global vrpProcessorReferenceSloCro
    global vrpProcessorReferenceElta

    """Main entry point for HTTP request"""
    received_request = request.get_json(force=True)

    # transforms received message for internal structures
    data = InputOutputTransformer.parse_received_recommendation_message(received_request)

    # needed for response handling
    request_id = received_request["request"]
    use_case = data['useCase']

    ##Errors
    if use_case != "SLO-CRO" and use_case != "ELTA":
        return {"message": "Parameter 'useCase' can have value 'SLO-CRO' or 'ELTA'."}
    if "useCase" not in data or "eventType" not in data:
        return {"message": "Parameter 'eventType' or 'useCase' is missing"}
    evt_type = data["eventType"]
    use_case = data["useCase"]

    ##Use Case SLO-CRO
    if use_case == "SLO-CRO":
        print("processing SLO-CRO use-case request")
        if vrpProcessorReferenceSloCro is None:     #initialize VRP
            vrpProcessorReferenceSloCro = RecReq.init_vrp(use_case)
        vrp_processor_ref = vrpProcessorReferenceSloCro

        # Extract 'clos' which should be a field in each request
        if "clos" not in data:
            return {"msg": "Parameter 'clos' is missing", "status": 0}
        clos = data["clos"]

        if evt_type == "brokenVehicle":
            if "clos" not in data or "brokenVehicle" not in data:
                return {"msg": "Parameter 'clos' or 'BrokenVehicle' is missing", "status": 0}
            broken_clo = data["brokenVehicle"]
            recommendations = RecReq.process_broken_clo(evt_type, clos, broken_clo, vrp_processor_ref, use_case)
        elif evt_type == "pickupRequest":
            if "clos" not in data or "orders" not in data:
                return {"msg": "Parameter 'clos' or 'orders' is missing", "status": 0}
            requests = data["orders"]
            recommendations = RecReq.process_pickup_requests(evt_type, clos, requests, vrp_processor_ref, use_case)

        elif evt_type == "crossBorder":
            print("cross border event received")
            if "clos" not in data:
                return {"msg": "Parameter 'clos' is missing", "status": 0}
            requests = []
            for clo in clos:
                parcels = clo["parcels"]
                for parcel in parcels:
                    parcel["currentLocation"] = clo["currentLocation"]
                    requests.append(parcel)
            recommendations = RecReq.process_cross_border_request(evt_type, clos, requests, vrp_processor_ref, use_case)
        else:
            return jsonify({"message": "Invalid event type: {}".format(evt_type), "status": 0})

        # Prepare output message from calculated recommendations
        response = InputOutputTransformer.prepare_output_message(recommendations, use_case, request_id)

        # This piece of code posts optimization response to MSB
        RecReq.post_response_msb(request_id, response)

        # Always return generic message stating that request was received and is due to be processed
        return generic_message_received_response

        ##Use Case ELTA
    elif use_case == "ELTA":
        print("processing ELTA usecase")
        ### VRP INICIALIZATION AND MESSAGE PREPROCESSING
        transform_map_dict = methods.get_orders_coordinates(data)
        if evt_type is None:
            data_request, data_CLOs = methods.proccess_elta_event(evt_type, data)
            res = process_new_CLOs_request(data_CLOs)  # make graph build
        else:
            data_request = methods.proccess_elta_event(evt_type, data)

        if vrpProcessorReferenceElta is None:     #initialize VRP
            vrpProcessorReferenceElta = RecReq.init_vrp(use_case)
        vrp_processor_ref = vrpProcessorReferenceElta

        if "clos" not in data_request:
            return {"msg": "Parameter 'clos' is missing", "status": 0}
        clos = data_request["clos"]

        ### MESSAGE PROCESSING ....
        if evt_type is None:
            if "orders" not in data_request:
                return {"msg": "Parameter 'orders' is missing", "status": 0}
            requests = data_request["orders"]
            recommendations = RecReq.process_pickup_requests(evt_type, clos, requests, vrp_processor_ref, use_case)
            response = InputOutputTransformer.prepare_output_message(
                methods.map_coordinates_to_response(recommendations, transform_map_dict), use_case, request_id)

        elif evt_type == "brokenVehicle":
            if "brokenVehicle" not in data_request:
                return {"msg": "Parameter 'BrokenVehicle' is missing", "status": 0}
            broken_clo = data_request["brokenVehicle"]
            recommendations = RecReq.process_broken_clo(evt_type, clos, broken_clo, vrp_processor_ref, use_case)
            recommendations_mapped = methods.map_coordinates_to_response(recommendations, transform_map_dict)
            response = InputOutputTransformer.prepare_output_message(recommendations_mapped, use_case, request_id)

        elif evt_type == "pickupRequest":
            if "orders" not in data_request:
                return {"msg": "Parameter 'orders' is missing", "status": 0}
            requests = data_request["orders"]
            recommendations = RecReq.process_pickup_requests(evt_type, clos, requests, vrp_processor_ref, use_case)
            response = InputOutputTransformer.prepare_output_message(recommendations, use_case, request_id)
        else:
            return jsonify({"msg": "Invalid event type: {}".format(evt_type), "status": 0})

        # This piece of code posts optimization response to MSB
        RecReq.post_response_msb(request_id, response)

        # Response is always a generic one which just states that CA received request and will process it.
        return generic_message_received_response

@app.route("/api/clo/newCLOs", methods=['POST'])
def new_clos():

    """
    API route used for handling request for newCLOs.
    This method checks if graph needs to be rebuilt or updated.
    """

    """Main entry point for HTTP request"""
    data = request.get_json(force=True)
    clos = data["clos"]  # Extract array of CLOs
    use_case = data["useCase"]
    # for ELTA only update the .csv list of of static locations
    if use_case == "ELTA":
        csv_file_path = config_parser.get_elta_path()
        with open(csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for json_obj in clos:
                csv_writer.writerow([json_obj["address"], json_obj["uuid"], json_obj["lat"], json_obj["lon"]])
        csv_file.close()
        return {"success": True}
    # for SLO-CRO create a new graph
    else:
        return process_new_CLOs_request(data)


class CognitiveAdvisorAPI:
    def __init__(self, port=5000, host="0.0.0.0"):
        self._port = port
        self._host = host

    def start(self):
        serve(app, host=self._host, port=self._port)
