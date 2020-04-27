from Data_Operations import*
import numpy as np
import pandas as pd
import pickle

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering
from sklearn.cluster import AgglomerativeClustering
from sklearn.svm import LinearSVC
from sklearn import metrics

## Dimension Reduction using PCA
def PCA_Transform(Matrix, No_Dimensions):

    pca = PCA(n_components=No_Dimensions)
    Reduced_Matrix = pca.fit_transform(Matrix)
    Reduced_Matrix = pd.DataFrame(Reduced_Matrix)

    return pca, Reduced_Matrix


## Clustering Algorithms

## 1. KMeans Clustering
def KMeans_Clustering(Matrix, No_Clusters):

    KMeans_Obj = KMeans(n_clusters=No_Clusters, init='k-means++').fit(Matrix)
    Model_Predict = KMeans_Obj
    Cluster_Labels = KMeans_Obj.labels_

    return Model_Predict, Cluster_Labels

## Using LineasSCV for prediction of labels for future data in case of transductive clustering algorithms
## reference: https://github.com/scikit-learn/scikit-learn/issues/901

## 2. Hierarchical Clustering
def Hierarchical_Clustering(Matrix, No_Clusters):
    Clustering_Obj = AgglomerativeClustering(n_clusters=No_Clusters, linkage="complete").fit(Matrix)
    Cluster_Labels= Clustering_Obj.labels_
    Model_Predict = LinearSVC().fit(Matrix, Cluster_Labels)

    return Model_Predict, Cluster_Labels

## 3. Spectral Clustering
def Spectral_Clustering(Matrix, No_Clusters):
    Clustering_Obj = SpectralClustering(n_clusters=No_Clusters, assign_labels="discretize", random_state=0).fit(Matrix)
    Cluster_Labels = Clustering_Obj.labels_
    Model_Predict = LinearSVC().fit(Matrix, Cluster_Labels)

    return Model_Predict, Cluster_Labels


## Clustering performance evaluation metrics
def Clustering_Evaluation(Matrix, Cluster_Labels, Dist_Metric='euclidean'):

    ## 1. The Silhouette Coefficient
    ## The score is bounded between -1 for incorrect clustering and +1 for highly dense clustering.
    ## Scores around zero indicate overlapping clusters.

    Silhouette_Score = metrics.silhouette_score(Matrix, Cluster_Labels, metric=Dist_Metric)

    ## 2. The Calinski-Harabasz index (Variance Ratio Criteria)
    ## The index is the ratio of the sum of between-clusters dispersion and of inter-cluster dispersion for all clusters.
    ## The score is higher when clusters are dense and well separated.

#     CH_Index = metrics.calinski_harabasz_score(Matrix, Cluster_Labels)
    CH_Index = 0

    ## 3. The Davies-Bouldin index
    ## This index signifies the average ‘similarity’ between clusters, where the similarity is a measure
    ## that compares the distance between clusters with the size of the clusters themselves.
    ## Zero is the lowest possible score. Values closer to zero indicate a better partition.

    DB_Index = metrics.davies_bouldin_score(Matrix, Cluster_Labels)

    return Silhouette_Score, CH_Index, DB_Index



def Perform_Clustering(Matrix, Clustering_Algo, No_Clusters):

    if Clustering_Algo=='KMeans':
        Model_Predict, Labels = KMeans_Clustering(Matrix, No_Clusters)
        Evaluation_Metrics = Clustering_Evaluation(Matrix, Labels, 'euclidean')

    elif Clustering_Algo=='Hierarchical':
        Model_Predict, Labels = Hierarchical_Clustering(Matrix, No_Clusters)
        Evaluation_Metrics = Clustering_Evaluation(Matrix, Labels)

    elif Clustering_Algo=='Spectral':
        Model_Predict, Labels = Spectral_Clustering(Matrix, No_Clusters)
        Evaluation_Metrics = Clustering_Evaluation(Matrix, Labels)

    else:
        print("Invalid algotirthm: ", Clustering_Algo)

    return (Model_Predict, Labels, Evaluation_Metrics)



