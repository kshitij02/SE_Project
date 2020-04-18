from Clustering_Algorithms import*

Matrix_FilePath = "./User_Product_Matrix.csv"
Col_List=[str(i) for i in range(1,453)]
Matrix_Data = pd.read_csv(Matrix_FilePath, sep=',')
Matrix = Matrix_Data[Col_List]

Clustering_AlgoList = ['KMeans', 'Hierarchical', 'Spectral']
No_Clusters_List = [2, 3, 4, 5, 6, 7]
PCA_List = [0, 100, 200]


Best_Model = Clustering_Comparison(Matrix, Clustering_AlgoList, No_Clusters_List, PCA_List)

if Best_Model[2] != Matrix.shape[1]:
    Reduced_Matrix = PCA_Transform(Matrix, Best_Model[2])
else:
    Reduced_Matrix = Matrix

Labels, Evaluation_Metrics = Perform_Clustering(Reduced_Matrix, Best_Model[0], Best_Model[1])

UserIDList = list(Matrix_Data['CustomerID'])
Store_Clusters(UserIDList, Labels, "./")
