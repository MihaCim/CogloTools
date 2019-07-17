import modules.middleware.event_processor as ca
import modules.middleware.test.api as api

class MockRemoteSIOT(ca.SIoT):

    async def get_vehicles_near(self, vehicle, location, vehicle_route):
        pass


class IntegrationTest:
    def __init__(self):
        awService = ca.NopAwarenessServices()


        self._advisor = ca.CaEventProcessor(awService, siot=MockRemoteSIOT(), storage=None, vehicle_routing=None)



if __name__ == '__main__':
    server = api.CognitiveAdvisorAPI()

    server.serve()

