from sklearn.cluster import MiniBatchKMeans
import csv


def MiniKMeansClustering(matrix, n_clusters):
    mbkmeans = MiniKMeansClustering(n_clusters=n, 
    max_iter=10000, 
    batch_size=1000, 
    init_size=1000).fit(matrix)

    labels = mbkmeans.labels_

    return labels

def load_GD_data
    with open('GD_data.csv', newline='') as csvfile:
        read = csv.DictReader(csvfile)


