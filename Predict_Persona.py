import pandas as pd
import pickle

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering
from sklearn.cluster import AgglomerativeClustering
from sklearn.svm import LinearSVC

def Assign_Persona(Test_Matrix, Saved_Model):

    Pca_Dimensions = Saved_Model['Dimensions']
    Model_Predict = Saved_Model['Model']

    if Pca_Dimensions != Test_Matrix.shape[1]:
        pca = PCA(n_components=Pca_Dimensions)
        Reduced_Matrix = pca.fit_transform(Test_Matrix)
        Reduced_Matrix = pd.DataFrame(Reduced_Matrix)
    else:
        Reduced_Matrix = Test_Matrix

    Predictions = Model_Predict.predict(Reduced_Matrix)

    return Predictions

def main():

    Matrix_FilePath = "./User_Product_Matrix_Test.csv"
    Col_List=[str(i) for i in range(1,453)]

    Test_Data = pd.read_csv(Matrix_FilePath, sep=',')
    Test_Matrix = Test_Data[Col_List]

    Model_Predict = None
    with open("./Saved_Model.pkl", 'rb') as file:
        Saved_Model = pickle.load(file)

    Predictions = Assign_Persona(Test_Matrix, Saved_Model)
    print(Predictions)

if __name__ == "__main__":
    main()
