import csv
import json
import os
import requests

from flask import Flask, request
from flask_jsonpify import jsonify
from flask_restful import Resource
#from jsonschema import ValidationError
from waitress import serve

#from .ErrorHandling import ErrorHandling
from ..create_graph.config.config_parser import ConfigParser
from ..create_graph.create_graph import JsonGraphCreator
from ..create_graph.methods import methods
from ..cvrp.processor.vrp_processor import VrpProcessor
from ..partitioning.graph_partitioning_preprocess import GraphPreprocessing
from ..utils.clo_update_handler import CloUpdateHandler
from ..utils.input_output import InputOutputTransformer
from ..utils.tsp import Tsp

app = Flask(__name__)
vrpProcessorReferenceSloCro = None
vrpProcessorReferenceElta = None

config_parser = ConfigParser()
msb_post_url = "https://msb.cog-lo.eu/api/publish"
response_validation_url = "http://db.cog-lo.eu/postRecommendation"
recommendation_post_verification_url = "http://116.203.13.198/api/postRecommendation"
planner_tsp_api_url = "localhost:1234/api/tsp"

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

        return vrp_processor_ref.process(vehicles, deliveries, evt_type, use_case)

    @staticmethod
    def process_broken_clo(evt_type, clos, broken_clo, vrp_processor_ref, use_case):
        print("Processing Broken CLO for ", len(clos), 'vehicles')
        vehicles = vrp_processor_ref.parse_vehicles(clos)
        deliveries = vrp_processor_ref.parse_deliveries(evt_type, clos, broken_clo, use_case)

        return vrp_processor_ref.process(vehicles, deliveries, evt_type, use_case)

    @staticmethod
    def process_cross_border_request(evt_type, clos, requests, vrp_processor_ref, use_case):
        print("Processing Cross Border Delivery Request for ", len(clos), 'vehicles')
        vehicles = vrp_processor_ref.parse_vehicles(clos)
        deliveries = vrp_processor_ref.parse_deliveries(evt_type, clos, requests, use_case)

        return vrp_processor_ref.process(vehicles, deliveries, evt_type, use_case)

    @staticmethod
    def post_response_msb(UUID, recommendations):
        # default=str set because we want to serialize Date objects as well
        json_for_serialization = {
            "recommendation": recommendations
        }
        headers = {'Content-type': 'application/json'}
        content = {
            "request": UUID,
            "topic": "recommendations",
            "sender": "COGLOmoduleCA",
            "message": json_for_serialization
        }

        print("Storing message for validation service...")
        with open('validation_service_message_posted.json', 'w') as outfile:
            json.dump(recommendations, outfile)

        print("Storing message content posted...")
        with open('content_message_posted.json', 'w') as outfile:
            json.dump(content, outfile)

        #print("posting response to validation URL: " + response_validation_url)
        #print(recommendations)
        #try:
        #    response = requests.post(response_validation_url, json = recommendations, headers=headers, verify=False).json()
        #    print("validation code for recommendations message: ", response)
        #except Exception as ex:
        #    print("Error occurred while validating response in validation service", ex)

        print("posting to MSB post URL: " + msb_post_url)
        print(content)

        try:
            response = requests.post(msb_post_url, json = content, headers=headers, verify=False)
            print("response from MSB:", response)
        except Exception as ex:
            print("Error occurred while posting response to MSB", ex)

