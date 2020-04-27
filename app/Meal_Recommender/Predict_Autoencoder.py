import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def Fetch_stored_pred(pred_df, USERID):
    temp = pd.DataFrame()
    temp = pred_df[pred_df[0] == USERID]

    all_prod = temp.iloc[0,1]

    return all_prod

def Products_prediction(Cluster, UserID, Test_Vector, Col_List, ModelPath):

    Cluster_Num = Cluster[0]
    UserID_List = Cluster[1]

    # read the predictions for this cluster

    Pred_csv_path = ModelPath + "Autoencoder_Data/" + str(Cluster_Num) + "_preds.csv"
    Pred_df = pd.read_csv(Pred_csv_path, header=None)

    temp = []
    if UserID in UserID_List:
        # existing user, fetch the prediction
        temp = Fetch_stored_pred(Pred_df, UserID)
    else:
        # load User_Product_Matrix corresponding to cluster

        FilePath = ModelPath + "Clustering_Data/" + str(Cluster_Num) + 'UP_Mat.csv'
        User_Product_Matrix = pd.read_csv(FilePath, sep=',')

        # Determine User with highest cosine similarity wrt this user
        # max_sim = -1
        # for i in range(len(all_cust)):
        #
        #     sim = cosine_similarity([Test_Vector[Col_List]],[User_Product_Matrix.iloc[i][Col_List]])[0][0]
        #     if sim>max_sim:
        #         max_sim = sim
        #         similar_user = int(User_Product_Matrix.iloc[i]['CustomerID'])

        Data_Matrix = User_Product_Matrix.iloc[:][Col_List].transpose()
        Test_Vector = np.array(Test_Vector[Col_List])

        Similarity = Test_Vector.dot(Data_Matrix)

        Max_Similarity_index = np.where(Similarity == np.amax(Similarity))[0][0]

        Similar_user = UserID_List[Max_Similarity_index]

        temp = Fetch_stored_pred(Pred_df, Similar_user)

    temp = temp.replace("[", "")
    temp = temp.replace("]", "")
    temp = temp.split()

    results = list(map(int, temp))
    print ("Recommended product ids for user_" + str(UserID) + ": ")
    # print (similar_user,':   ', results)

    return results
