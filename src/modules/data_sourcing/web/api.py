from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import asyncio

from flask_jsonpify import jsonify
import modules.middleware.test.integration_test as it
import modules.middleware.event_processor as ca

processor = ca.CaEventProcessor(ca.NopAwarenessServices(), it.MockRemoteSIOT(), it.MockStorage(), it.MockVRP())

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

        evt = ca.VehicleBreakdownEvent(vehicle['vehicleId'], None, None)
        task = asyncio.ensure_future(processor.process_event(evt), loop=loop)

        print('processed')
        loop.run_until_complete(task)
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
        self._app.run(host='0.0.0.0',port=self._port)

    # ================================
    #  API ENDPOINTS
    # ================================


if __name__ == '__main__':
    server = CognitiveAdvisorAPI()

    server.serve()