@app.route("/api/adhoc/getRecommendation", methods=['POST'])
def handle_recommendation_request():
    # TODO: Make generic_message_received_response synchronous and all other operations asynchronous

    global vrpProcessorReferenceSloCro
    global vrpProcessorReferenceElta

    transformation_map = LocationParcelMap()

    """Main entry point for HTTP request"""
    received_request = request.get_json(force=True)
    #Error Handling
    """try:
        ErrorHandling.check_messages_correction(received_request)
    except ValidationError as error:
        return str(error)
    """
    with open('received_request.json', 'w') as outfile:
        json.dump(received_request, outfile)

    print("received getRecommendation request", received_request)

    # transforms received message for internal structures
    try:
        data = InputOutputTransformer.parse_received_recommendation_message(
            received_request, transformation_map)
    except ValueError as error:
        return str(error)

    # needed for response handling
    request_id = received_request["request"]
    use_case = data['useCase']
    organization = received_request["organization"]

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
            if "clos" not in data or "orders" not in data:
                return {"msg": "Parameter 'clos' or 'orders' is missing", "status": 0}
            broken_clo_orders = data["orders"]
            recommendations = RecReq.process_broken_clo(evt_type, clos, broken_clo_orders, vrp_processor_ref, use_case)
        elif evt_type == "pickupRequest":
            if "clos" not in data or "orders" not in data:
                return {"msg": "Parameter 'clos' or 'orders' is missing", "status": 0}
            requests = data["orders"]
            recommendations = RecReq.process_pickup_requests(evt_type, clos, requests, vrp_processor_ref, use_case)
        elif evt_type == "crossBorder" or "border":
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

        # Map parcel locations back to the original ones
        #recommendations_raw = InputOutputTransformer.revert_coordinates(recommendations, transformation_map)

        print("starting final reordering & TSP")
        recommendations = InputOutputTransformer.PickupNodeReorder(recommendations)

        # print route for all vehicles
        P=InputOutputTransformer.PrintRoutes(recommendations)
        # Prepare output message from calculated recommendations
        response = InputOutputTransformer.prepare_output_message(recommendations, use_case, request_id, organization)

        # Post response to MSB
        RecReq.post_response_msb(request_id, response)
        # Return generic message stating that request was received and is due to be processed
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
            data_requests = data_request["orders"]
            recommendations = RecReq.process_pickup_requests(evt_type, clos, data_requests, vrp_processor_ref, use_case)
        elif evt_type == "brokenVehicle":
            if "clos" not in data or "orders" not in data:
                return {"msg": "Parameter 'clos' or 'orders' is missing", "status": 0}
            broken_clo_orders = data_request["orders"]
            recommendations = RecReq.process_broken_clo(evt_type, clos, broken_clo_orders, vrp_processor_ref, use_case)
        elif evt_type == "pickupRequest":
            if "orders" not in data_request:
                return {"msg": "Parameter 'orders' is missing", "status": 0}
            data_requests = data_request["orders"]
            recommendations = RecReq.process_pickup_requests(evt_type, clos, data_requests, vrp_processor_ref, use_case)
        else:
            return jsonify({"msg": "Invalid event type: {}".format(evt_type), "status": 0})

        print("starting final reordering & TSP")
        recommendations = InputOutputTransformer.PickupNodeReorder(recommendations)

        # print route for all vehicles
        P = InputOutputTransformer.PrintRoutes(recommendations)


        # Maps recommendations based on transform_map_dict
        recommendations_mapped = methods.map_coordinates_to_response(recommendations, transform_map_dict)

        # Transforms response in 'JSI' format to the one used for MSB
        response1 = InputOutputTransformer.prepare_output_message(recommendations_mapped, use_case, request_id, organization)

        # restructures steps plan and and lists all the parcels from clusters as a list of locations
        response = methods.order_parcels_on_route(response1)

        # This piece of code posts optimization response to MSB
        #RecReq.post_response_msb(request_id, response)

        # Response is always a generic one which just states that CA received request and will process it.
        #return generic_message_received_response
        return response

