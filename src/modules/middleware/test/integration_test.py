import modules.middleware.event_processor as ca
import requests


class MockRemoteSIOT(ca.SIoT):

    # Make req to SIOT simulator
    async def send_event(self, event):
        url = None

        if url is not None:
            payload = {
                'event': {
                    'name': 'fault',
                    'type': 'delay/broken fire'
                },
                'vehicle': event.metadata.vehicle_id

            }

            data = requests.post(url, payload)

            # TODO parse data
            return data.json()['vehicles']
        else:
            return await self.get_vehicles_near(None, None)

    async def propose_plan(self, data):
        url = None

        if url is not None:
            payload = {
                "vehicles": [
                    {
                        "UUID": "92C199BD42E6None",
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
                        "UUID": "92C199BD42E6None",
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

            data = requests.post(url, payload)

    # Just mock some nearby vehicles
    async def get_vehicles_near(self, vehicle, dropoff_id, vehicle_route):
        vehicles = [
            {
                "vehicleId": 1,

                "metadata": {
                    "capacityM3": "10",
                    "capacityKg": "150",
                    "fuelCostKm": "1",
                    "currentLoadM3": "7",
                    "currentLoadKg": "110"

                }
            },
            {
                "vehicleId": 3,
                "metadata": {
                    "capacityM3": "10",
                    "capacityKg": "150",
                    "fuelCostKm": "1",
                    "currentLoadM3": "7",
                    "currentLoadKg": "110"
                }
            },
            {
                "vehicleId": 3,

                "metadata": {
                    "capacityM3": "10",
                    "capacityKg": "150",
                    "fuelCostKm": "1",
                    "currentLoadM3": "7",
                    "currentLoadKg": "110"
                }
            }
        ]

        return [v['vehicleId'] for v in vehicles], \
               [v['metadata']['capacityKg'] for v in vehicles], \
               [v['metadata']['currentLoadKg'] for v in vehicles]


class MockVRP(ca.VRPlanner):
    async def calc_plan(self):
        pass


class MockStorage(ca.CaStorage):
    def __init__(self):
        self._plans = {}

    async def get_plan_by_vehicle(self, vehicle_id):
        return self._plans[vehicle_id]

    async def store_plan(self, plan):
        self._plans[plan['UUID']] = plan['dropOffLocations']
