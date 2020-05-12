import json
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd


def elta_clustering(data):
    print(data)
    l = []
    for el in data['orders']:
        l.append([el['UUIDParcel'], "destination"] + el['destination'])
        l.append([el['UUIDParcel'], "pickup"] + el['pickup'])
    df = pd.DataFrame(l)
    # run clustering
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(df[[2, 3]])  # Compute k-means clustering.
    centers = kmeans.cluster_centers_
    df["labels"] = labels = kmeans.labels_
    for index, row in df.iterrows():
        print(index)
        print(row)
        data['orders'][index // 2][row[1]] = row['labels']
    print(df)

    clos = {"useCase": "ELTA"}
    clos_list = []
    i = 0
    for row in centers:
        clos_list.append({
            "uuid": i,
            "lat": row[0],
            "lon": row[1]
        })
        i = i + 1
    clos["CLOS"] = clos_list

    return data, clos


def elta_map_parcels(data):
    print(data)
# map parcels to exisitng virtual nodes
