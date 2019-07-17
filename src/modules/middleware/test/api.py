from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from json import dumps

from flask_jsonpify import jsonify

import modules.middleware.event_processor as ca

processor = ca.CaEventProcessor(ca.NopAwarenessServices(), None, None, None)


class Event(Resource):

    def post(self):
        json = request.get_json(force=True)
        event = json['event']
        vehicles = json['vehicles']

        if "broken" not in event['type']:
            return jsonify({
                "success": False,
                "message": "Event type " + event['type'] + " currently not supported"
            })

        for vehicle in vehicles:
            evt = ca.VehicleBreakdownEvent(vehicle['UUID'], vehicle['metadata'], vehicle['dropOffLocation'])
            processor.process_event(evt)
        print(json)
        return jsonify({
            "success": True,
            "message": "Processing " + len(vehicles) + " events"
        })


class CognitiveAdvisorAPI:
    def __init__(self, port=5000):
        self._port = port
        self._app = Flask(__name__)
        self._api = Api(self._app)
        self._add_endpoints()

    def _add_endpoints(self):
        self._register_endpoint('/api/adhoc/newEvent', Event)

    def _register_endpoint(self, endpoint_name, class_ref):
        self._api.add_resource(class_ref, endpoint_name)

    def serve(self):
        self._app.run(port=self._port)

    # ================================
    #  API ENDPOINTS
    # ================================


if __name__ == '__main__':
    server = CognitiveAdvisorAPI()

    server.serve()
