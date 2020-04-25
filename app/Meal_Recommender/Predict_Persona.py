import pandas as pd
import pickle

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering
from sklearn.cluster import AgglomerativeClustering
from sklearn.svm import LinearSVC

def Predict_Cluster(Test_Matrix, Saved_Model):

    Pca_Obj = Saved_Model['PCA_Obj']
    Model_Predict = Saved_Model['Model']

    if Pca_Obj:
        Reduced_Matrix = Pca_Obj.transform(Test_Matrix)
        Reduced_Matrix = pd.DataFrame(Reduced_Matrix)
    else:
        Reduced_Matrix = Test_Matrix

    Cluster_Labels = Model_Predict.predict(Reduced_Matrix)

    return Cluster_Labels
