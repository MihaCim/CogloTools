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

    # Just mock some nearby vehicles
    async def get_vehicles_near(self, vehicle, vehicle_route):
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

        return vehicles


class MockVRP(ca.VRPlanner):
    async def calc_plan(self):
        pass


class MockStorage(ca.CaStorage):
    async def get_plan_by_vehicle(self, vehicle_id):
        pass

    async def store_plan(self, plan):
        pass
