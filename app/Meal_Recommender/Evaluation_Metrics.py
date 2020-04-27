
from Predict_Autoencoder import*
from Predict_Persona import*
import pickle
import requests 
import numpy as np
import pandas as pd
import os
from sklearn.metrics.pairwise import cosine_similarity

def Prediction():

    Clusters = pickle.load(open(Folder_Path + "Clusters.pkl","rb"))

    All_Similar_Products = []
    for i in range(len(UserID_List)):
        User_ID = UserID_List[i]
        Test_Row = Test_Matrix.iloc[i]
        Cluster_Label = Predict_Cluster(pd.DataFrame([Test_Row]), Model_Predict)
        Cluster = (Cluster_Label[0], Clusters[Cluster_Label[0]])
        Similar_Products = Products_prediction(Cluster, User_ID, Test_Row, Col_List, Absolute_Trained_Model_Path)

        All_Similar_Products.append(Similar_Products)

    return All_Similar_Products

def AvgSimilarity(Matrix):

    Similarity_Matrix = cosine_similarity(X=Matrix)

    total_sim = 0
    total_pairs = 0
    for row in range(len(Similarity_Matrix)):
        for col in range(len(Similarity_Matrix[0])):
            total_sim += Similarity_Matrix[row][col]
            total_pairs += 1

    Avg_Similarity = total_sim / total_pairs

    return Avg_Similarity

# We cannot apply coverage on recipe recommendation output as we have used
# purchase history of ingredients for recommendation but are using recommending 
# recipes for predictions.

def Coverage():

    np.array(All_Similar_Products)

    Product_Prediction_count = len(np.unique(All_Similar_Products, return_counts=False))

    coverage = (Product_Prediction_count / Total_No_Products) *100
    return coverage

# Dissimilarity (1- cosine similarity) between recipes recommended to users in the test data
def Personalization():
    
    All_Recommendations_Matrix = np.zeros((0, Total_No_Recipes))

    for i in range(len(UserID_List)):

        User_ID = UserID_List[i]
        Cart_Product_Ids = []
        Cart_Product_vector = Test_Data[Test_Data[UserID_Col]==User_ID].loc[i][Col_List]

        for j in range(len(Cart_Product_vector)):
            if int(Cart_Product_vector[j]) == 1:
                Cart_Product_Ids.append(j+1)

        Predicted_Products = All_Similar_Products[i]
        Recommendations = GetRecipeRecommendations(Cart_Product_Ids,Predicted_Products)

        temp = np.zeros((1,Total_No_Recipes))
        for recipe_no in Recommendations:
            temp[0][recipe_no] = 1

        All_Recommendations_Matrix = np.append(All_Recommendations_Matrix,temp,axis=0)

    Avg_Similarity = AvgSimilarity(All_Recommendations_Matrix)

    Dissimilarity = 1 - Avg_Similarity

    return Dissimilarity

def Intra_List_Similarity():
    # read recipe and cuisine data

    with open( Absolute_Trained_Model_Path + "Culinary_DB_Data/culinaryDB_new_cuisines.pkl", 'rb') as file:
        Cuisine_Data = pickle.load(file)

    Cuisines = {}
    i = 0
    for val in Cuisine_Data.values():
        if val not in Cuisines:
            Cuisines[val] = i
            i += 1

    Total_No_Cuisines = len(Cuisines)

    User_Cuisine_Matrix = np.zeros((0, Total_No_Cuisines))

    for i in range(len(UserID_List)):

        User_ID = UserID_List[i]
        Cart_Product_Ids = []
        Cart_Product_vector = Test_Data[Test_Data[UserID_Col]==User_ID].loc[i][Col_List]
        
        for j in range(len(Cart_Product_vector)):
            if int(Cart_Product_vector[j]) == 1:
                Cart_Product_Ids.append(j+1)

        Predicted_Products = All_Similar_Products[i]
        Recommendations = GetRecipeRecommendations(Cart_Product_Ids,Predicted_Products)

        temp = np.zeros((1,Total_No_Cuisines))
        for recipe_no in Recommendations:
            Cuisine_Name = Cuisine_Data[recipe_no]
            Cuisine_No = Cuisines[Cuisine_Name]
            temp[0][Cuisine_No] = 1
         
        User_Cuisine_Matrix = np.append(User_Cuisine_Matrix,temp,axis=0)

    IntraListSimilarity = AvgSimilarity(User_Cuisine_Matrix)

    return IntraListSimilarity


if __name__ == '__main__':

    Absolute_Trained_Model_Path = "/home/niharika/Sem 4/SE/Project/SE_Project-User_Interface/app/Trained_Models/"
    
    Data_Folder_Path = Absolute_Trained_Model_Path + "/Matrix_Data/"
    Folder_Path = Absolute_Trained_Model_Path + "/Clustering_Data/"
    Matrix_FilePath = Data_Folder_Path + "User_Product_Matrix_Test.csv"
    UserID_Col = "CustomerID"
    Col_List=[str(i) for i in range(1,621)]
    
    Test_Data = pd.read_csv(Matrix_FilePath, sep=',')
    UserID_List = list(Test_Data[UserID_Col])
    Test_Matrix = Test_Data[Col_List]


    All_Similar_Products = []
    if os.path.exists("./All_Similar_Products.pkl"):
        with open("./All_Similar_Products.pkl", 'rb') as file:
            All_Similar_Products = pickle.load(file)
    else :
        Model_Predict = None
        with open(Folder_Path + "Clustering_Model.pkl", 'rb') as file:
            Model_Predict = pickle.load(file)
    
        All_Similar_Products = Prediction()

        with open("./All_Similar_Products.pkl", 'wb') as file:
            pickle.dump(All_Similar_Products, file)
    
    Total_No_Products = 620 
    Total_No_Recipes = 45749

    coverage = Coverage()
    print ('Coverage: ', coverage )

    personalization = Personalization()
    print ('Personalization: ', personalization )

    IntraListSimilarity = Intra_List_Similarity()
    print ('Intra List Similarity: ', IntraListSimilarity )
