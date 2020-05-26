from datetime import date

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
        event = json["event"]
        payload = {
            "useCase": json["organization"],
            "UUIDRequest": json["request"],
        }

        if json["organization"] == "SLO-CRO":
            if event["event_type"] is None:  ##when dailiy plan processing we do same as for pickup request
                payload["eventType"] = "pickupRequest"
            else:
                payload["eventType"] = event["event_type"]
            CLOS = json["CLOS"]
            for clo in CLOS:

                clo['currentLocation'] = clo["info"].pop('locationId')
                clo["capacity"] = clo["info"].pop('capacity')
                for parcel in clo["parcels"]:
                    parcel['UUIDParcel'] = parcel.pop('id')
                    parcel['weight'] = parcel.pop('payweight')
                    parcel['destination'] = parcel.pop('destination_id')
                payload["CLOS"] = CLOS
            if event["event_type"] == "brokenVehicle":
                brokenVehicle = json["brokenVehicle"]
                brokenVehicle['currentLocation'] = brokenVehicle["info"].pop('locationId')
                for parcel in brokenVehicle["parcels"]:
                    parcel['UUIDParcel'] = parcel.pop('id')
                    parcel['weight'] = parcel.pop('payweight')
                    parcel['destination'] = parcel.pop('destination_id')
                payload["brokenVehicle"] = brokenVehicle
            else:

                ORDERS = json["orders"]
                for parcel in ORDERS:
                    parcel['UUIDParcel'] = parcel.pop('id')
                    parcel['weight'] = parcel.pop('payweight')
                    parcel['destination'] = parcel.pop('destination_id')
                    parcel['pickup'] = parcel.pop('source_location')
                payload["orders"] = ORDERS

        elif json["organization"] == "ELTA":
            CLOS = json["CLOS"]
            payload["eventType"] = event["event_type"]
            for clo in CLOS:
                clo['currentLocation'] = clo["info"].pop('location')
                clo['capacity'] = clo["info"].pop('capacity')
                for parcel in clo["parcels"]:
                    parcel['UUIDParcel'] = parcel.pop('id')
                    parcel['weight'] = parcel.pop('payweight')
                    parcel['destination'] = parcel.pop('destination_location')
                payload["CLOS"] = CLOS
            if event["event_type"] == "brokenVehicle":
                brokenVehicle = json["brokenVehicle"]
                brokenVehicle['currentLocation'] = brokenVehicle["info"].pop('location')
                for parcel in brokenVehicle["parcels"]:
                    parcel['UUIDParcel'] = parcel.pop('id')
                    parcel['weight'] = parcel.pop('payweight')
                    parcel['destination'] = parcel.pop('destination_location')
                payload["brokenVehicle"] = brokenVehicle
            else:
                ORDERS = json["orders"]
                for parcel in ORDERS:
                    parcel['UUIDParcel'] = parcel.pop('id')
                    parcel['weight'] = parcel.pop('payweight')
                    parcel['destination'] = parcel.pop('destination_location')
                    parcel['pickup'] = parcel.pop('source_location')
                payload["orders"] = ORDERS

        return payload

    @staticmethod
    def prepare_output_message(recommendations, use_case, request_id):
        messages = []
        for clo_plan in recommendations:
            message = {
                "id": request_id,
                "organization": use_case,
                "execution_date": date.today(),
                "steps": clo_plan
            }
            messages.append(message)

        return {
            "status": 1,
            "msg": messages
        }














