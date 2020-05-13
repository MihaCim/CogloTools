import csv
from sklearn.cluster import KMeans
import pandas as pd
from ..config.config_parser import ConfigParser
import copy
config_parser = ConfigParser()

def proccess_elta_event(proc_event, data):
    if proc_event==None:
        return elta_clustering(data)
    elif proc_event=='pickup':
        return elta_map_parcels(data)

def elta_clustering(orig_data):
    data = copy.deepcopy(orig_data)
    l = []
    for el in data['orders']:
        l.append([el['UUIDParcel'], "destination"] + el['destination'])
        l.append([el['UUIDParcel'], "pickup"] + el['pickup'])
    df = pd.DataFrame(l)
    # run clustering
    kmeans = KMeans(n_clusters=5)
    kmeans.fit(df[[2, 3]])  # Compute k-means clustering.
    centers = kmeans.cluster_centers_
    df["labels"] = labels = kmeans.labels_
    for index, row in df.iterrows():
        data['orders'][index // 2][row[1] + '_location'] = data['orders'][index // 2][row[1]]
        data['orders'][index // 2][row[1]] = str(row['labels'])

    clos = {"useCase": "ELTA"}
    clos_list = []
    i = 0
    for row in centers:
        clos_list.append({
            "uuid": str(i),
            "address": "address",
            "lat": row[0],
            "lon": row[1]
        })
        i = i + 1
    clos["CLOS"] = clos_list
    return data, clos

def find_min(lat_cord, lon_cord):
    elta = config_parser.get_csv_path("ELTA")
    posts = []
    with open(elta) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            posts.append([row[1], (row[2], row[3])])
    import sys
    cur_max = sys.maxsize
    label = -1
    for post in posts:
        lat = float(lat_cord) - float(post[1][0])
        lon = float(lon_cord) - float(post[1][1])
        m = (lat * lat) + (lon * lon)
        if m < cur_max:
            cur_max = m
            label = post[0]
    return label


def elta_map_parcels(orig_data):
    data = copy.deepcopy(orig_data)
    for clo in data['CLOS']:
        m = find_min(clo['currentLocation'][0], clo['currentLocation'][1])
        clo['currentLocation'] = m
        clo['currentLocationL'] = clo['currentLocation']
        for parcel in clo['parcels']:
            m = find_min(parcel['destination'][0], parcel['destination'][1])
            parcel['destination_location'] = parcel['destination']
            parcel['destination'] = m
            print(m)

    for clo in data['orders']:
        m = find_min(clo['destination'][0], clo['destination'][1])
        clo['destination_location'] = clo['destination']
        clo['destination'] = m

        m = find_min(clo['pickup'][0], clo['pickup'][1])
        clo['pickup_location'] = clo['pickup']
        clo['pickup'] = m
    return data
# map parcels to exisitng virtual nodes
