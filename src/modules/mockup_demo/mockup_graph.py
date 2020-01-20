import json
from math import sin, cos, sqrt, atan2, radians, inf
from modules.mockup_demo.mockup_partitioning import MockupPartitioning

class MockupGraph:

    def __init__(self, path):
        self.nodes, self.edges = self.__load_graph(path)


    def __load_graph(self, path):
        with open(path, "r") as read_file:
            data = json.load(read_file)
            print(data)
            edges = data["edge"]
            nodes = data["nodes"]
        return (nodes, edges)

    def __distance(self, latitude1, longitude1, latitude2, longitude2):
        # approximate radius of earth in km
        R = 6373.0

        lat1 = radians(latitude1)
        lon1 = radians(longitude1)
        lat2 = radians(latitude2)
        lon2 = radians(longitude2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

    def get_graph(self):
        node_array = []
        edge_array = []
        incident_matrix = []
        for index, node in enumerate(self.edges):
            edge_array.append(str(node[0]) + "_" + str(node[1]))

        for key, value in self.nodes.items():
            node_array.append(value["node_id"])
            # print(key)
            # print(value[])
            tmp_arr = [0] * len(self.edges)
            for index, node in enumerate(self.edges):

                if value["node_id"] == node[0] or value["node_id"] == node[1]:
                    tmp_arr[index] = 1
            incident_matrix.append(tmp_arr)

        return (node_array, edge_array, incident_matrix)

    def map_truck(self, trucks):
        map_trucks = []
        for truck in trucks:
            min = inf
            id  = inf
            for key, value in self.nodes.items():
                dist =self.__distance(truck['latitude'], truck['longitude'], value['lat'], value['lon'])
                if dist < min:
                    min = dist
                    id = value['node_id']
            map_trucks.append([truck['id'], id])
        return map_trucks

if __name__ == "__main__":

    mg = MockupGraph("../../atene_south.json")
    print(mg.get_graph())
    trucks = json.loads("[{\"id\": \"carflowF1\", \"latitude\": 43.5104144, \"longitude\": 16.4390596}, "
                        "{\"id\": \"carflowF3\", \"latitude\": 43.5124174, \"longitude\": 16.4322733}]")

    #print(mg.map_truck(trucks))
    #mp = MockupPartitioning(mg.nodes, mg.edges)
    #mp.partitioning_graph()




