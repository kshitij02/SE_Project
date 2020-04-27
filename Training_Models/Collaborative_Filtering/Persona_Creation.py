from Clustering_Algorithms import*

def Create_Persona():
    Folder_Path = "./Matrix_Data/"
    Matrix_FilePath = Folder_Path + "User_Product_Matrix.csv"
    # Matrix_FilePath = Folder_Path + "User_Product_Matrix_Train.csv"
    UserID_Col = "CustomerID"
    Col_List=[str(i) for i in range(1,621)]
    Matrix_Data = pd.read_csv(Matrix_FilePath, sep=',')
    Matrix = Matrix_Data[Col_List]

    # Clustering_AlgoList = ['KMeans', 'Hierarchical', 'Spectral']
    # No_Clusters_List = [2, 3, 4, 5, 6, 7]
    # PCA_List = [0, 100, 200]

    Clustering_AlgoList = ['KMeans' ,'Hierarchical']
    No_Clusters_List = [6, 7, 8, 9, 10]
    PCA_List = [0, 100, 200, 300]

    Best_Model = Clustering_Comparison(Matrix, Clustering_AlgoList, No_Clusters_List, PCA_List)

    if Best_Model[2] != Matrix.shape[1]:
        PCA_fitted_obj, Reduced_Matrix = PCA_Transform(Matrix, Best_Model[2])
    else:
        PCA_fitted_obj = None
        Reduced_Matrix = Matrix

    Model_Predict, Labels, Evaluation_Metrics = Perform_Clustering(Reduced_Matrix, Best_Model[0], Best_Model[1])

    UserIDList = list(Matrix_Data['CustomerID'])
    Store_Clusters(Matrix_Data, UserID_Col, Model_Predict, Best_Model[3], UserIDList, Labels, "./Clustering_Data/")

if __name__ == "__main__":
    Create_Persona()
