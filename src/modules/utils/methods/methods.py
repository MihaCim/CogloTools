import json
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd


def elta_clustering(evt_type, data):
    if evt_type is None:
        #print("start data", data)
        l = []
        for element in data['orders']:
            l.append([element['UUIDParcel'], "destination"] + element['destination'])
            l.append([element['UUIDParcel'], "pickup"] + element['pickup'])
        df = pd.DataFrame(l)
        # run clustering
        kmeans = KMeans(n_clusters=5)
        kmeans.fit(df[[2, 3]])  # Compute k-means clustering.
        centers = kmeans.cluster_centers_
        df["labels"] = labels = kmeans.labels_
        for index, row in df.iterrows():
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
        #print("elta_data", data)
        return data, clos
    elif evt_type == "pickupRequest":
        #map parcel pickup and destination to existing clusters ids#
        return data
    else:
        return jsonify({"message": "Invalid event type in input message: {}".format(evt_type)})

def elta_map_parcels(data):
    print(data)
# map parcels to exisitng virtual nodes