def Clustering_Comparison(Matrix, Clustering_AlgoList=[], No_Clusters_List=[], PCA_List=[]):

    Clustering_Results = []

    for dimension in PCA_List:
        if int(dimension) != 0:
            pca_dimension = dimension
            pca_obj, Reduced_Matrix = PCA_Transform(Matrix, pca_dimension)
        else:
            pca_obj = None
            pca_dimension = Matrix.shape[1]
            Reduced_Matrix = Matrix

        for algo in Clustering_AlgoList:
            for No_Clusters in No_Clusters_List:

                Model_Predict, Labels, Evaluation_Metrics = Perform_Clustering(Reduced_Matrix, algo, No_Clusters)

                print("---------------------------------------------------------------------------")
                print("Performace for algo: " + str(algo) + ", No. of clusters: "+ str(No_Clusters) + ", PCA with dimensions: " + str(pca_dimension))
                print("Silhouette Coefficient:  ", Evaluation_Metrics[0])
#                 print("Calinski-Harabasz Index: ", Evaluation_Metrics[1])
                print("Davies-Bouldin Index:    ", Evaluation_Metrics[2])

                Model_Details = (algo, No_Clusters, pca_dimension, pca_obj)
                Clustering_Results.append((Model_Details, Evaluation_Metrics))

#     Sorted_Result = sorted(Clustering_Results, key=lambda x: (-x[1][0], -x[1][1], x[1][2]))
    Filtered_Results = [result for result in Clustering_Results if result[1][0]>0]
    if len(Filtered_Results)>0:
        Sorted_Result = sorted(Filtered_Results, key=lambda x: (x[1][2], -x[1][0]))
    else:
        Sorted_Result = sorted(Clustering_Results, key=lambda x: (x[1][2], -x[1][0]))
    Best_Result = Sorted_Result[0]

    Best_Result_Eval = Best_Result[1]
    print("=========================== BEST RESULT ============================")
    print("Silhouette Coefficient:  ", Best_Result_Eval[0])
    print("Calinski-Harabasz Index: ", Best_Result_Eval[1])
    print("Davies-Bouldin Index:    ", Best_Result_Eval[2])

    Best_Model_Params = Best_Result[0]
    print("============================ BEST MODEL =============================")
    print("Algorithm:           ", Best_Model_Params[0])
    print("No. of clusters:     ", Best_Model_Params[1])
    print("Dimension Reduction: ", Best_Model_Params[2])

    return Best_Model_Params

## Store Clustering Algorithm Output
def Store_Clusters(Matrix, UserID_Col, Model_Predict, PCA_fitted_obj, UserID_List, Labels, Output_Folder_Path):

    ## Store Model Params which will be used in prediction of labels for future data.
    ## Load this model and call predict() function on 'Model_Predict' for inference.
    Saved_Model = {'Model' : Model_Predict, 'PCA_Obj' : PCA_fitted_obj}
    with open(Output_Folder_Path + "Clustering_Model.pkl", 'wb') as output_file:
        pickle.dump(Saved_Model, output_file)
    print("Storing trained clustering model...")

    ## Store UserIDs divided into clusters which will be used to train autoencoders in next phase.
    Clusters = {}
    for i in range(len(Labels)):

        label = Labels[i]
        UserID = UserID_List[i]

        if label not in Clusters.keys():
            Clusters[label] = [UserID]
        else:
            Clusters[label].append(UserID)

    with open(Output_Folder_Path + "Clusters.pkl", 'wb') as output_file:
        pickle.dump(Clusters, output_file)
    print("Storing clustered UserIDs...")

    for cluster in Clusters.keys():
        User_List = Clusters[cluster]
        Cluster_matrix = Matrix[Matrix[UserID_Col].isin(User_List)]
        Cluster_matrix.to_csv(Output_Folder_Path + str(cluster) + 'UP_Mat.csv')
        print("Storing matrix for cluster " + str(cluster))
