import pytest

import modules.middleware.event_processor as ca

import numpy as np
from scipy.sparse import csc_matrix

class MockCaStorage(ca.CaStorage):

    def __init__(self):
        vehicle_ids = [5, 6, 7]
        location_ids = [10, 11, 12, 13, 14, 15]

        example_plan = ca.DistributionPlan(
            task_id=1,
            location_ids=location_ids,
            vehicle_ids=vehicle_ids,
            dropoff_matrix=np.array([
                [0.0, 0.0, 1.0, 0.5, 4.0, 0.0],
                [2.0, 3.0, 0.0, 0.0, 0.5, 0.0],
                [0.0, 0.0, 0.0, 0.5, 0.0, 3.0]
            ]),
            G=csc_matrix([
                [1, 0, 0, 0, 0, 0, 0],
                [1, 1, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 1, 0],
                [0, 0, 1, 0, 1, 0, 1],
                [0, 0, 0, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 1, 1]
            ])
        )

        self._vehicle_plan_map = {}
        self._plan_map = {
            example_plan.plan_id(): example_plan
        }

        for vehicle_id in vehicle_ids:
            self._vehicle_plan_map[vehicle_id] = example_plan


    async def get_plan_by_vehicle(self, vehicle_id):
        return self._vehicle_plan_map[vehicle_id]

    async def store_plan(self, plan):
        self._plan_map[plan.plan_id()] = plan

    def get_all_plans(self):
        return self._plan_map


class MockSiot(ca.SIoT):

    def __init__(self, vehicle_ids, vehicle_capacities, vehicle_loads):
        self._vehicle_ids = vehicle_ids
        self._vehicle_capacities = vehicle_capacities
        self._vehicle_loads = vehicle_loads

    async def get_vehicles_near(self, vehicle_id, vehicle_future_loc_ids):
        return self._vehicle_ids, self._vehicle_capacities, self._vehicle_loads


class MockVrp(ca.VRPlanner):

    async def calc_plan(self, graph_adjmat, vehicle_capacity_vec, dropoff_quantities):
        print('dropoff quantities: ' + str(dropoff_quantities))
        return np.array([
            [dropoff_quantities[0], dropoff_quantities[1], 0.0, 0.5*dropoff_quantities[3], dropoff_quantities[4], 0.0],
            [0.0, 0.0, dropoff_quantities[2], 0.5*dropoff_quantities[3], 0.0, dropoff_quantities[5]]
        ])



class TestCaSplit:

    @pytest.mark.asyncio
    async def test_basic(self):
        breakdown_vehicle_id = 5
        breakdown_location_id = 12

        available_vehicles = [6, 7]
        vehicle_capacities = [10.0, 10.0]
        vehicle_loads = [0.0, 0.0]

        awareness_services = ca.NopAwarenessServices()
        siot = MockSiot(available_vehicles, vehicle_capacities, vehicle_loads)
        storage = MockCaStorage()
        vrp = MockVrp()

        advisor = ca.CaEventProcessor(awareness_services, siot, storage, vrp)

        # result of the cognitive advisor
        global adjusted_plan
        adjusted_plan = None

        def on_plan_adjusted(plan):
            global adjusted_plan
            print('event fired')
            # global adjusted_plan
            adjusted_plan = plan

        advisor.on('plan-adjusted', on_plan_adjusted)

        # process the event
        event = ca.VehicleBreakdownEvent(
            breakdown_vehicle_id,
            breakdown_location_id
        )
        await advisor.process_event(event)

        assert adjusted_plan is not None

        vehicle_loads = adjusted_plan.vehicle_loads()

        assert vehicle_loads[0] == 2.0 + 3.0 + 0.5 + 4.5
        assert vehicle_loads[1] == 1.0 + 0.5 + 3.0
        assert len(storage.get_all_plans()) == 2

#         print('hello')
#         print(adjusted_plan)