@app.route("/api/clo/newCLOs", methods=['POST'])
def new_clos():
    """
    API route used for handling request for newCLOs.
    This method checks if graph needs to be rebuilt or updated.

    Example request:
    {
      "clos": [
        {
          "id": "PSpostofficeS1",
          "info": {
            "name": "Kapele",
            "type": "station",
            "subtype": "post office",
            "organization": "PS",
            "physical_id": "S1",
            "location": {
              "latitude": 45.93107932,
              "longitude": 15.67793203,
              "country": "SLO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "PSpostofficeS2",
          "info": {
            "name": "Globoko",
            "type": "station",
            "subtype": "post office",
            "organization": "PS",
            "physical_id": "S2",
            "location": {
              "latitude": 45.95503619,
              "longitude": 15.63656969,
              "country": "SLO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "PSpostofficeS3",
          "info": {
            "name": "Jesenice",
            "type": "station",
            "subtype": "post office",
            "organization": "PS",
            "physical_id": "S3",
            "location": {
              "latitude": 45.85945758,
              "longitude": 15.68964069,
              "country": "SLO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "PSpostofficeS4",
          "info": {
            "name": "Topliska cesta",
            "type": "station",
            "subtype": "post office",
            "organization": "PS",
            "physical_id": "S4",
            "location": {
              "latitude": 45.89320611,
              "longitude": 15.6212996,
              "country": "SLO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "PSpostofficeS5",
          "info": {
            "name": "Cerklje ob Krki",
            "type": "station",
            "subtype": "post office",
            "organization": "PS",
            "physical_id": "S5",
            "location": {
              "latitude": 45.88461153,
              "longitude": 15.5231045,
              "country": "SLO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "PSpostofficeS6",
          "info": {
            "name": "Ulica 11. novembra",
            "type": "station",
            "subtype": "post office",
            "organization": "PS",
            "physical_id": "S6",
            "location": {
              "latitude": 45.942039,
              "longitude": 15.478103,
              "country": "SLO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "PSpostofficeS7",
          "info": {
            "name": "Kriska vas",
            "type": "station",
            "subtype": "post office",
            "organization": "PS",
            "physical_id": "S7",
            "location": {
              "latitude": 45.89123853,
              "longitude": 15.57086927,
              "country": "SLO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "PSpostofficeS8",
          "info": {
            "name": "Ulica stare pravde",
            "type": "station",
            "subtype": "post office",
            "organization": "PS",
            "physical_id": "S8",
            "location": {
              "latitude": 45.90488128,
              "longitude": 15.59338439,
              "country": "SLO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "PSpostofficeS9",
          "info": {
            "name": "Ulica bratov Gerjovicev",
            "type": "station",
            "subtype": "post office",
            "organization": "PS",
            "physical_id": "S9",
            "location": {
              "latitude": 45.89504865,
              "longitude": 15.66006978,
              "country": "SLO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "HPpostofficeH1",
          "info": {
            "name": "Ul. ?ure Basari?eka 9",
            "type": "station",
            "subtype": "post office",
            "organization": "HP",
            "physical_id": "H1",
            "location": {
              "latitude": 45.839828,
              "longitude": 15.68643,
              "country": "CRO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "HPpostofficeH2",
          "info": {
            "name": "Ul. Ljudevita Gaja 4",
            "type": "station",
            "subtype": "post office",
            "organization": "HP",
            "physical_id": "H2",
            "location": {
              "latitude": 45.803142,
              "longitude": 15.710135,
              "country": "CRO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "HPpostofficeH3",
          "info": {
            "name": "Gori?ka 1",
            "type": "station",
            "subtype": "post office",
            "organization": "HP",
            "physical_id": "H3",
            "location": {
              "latitude": 45.917165,
              "longitude": 15.730056,
              "country": "CRO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "HPpostofficeH4",
          "info": {
            "name": "Ul. Dr. Franje Tu?mana 38a",
            "type": "station",
            "subtype": "post office",
            "organization": "HP",
            "physical_id": "H4",
            "location": {
              "latitude": 45.808406,
              "longitude": 15.816847,
              "country": "CRO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "HPpostofficeH5",
          "info": {
            "name": "Zagreba?ka ul. 45",
            "type": "station",
            "subtype": "post office",
            "organization": "HP",
            "physical_id": "H5",
            "location": {
              "latitude": 45.887335,
              "longitude": 15.697116,
              "country": "CRO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "HPpostofficeH6",
          "info": {
            "name": "Ul. Drage ?vajcara 5",
            "type": "station",
            "subtype": "post office",
            "organization": "HP",
            "physical_id": "H6",
            "location": {
              "latitude": 45.859075,
              "longitude": 15.80341,
              "country": "CRO"
            }
          },
          "state": {
            "status": 1.0
          }
        },
        {
          "id": "HPpostofficeH7",
          "info": {
            "name": "Zagreba?ka ul. 29",
            "type": "station",
            "subtype": "post office",
            "organization": "HP",
            "physical_id": "H9",
            "location": {
              "latitude": 45.878072,
              "longitude": 15.739208,
              "country": "CRO"
            }
          },
          "state": {
            "status": 1.0
          }
        }
      ],
      "useCase": "SLO-CRO"
    }

    """
    """Main entry point for HTTP request"""
    data = request.get_json(force=True)

    print("newCLOs request arrived with payload:", data)

    clos = data["clos"]  # Extract array of CLOs

    # Check for non empty array
    if len(clos) < 1:
        return {
            "status": -1,
            "msg": "List of 'clos' should have at least one field."
        }
    first_clo = clos[0]["info"]
    use_case = first_clo["organization"]

    # for ELTA only update the .csv list of of static locations
    if use_case == "ELTA":
        csv_file_path = config_parser.get_elta_path()
        with open(csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for json_obj in clos:
                # Extract CLO ID and it's location object. Location object should have fields 'address',
                # 'latitude' and 'longitude'
                id = json_obj["id"]
                info_obj = json_obj["info"]
                location = info_obj["location"]

                # Write rows
                csv_writer.writerow([location["address"], id, location["latitude"], location["longitude"]])
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


class LocationParcelMap:
    """
    Class used for storing location for each parcel ID.
    """
    def __init__(self):
        self.dict = {}

    def map(self, key, location):
        self.dict[key] = location

    def keys(self):
        return self.dict.keys()

    def get(self, key):
        return self.dict[key]