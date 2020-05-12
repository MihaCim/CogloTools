import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import seaborn as sns; sns.set()
import csv



class methods:

    @staticmethod
    def elta_clustering(data):
        #prepare df
        dataDir = ("./")
        df = pd.read_csv(dataDir + r"ELTA_All11.csv")
        X = df.loc[:, ['UID', 'Geocode X', 'Geocode Y']]

        #run clustering
        kmeans = KMeans(n_clusters=3, init='k-means++')
        kmeans.fit(X[X.columns[1:3]])  # Compute k-means clustering.
        X['cluster_label'] = kmeans.fit_predict(X[X.columns[1:3]])
        df["labels"] = labels = kmeans.labels_
        virtual_nodes = kmeans.cluster_centers_

        #print the clusters
        #X.plot.scatter(x='Geocode X', y='Geocode Y', c=labels, s=10, cmap='viridis')
        #plt.scatter(centers[:, 0], centers[:, 1], c='black', s=50, alpha=0.5)
        response = df.to_json()
        json.dump(my_details, response)

        return(response)

    @staticmethod
    def elta_map_parcels(data):
        #map parcels to exisitng virtual nodes




