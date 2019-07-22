from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import asyncio
import requests
from flask_jsonpify import jsonify

SIOT_URL = 'http://151.97.13.227:8080/SIOT-war/SIoT/Server/'
SIOT_URL = 'https://postman-echo.com/post'


class Event(Resource):

    def get(self):
        return jsonify({"success": True, "message": "Please use POST request"})

    def post(self):
        json = request.get_json(force=True)
        event = json['event']
        vehicle = json['vehicle']
        loop = asyncio.new_event_loop()
        print(json)
        if "broken" not in event['type']:
            return jsonify({
                "success": False,
                "message": "Event type " + event['type'] + " currently not supported"
            })

        data = requests.post(SIOT_URL + "newEvent", json=json)
        print(data.json())

        plan_payload = {
            "vehicles": [
                {
                    "UUID": "carflowF1",
                    "route": [
                        {
                            "locationId": 3,
                            "dropoffWeightKg": 130,
                            "dropoffVolumeM3": 5
                        },
                        {
                            "locationId": 5,
                            "dropoffWeightKg": 40,
                            "dropoffVolumeM3": 5
                        },
                        {
                            "locationId": 9,
                            "dropoffWeightKg": 30,
                            "dropoffVolumeM3": 1
                        },
                        {
                            "locationId": 12,
                            "dropoffWeightKg": 130,
                            "dropoffVolumeM3": 5
                        }
                    ]
                },
                {
                    "UUID": "carflowF3",
                    "route": [
                        {
                            "locationId": 13,
                            "dropoffWeightKg": 130,
                            "dropoffVolumeM3": 5
                        },
                        {
                            "locationId": 6,
                            "dropoffWeightKg": 40,
                            "dropoffVolumeM3": 5
                        },
                        {
                            "locationId": 13,
                            "dropoffWeightKg": 30,
                            "dropoffVolumeM3": 1
                        },
                        {
                            "locationId": 10,
                            "dropoffWeightKg": 130,
                            "dropoffVolumeM3": 5
                        }
                    ]
                }
            ]
        }

        plan_response = requests.post(SIOT_URL + "proposedPlan", json=plan_payload)
        print(plan_response.json())

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
