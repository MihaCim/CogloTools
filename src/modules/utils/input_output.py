from datetime import datetime
from ..create_graph.config.config_parser import ConfigParser
from ..utils.clo_update_handler import CloUpdateHandler

config_parser = ConfigParser()

ELTA_USE_CASE = "ELTA"
SLO_CRO_USE_CASE = "SLO-CRO"


class InputOutputTransformer:
    @staticmethod
    def clo(uuid, info, state):
        return {
            "UUID": uuid,
            "info": info,
            "state": state
        }

    @staticmethod
    def clo_info(organization, physical_id, type, subtype, description, location, capacity, capacity_unit, working_hours):
        return {
            "organization": organization,
            "physical_id": physical_id,
            "type": type,
            "subtype": subtype,
            "description": description,
            "location": location,
            "capacity": capacity,
            "capacity_unit": capacity_unit,
            "working_hours": working_hours
        }

    @staticmethod
    def location(lat, lon, address=None, postal_code=None, city=None, country=None):
        return {
            "address": address,
            "postal_code": postal_code,
            "city": city,
            "country": country,
            "lat": lat,
            "lon": lon
        }

    @staticmethod
    def parking(uuid, uuids):
        return {
            "container": uuid,
            "content": uuids
        }

    # Vehicle route
    @staticmethod
    def plan(uuid, organization, steps, execution_date=None):
        return {
            "id": uuid,
            "organization": organization,
            "execution_date": execution_date,
            "steps": steps
        }

    @staticmethod
    def recommendation(uuid, plan):
        return {
            "clo": uuid,
            "plan": plan
        }

    @staticmethod
    def parking(uuid, content):
        return {
            "container": uuid,
            "content": content
        }

    @staticmethod
    def itinerary(station, departure, arrival, cutoff):
        return {
            "station": station,
            "departure_time": departure,
            "arrival_time": arrival,
            "cutoff_time": cutoff
        }

    @staticmethod
    def schedule(weekday, start, end):
        return {
            "weekday": weekday,
            "start_time": start,
            "end_time": end
        }

    @staticmethod
    def postalbox_state(location, status, load_size, load_unit):
        return {
            "location": location,
            "status": status,
            "load_size": load_size,
            "load_unit": load_unit
        }

    @staticmethod
    def transportation_state(location, status, prediction, load_volume, available, capacity_unit, driver, plan, completed, remaining, delay):
        return {
            "location": location,
            "status": status,
            "availability_prediction": prediction,
            "load_volume": load_volume,
            "available_space": available,
            "capacity_unit": capacity_unit,
            "driver": driver,
            "plan": plan,
            "completed_plan": completed,
            "remaining_plan": remaining,
            "delay": delay
        }

    @staticmethod
    def parcel(organization, id, source_id, source_type, source_location, destination_id, destination_type, destination_location, service_type, payweight, issued, customs):
        return {
            "organization": organization,
            "id": id,
            "source_id": source_id,
            "source_type": source_type,
            "source_location": source_location,
            "destination_id": destination_id,
            "destination_type": destination_type,
            "destination_location": destination_location,
            "service_type": service_type,
            "payweight": payweight,
            "issued": issued,
            "customs_checkpoint": customs
        }

    @staticmethod
    def event(time, event_type, event, initiator, info):
        return {
            "time": time,
            "event_type": event_type,
            "event": event,
            "initiator": initiator,
            "info": info
        }

    @staticmethod
    def packing(container, content):
        return {
            "container": container,
            "content": content
        }

    @staticmethod
    def plan_step(id, rank, order, location, station, station_type, pack, unpack, load, unload, due_time, dependency):
        return {
            "id": id,
            "rank": rank,
            "order": order,
            "location": location,
            "station": station,
            "station_type": station_type,
            "pack": pack,
            "unpack": unpack,
            "load": load,
            "unload": unload,
            "due_time": due_time,
            "dependency": dependency
        }

    @staticmethod
    def parse_received_recommendation_message(json):
        payload = {
            "useCase": json["organization"],
            "UUIDRequest": json["request"],
        }

        # SLO-CRO use-case and it's parsing remained the same as it was before... we need example message before
        # changing the structure
        if json["organization"] == SLO_CRO_USE_CASE or json["organization"] == "PS" or json["organization"] == "HP":
            payload["useCase"] = SLO_CRO_USE_CASE
            if "event" not in json:
                payload["eventType"] = "pickupRequest"
            else:
                event = json["event"]
                if event is None:  # Procedure for daily plan is the same as for pickupRequest
                    payload["eventType"] = "pickupRequest"
                else:
                    payload["eventType"] = event["event_type"]
        elif json["organization"] == ELTA_USE_CASE:
            payload["useCase"] = ELTA_USE_CASE
            # None is used for dailyPlan
            if "event" not in json:
                payload["eventType"] = None
            else:
                event = json["event"]
                if event is None:
                    payload["eventType"] = None
                else:
                    payload["eventType"] = event["event_type"]

        clos = json["clos"]

        for clo in clos:
            clo["UUID"] = clo["id"]
            location = clo["info"].pop('location')

            if payload["useCase"] == SLO_CRO_USE_CASE:
                # Extract station ID from given 'latitude' and 'longitude'.
                csv_file = config_parser.get_csv_path(SLO_CRO_USE_CASE)
                location_station_dict = CloUpdateHandler.extract_location_station_dict(csv_file)
                station_id = location_station_dict[(str(location["latitude"]), str(location["longitude"]))]

                clo['currentLocation'] = station_id
            else:
                clo['currentLocation'] = [
                    location["latitude"],
                    location["longitude"]
                ]
            if "country" in location:
                clo['country'] = location["country"]
            clo['capacity'] = clo["info"].pop('capacity')

            # Check for state -> remaining_plan -> steps
            if "state" not in clo:
                clo["parcels"] = []
                continue
            if clo["state"] is None:
                clo["parcels"] = []
                continue
            if "remaining_plan" not in clo["state"]:
                clo["parcels"] = []
                continue
            if "steps" not in clo["state"]["remaining_plan"]:
                clo["parcels"] = []
                continue

            parcels = clo["state"]["remaining_plan"]["steps"]
            clo_parcels = []

            for parcel in parcels:
                parcel['UUIDParcel'] = parcel.pop('id')
                parcel['weight'] = parcel.pop('payweight')

                destination = parcel.pop('location')

                if payload["useCase"] == SLO_CRO_USE_CASE:
                    parcel['destination'] = destination["station"]
                else:
                    parcel['destination'] = [
                        destination["latitude"],
                        destination["longitude"]
                    ]
                if "country" in destination:
                    parcel['country'] = destination["country"]

                clo_parcels.append(parcel)

            clo["parcels"] = clo_parcels
        payload["clos"] = clos

        # TODO: This needs to be tested furthermore on examples provided by testers!!!
        if payload["eventType"] == "brokenVehicle":
            brokenVehicle = json["brokenVehicle"]

            current_location = brokenVehicle["info"].pop('location')

            if payload["useCase"] == SLO_CRO_USE_CASE:
                brokenVehicle["currentLocation"] = current_location["station"]
            else:
                brokenVehicle['currentLocation'] = [
                    current_location["latitude"],
                    current_location["longitude"]
                ]
            if "country" in current_location:
                brokenVehicle['country'] = current_location["country"]

            for parcel in brokenVehicle["parcels"]:
                parcel['UUIDParcel'] = parcel.pop('id')
                parcel['weight'] = parcel.pop('payweight')

                destination = parcel.pop('destination')
                if payload["useCase"] == SLO_CRO_USE_CASE:
                    parcel['destination'] = destination["station"]
                else:
                    parcel['destination'] = [
                        destination["latitude"],
                        destination["longitude"]
                    ]
                if "country" in destination:
                    parcel['country'] = destination["country"]

            payload["brokenVehicle"] = brokenVehicle
        else:
            orders = []
            if json["parcels"] is not None:
                orders = json["parcels"]

            for parcel in orders:
                parcel['UUIDParcel'] = parcel.pop('id')
                parcel['weight'] = parcel.pop('payweight')

                # Destination field is a JSON object
                destination = parcel.pop('destination')
                if payload["useCase"] == SLO_CRO_USE_CASE:
                    parcel['destination'] = destination["station"]
                else:
                    parcel['destination'] = [
                        destination["latitude"],
                        destination["longitude"]
                    ]
                if "country" in destination:
                    parcel['country'] = destination["country"]

                # Pickup field is a JSON object
                pickup = parcel.pop("source")
                if payload["useCase"] == SLO_CRO_USE_CASE:
                    parcel['pickup'] = pickup["station"]
                else:
                    parcel['pickup'] = [
                      pickup["latitude"],
                      pickup["longitude"]
                    ]
                if "country" in pickup:
                    parcel['country'] = pickup["country"]
            payload["orders"] = orders

        return payload

    @staticmethod
    def prepare_output_message(recommendations, use_case, request_id):
        # TODO: Replace location_id in messages to be in form of:
        # "location": { "latitude" : "xxx", "longitude": "xxx", "station": location_id}
        clo_plans = []

        counter = 0
        for clo_plan in recommendations:
            counter+=1
            recommendation_text = "%srecommendation%s" % (use_case, counter)
            message = {
                "clo": clo_plan["UUID"], # Vehicle
                "plan": {
                    "id": request_id,
                    "organization": use_case,
                    "execution_date": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    "recommendation": recommendation_text,
                    "steps": clo_plan["route"]
                }
            }
            clo_plans.append(message)

        return {
            "organization": use_case,
            "id": request_id,
            "cloplans": clo_plans
        }














