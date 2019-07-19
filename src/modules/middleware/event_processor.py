from abc import ABC, abstractmethod
import numpy as np

#=======================================
# INTERFACES
#=======================================

class AwarenessServices(ABC):

    @abstractmethod
    async def classify_event(self, event):
        pass

class SIoT(ABC):

    @abstractmethod
    async def get_vehicles_near(self, vehicle, location, vehicle_route):
        pass

    @abstractmethod
    async def send_event(self, event):
        pass

    async def propose_plan(self, data):
        pass

class CaStorage(ABC):

    @abstractmethod
    async def store_plan(self, plan):
        pass

    @abstractmethod
    async def get_plan_by_vehicle(self, vehicle_id):
        pass

class VRPlanner(ABC):

    @abstractmethod
    async def calc_plan(self):
        pass
#=======================================
# INITIAL IMPLEMENTATIONS
#=======================================

class NopAwarenessServices(AwarenessServices):

    async def classify_event(self, event):
        return event

#=======================================
# OBJECTS
#=======================================


curr_plan_id = -1

def gen_plan_id():
    global curr_plan_id
    curr_plan_id += 1
    return curr_plan_id

class DistributionPlan:

    def __init__(self, task_id, location_ids, vehicle_ids, dropoff_matrix, G, previous_plan_id=None):
        self._task_id = task_id
        self._plan_id = gen_plan_id()
        self._previous_plan_id = previous_plan_id if previous_plan_id is not None else self._plan_id

        self._location_ids = location_ids
        self._vehicle_ids = vehicle_ids

        self._id2idx_vehicle = {vehicle_ids[vehicleN]: vehicleN for vehicleN in range(len(vehicle_ids))}

        # the distribution matrix is a matrix of shape k x n where k is the number of vehicles
        # and n is the number of dropoff locations
        # each entry D_ij tells how much cargo vehicle i will drop off at location j
        self._dropoff_matrix = dropoff_matrix
        # self._dropoff_quantities = []
        self._G = G

        print('created plan: ' + str(dropoff_matrix))

    def create_adjusted(self, dropoff_matrix):
        return DistributionPlan(
            self._task_id,
            self._location_ids,
            self._vehicle_ids,
            dropoff_matrix,
            self._G,
            previous_plan_id=self._previous_plan_id
        )

    def plan_id(self):
        return self._plan_id

    def infrastructure_topology(self):
        '''

        Returns the internal representation of the logistics infrastructure. This
        representation can be used to generate various other representations like
        the sparse matrix for the grph partitioning algorithm or the matrix for
        VRP.

        '''
        return self._G

    def routing_graph(self):
        '''

        Returns a weighted graph of the infrastructre which can be used
        by the VRP algorithm.

        '''
        return self._G

    def dropoff_quantities(self):
        k = len(self._vehicle_ids)

        #
        #          [d11 d12 d13 ...]
        # [1  1] * [d21 d22 d23 ...] = [d11+d21 d12+d22 ...]
        ones_k = np.ones(k)
        dropoff_vec = np.dot(ones_k, self._dropoff_matrix)

        return dropoff_vec

    def vehicle_loads(self):
        n = len(self._location_ids)

        ones_n = np.ones(n)
        vehicle_loads = np.dot(self._dropoff_matrix, ones_n)

        return vehicle_loads

    def get_route_location_ids(self, vehicle_id):
        '''

        Returns a list of locations (specified by location ID) that the
        vehicle is going to visit.

        '''

        cols = len(self._location_ids)

        rowN = self._id2idx_vehicle[vehicle_id]

        location_ids = []
        for colN in range(cols):
            if self._dropoff_matrix[rowN][colN] > 0.0:
                location_id = self._location_ids[colN]
                location_ids.append(location_id)

        return location_ids

#=======================================
# EVENTS
#=======================================

class VehicleBreakdownEvent:

    type = 'vehicle-breakdown'

    def __init__(self, vehicle_id, metadata, route):
        self.metadata = {
            'vehicle_id': vehicle_id,
            'route': route,
            'metadata': metadata,
            'last_visited_location_id': 0
        }

#=======================================
# EVENT PROCESSOR
#=======================================

class CaEventProcessor:

    '''

    The Congitive Advisor Event Processor component is the main orchestrator in the
    Cognitive Advisor system.

    It orchestrates the COG-LO Awareness Services, Digita State Representation
    Services, Knowledge Formalization Services, and Distributed Intelligence Services.

    '''

    def __init__(self, awareness_services, siot, storage, vehicle_routing):
        self._awareness_services = awareness_services
        self._siot = siot
        self._storage = storage
        self._vehicle_routing = vehicle_routing

        # functions for processing specific event types
        self._event_processors = {
            VehicleBreakdownEvent.type: self._process_truck_breakdown
        }
        self._event_handlers = {
            'plan-adjusted': []
        }


    async def process_event(self, event):
        event_data = await self._awareness_services.classify_event(event)

        event_type = event_data.type
        event_metadata = event_data.metadata

        print('processing an event of type: ' + event_type)

        event_processor = self._event_processors[event_type]
        if event_processor is None:
            raise ValueError('Invalid event type: ' + event_type)

        await event_processor(event_metadata)

    async def _process_truck_breakdown(self, event_data):
        '''

        A handler function for the `truck-breakdown` event. The
        function first searches for alternative trucks and then
        creates a new plan taking into account the new trucks.
        The new plan is output as a `plan-adjusted` event.

        '''
        print('processing a vehicle breakdown event')

        vehicle_id = event_data['vehicle_id']
        last_dropoff_id = event_data['last_visited_location_id']

        print('fetching current distribution plan')
        #await self._storage.store_plan({'UUID': vehicle_id, 'dropOffLocations': event_data['route'] })

        #previous_plan = await self._storage.get_plan_by_vehicle(vehicle_id)
        # vehicle_route = previous_plan.get_route_location_ids(vehicle_id)
        vehicle_route = None
        print('fetching nearby vehicles')


        new_vehicles, new_capacities, new_loads = await self._siot.get_vehicles_near(
            vehicle_id,
            last_dropoff_id,
            vehicle_route
        )

        #TODO refactor vehicles

        new_plan = None
        await self._siot.propose_plan(new_plan)
        return

        print('constructing VRP constraints')
        # get the capacity of each vehicle
        routing_graph = previous_plan.routing_graph()
        vehicle_capacities = np.subtract(new_capacities, new_loads)
        dropoff_quantities = previous_plan.dropoff_quantities()

        print('vehicle capacities: ' + str(vehicle_capacities))

        # calc a new dropoff plan, the result is a matrix k x n, where k is
        # the number of vehicles and n is the number of locations
        new_dropoff_matrix = await self._vehicle_routing.calc_plan(
            routing_graph,
            vehicle_capacities,
            dropoff_quantities
        )

        print('storing the new plan')
        new_plan = previous_plan.create_adjusted(new_dropoff_matrix)
        await self._storage.store_plan(new_plan)

        print('notifying plan change')
        await self._fire_event('plan-adjusted', new_plan)

    #==================================
    # OUTPUT EVENTS
    #==================================

    async def _fire_event(self, event_id, event):
        if event_id not in self._event_handlers:
            raise ValueError('Invalid event: ' + event_id)
        print('firing event: ' + event_id)
        handlers = self._event_handlers[event_id]
        for handler in handlers:
            try:
                handler(event)
            except ValueError:
                print("An exception while processing event: " + event_id)

    def on(self, event_id, handler):
        if event_id not in self._event_handlers:
            raise ValueError('Invalid event: ' + event_id)
        self._event_handlers[event_id].append(handler)
