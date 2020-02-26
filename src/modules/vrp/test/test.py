import requests
import json

if __name__ == '__main__':
    E = [
        [-1, -1,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0],
        [ 1,  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  1, -1, -1, -1,  1,  0,  0,  1,  0],
        [ 0,  0,  0,  0,  0,  1,  0, -1, -1,  0,  0,  1],
        [ 0,  1,  0,  0,  0,  0,  1,  0,  1, -1, -1, -1]
    ]

    X = [
        [ 1,  1,  1,  0,  0,  1,  0,  0,  1,  1,  1,  0],
        [ 0,  1,  1,  0,  1,  0,  0,  1,  0,  0,  0,  1]
    ]

    C_edge = [
        [ 6,  1,  6,  6,  6,  1,  1,  1,  1,  1,  1,  1],
        [ 6,  1,  6,  6,  6,  1,  1,  1,  1,  1,  1,  1]
    ]

    edge_time_vec = [ 1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1]

    start_vec = [1, 1]
    end_vec = [1, 1]

    distrib_vec = [0, 4, 3, 4, 3]
    capacity_vec = [10, 10]

    t_start_vec = [0, 0, 0, 0, 0]
    t_end_vec = [10, 10, 10, 10, 10]

    req_json = {
        'incidenceMat': E,
        'costMat': C_edge,
        'edgeTimeV': edge_time_vec,
        'startV': start_vec,
        'endV': end_vec,
        'nodeDistributionV': distrib_vec,
        'vehicleCapacityV': capacity_vec,
        'nodeOpenV': t_start_vec,
        'nodeCloseV': t_end_vec
    }

    response = requests.post(url='http://localhost:4504/api/vrptw', json=req_json)

    status_code = response.status_code
    if status_code < 200 or 300 <= status_code:
        print('Request failed! Status code: ' + str(status_code))
    else:
        content_str = response.content
        content_json = json.loads(content_str)

        print('received response: ' + json.dumps(content_json))
