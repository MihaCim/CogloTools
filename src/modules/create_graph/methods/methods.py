import csv
from sklearn.cluster import KMeans
import pandas as pd
from ..config.config_parser import ConfigParser
import copy
import matplotlib.pyplot as plt

config_parser = ConfigParser()
url = "https://graphhopper.com/api/1/vrp?key=e8a55308-9419-4814-81f1-6250efe25b5c"


def proccess_elta_event(proc_event, data):
    if proc_event == None:
        return elta_clustering(data)
    elif proc_event == 'pickupRequest':
        return elta_map_parcels(data)

def elta_clustering(orig_data):
    data = copy.deepcopy(orig_data)
    l = []
    for i, el in enumerate(data['CLOS']):
        l.append([i, el['UUID'], 'clos', el['currentLocation'][0], el['currentLocation'][1]])
    for i, el in enumerate(data['orders']):
        l.append([i, el['UUIDParcel'], "destination"] + el['destination'])
        l.append([i, el['UUIDParcel'], "pickup"] + el['pickup'])
    df = pd.DataFrame(l)
    # run clustering
    kmeans = KMeans(n_clusters=5)
    kmeans.fit(df[[3, 4]])  # Compute k-means clustering.
    centers = kmeans.cluster_centers_
    df["labels"] = labels = kmeans.labels_
    for index, row in df.iterrows():
        if row[2] == 'clos':
            data['CLOS'][row[0]]['currentLocation'] = str(row['labels'])
        else:
            data['orders'][row[0]][row[2] + '_location'] = data['orders'][row[0]][row[2]]
            data['orders'][row[0]][row[2]] = str(row['labels'])
    ## print clusters
    # df.plot.scatter(x=3, y=4, c=labels, s=10, cmap='viridis')
    # plt.scatter(centers[:, 0], centers[:, 1], c='black', s=80, alpha=0.5)
    # plt.show()

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
    cur_min = sys.maxsize
    label = -1
    for post in posts:
        lat = float(lat_cord) - float(post[1][0])
        lon = float(lon_cord) - float(post[1][1])
        distance = (lat * lat) + (lon * lon)
        if distance < cur_min:
            cur_min = distance
            label = post[0]
    if label == -1:
        raise Exception( "Error in mapping parcels to nodes")

    return label


def elta_map_parcels(orig_data):
    data = copy.deepcopy(orig_data)
    for clo in data['CLOS']:
        mapped_location = find_min(clo['currentLocation'][0], clo['currentLocation'][1])
        clo['currentLocation'] = mapped_location
        clo['currentLocationL'] = clo['currentLocation']
        for parcel in clo['parcels']:
            mapped_location = find_min(parcel['destination'][0], parcel['destination'][1])
            parcel['destination_location'] = parcel['destination']
            parcel['destination'] = mapped_location
            print(mapped_location)

    for clo in data['orders']:
        mapped_location = find_min(clo['destination'][0], clo['destination'][1])
        clo['destination_location'] = clo['destination']
        clo['destination'] = mapped_location

        mapped_location = find_min(clo['pickup'][0], clo['pickup'][1])
        clo['pickup_location'] = clo['pickup']
        clo['pickup'] = mapped_location
    return data

# map parcels to exisitng virtual nodes
