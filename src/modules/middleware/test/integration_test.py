import modules.middleware.event_processor as ca


class MockRemoteSIOT(ca.SIoT):

    async def get_vehicles_near(self, vehicle, vehicle_route):
        pass


class MockVRP(ca.VRPlanner):
    async def calc_plan(self):
        pass

class MockStorage(ca.CaStorage):
    async def get_plan_by_vehicle(self, vehicle_id):
        pass

    async def store_plan(self, plan):
        pass