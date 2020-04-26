from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def fetch_stored_pred(pred_df, user_id):
    temp = pd.DataFrame()
    temp = pred_df[pred_df[0] == user_id]

    all_prod = temp.iloc[0,1]

    return all_prod

def Products_prediction(Cluster, user_id, Test_Vector, Col_List):

    cluster_num = Cluster[0]
    all_cust = Cluster[1]

    # read the predictions for this cluster
    pred_csv_path = '/Users/kratikakothari/Desktop/SE/Project/User_Interface/SE_Project/app/Trained_Models/Autoencoder_Data/' + str(cluster_num) + "_preds.csv"
    pred_df = pd.read_csv(pred_csv_path, header=None)

    temp = []
    if user_id in all_cust:
        # existing user, fetch the prediction
        temp = fetch_stored_pred(pred_df, user_id)
    else:
        # load User_Product_Matrix corresponding to cluster
        FilePath = '/Users/kratikakothari/Desktop/SE/Project/User_Interface/SE_Project/app/Trained_Models/Clustering_Data/' + str(cluster_num) + 'UP_Mat.csv'
        User_Product_Matrix = pd.read_csv(FilePath, sep=',')

        # Determine User with highest cosine similarity wrt this user
        max_sim = -1
        for i in range(len(all_cust)):

            sim = cosine_similarity([Test_Vector[Col_List]],[User_Product_Matrix.iloc[i][Col_List]])[0][0]
            if sim>max_sim:
                max_sim = sim
                similar_user = int(User_Product_Matrix.iloc[i]['CustomerID'])

        temp = fetch_stored_pred(pred_df, similar_user)

    temp = temp.replace("[", "")
    temp = temp.replace("]", "")
    temp = temp.split()

    results = list(map(int, temp))
    print ("Recommended product ids for user_" + str(user_id) + ": ")
    # print (similar_user,':   ', results)

    return results
