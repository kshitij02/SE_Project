from Predict_Autoencoder import*
from Predict_Persona import*

def Prediction():

    Clusters = pickle.load(open(Folder_Path + "Clusters.pkl","rb"))

    Ingredient_Predictions = []
    for i in range(len(UserID_List)):
        User_ID = UserID_List[i]
        Test_Row = Test_Data.iloc[i]
        # Test_Row = Test_Matrix.iloc[i]
        Cluster_Label = Predict_Cluster(pd.DataFrame([Test_Row[Col_List]]), Model_Predict)
        # Cluster_Label = Predict_Cluster(pd.DataFrame([Test_Row]), Model_Predict)
        Cluster = (Cluster_Label[0], Clusters[Cluster_Label[0]])
        Ingredient_Prediction = Products_prediction(Cluster, User_ID, Test_Row, Col_List)

        Ingredient_Predictions.append(Ingredient_Prediction)

    return Ingredient_Predictions

if __name__ == '__main__':

    Data_Folder_Path = "./Matrix_Data/"
    Folder_Path = "./Clustering_Data/"
    Matrix_FilePath = Data_Folder_Path + "User_Product_Matrix_Test.csv"
    UserID_Col = "CustomerID"
    Col_List=[str(i) for i in range(1,621)]
    
    Test_Data = pd.read_csv(Matrix_FilePath, sep=',')
    UserID_List = list(Test_Data[UserID_Col])
    Test_Matrix = Test_Data[Col_List]

    Model_Predict = None
    with open(Folder_Path + "Clustering_Model.pkl", 'rb') as file:
        Model_Predict = pickle.load(file)


    Ingredient_Predictions = Prediction()
    print("Ingredient_Predictions: ", Ingredient_Predictions)
    
    with open("./Ingredient_Predictions.pkl", 'wb') as file:
        pickle.dump(Ingredient_Predictions, file)
    