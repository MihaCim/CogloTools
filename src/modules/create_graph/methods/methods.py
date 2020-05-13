import json
import numpy as np
import csv
from sklearn.cluster import KMeans
import pandas as pdgit
from ..config.config_parser import ConfigParser

config_parser = ConfigParser()


def elta_clustering(data):
    print(data)
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
        print(index)
        print(row)
        data['orders'][index // 2][row[1] + '_location'] = data['orders'][index // 2][row[1]]
        data['orders'][index // 2][row[1]] = str(row['labels'])
    print(df)

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

    cur_max = 0
    label = -1
    for post in posts:
        lat = float(lat_cord) - float(post[1][0])
        lon = float(lon_cord) - float(post[1][1])
        m = lat * lat + lon * lon
        if m > cur_max:
            cur_max = m
            label = post[0]
    return label


def elta_calculating_closest(data):
    for clo in data['CLOS']:
        m = find_min(clo['currentLocation'][0], clo['currentLocation'][1])
        clo['currentLocation'] = m
        clo['currentLocationL'] = clo['currentLocation']
        for parcel in clo['parcels']:
            m = find_min(parcel['destination'][0], parcel['destination'][1])
            parcel['destination_location'] = parcel['destination']
            parcel['destination'] = m
            print(m)

def elta_map_parcels(data):
    print(data)
# map parcels to exisitng virtual nodes
