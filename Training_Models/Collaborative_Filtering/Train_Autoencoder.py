import csv
import os
import math
import pickle
import random
import numpy as np
import pandas as pd
import pprint as pp
import tensorflow as tf
from Data_Operations import*


class Autoencoder(object):

    def __init__(self,User_Product_Matrix):

        num_input = User_Product_Matrix.shape[1]  ## No. of products
        num_hidden_1 = 10
        num_hidden_2 = 5

        self.X = tf.placeholder(tf.float64, [None, num_input])

        self.weights = {
            'encoder_h1': tf.Variable(tf.random_normal([num_input, num_hidden_1], dtype=tf.float64)),
            'encoder_h2': tf.Variable(tf.random_normal([num_hidden_1, num_hidden_2], dtype=tf.float64)),
            'decoder_h1': tf.Variable(tf.random_normal([num_hidden_2, num_hidden_1], dtype=tf.float64)),
            'decoder_h2': tf.Variable(tf.random_normal([num_hidden_1, num_input], dtype=tf.float64)),
        }

        self.biases = {
            'encoder_b1': tf.Variable(tf.random_normal([num_hidden_1], dtype=tf.float64)),
            'encoder_b2': tf.Variable(tf.random_normal([num_hidden_2], dtype=tf.float64)),
            'decoder_b1': tf.Variable(tf.random_normal([num_hidden_1], dtype=tf.float64)),
            'decoder_b2': tf.Variable(tf.random_normal([num_input], dtype=tf.float64)),
        }


    def construct_model(self):

        # Encoder: 2 Hidden layers with sigmoid activations
        layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(self.X, self.weights['encoder_h1']), self.biases['encoder_b1']))
        layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, self.weights['encoder_h2']), self.biases['encoder_b2']))
        self.encoder_op = layer_2

        # Decoder: 2 Hidden layers with sigmoid activations
        layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(self.encoder_op, self.weights['decoder_h1']), self.biases['decoder_b1']))
        layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, self.weights['decoder_h2']), self.biases['decoder_b2']))
        self.decoder_op = layer_2


    # Define loss and optimizer, minimize the squared error
    def loss_optimize(self):

        y_true = self.X
        y_pred = self.decoder_op
        self.loss = tf.losses.mean_squared_error(y_true, y_pred)
        self.optimizer = tf.train.RMSPropOptimizer(0.03).minimize(self.loss)

        # Define evaluation metrics
        eval_x = tf.placeholder(tf.int32, )
        eval_y = tf.placeholder(tf.int32, )
        pre, pre_op = tf.metrics.precision(labels=eval_x, predictions=eval_y)


    ## Batch-wise training of all users of the cluster
    def run_session(self, User_Product_Matrix):

        predictions = pd.DataFrame()
        init = tf.global_variables_initializer()
        local_init = tf.local_variables_initializer()

        with tf.Session() as session:
            epochs = 100
            batch_size = 50

            session.run(init)
            session.run(local_init)

            num_batches = math.ceil(User_Product_Matrix.shape[0] / batch_size)
            BatchIndex = 0

            for i in range(epochs):
                avg_cost = 0

                for batchNum in range(num_batches) :
                    if(batchNum == num_batches-1):
                        batch = User_Product_Matrix.iloc[batchNum :, :]
                    else :
                        batch = User_Product_Matrix.iloc[batchNum : batchNum+batch_size, :]

                    _, l = session.run([self.optimizer, self.loss], feed_dict={self.X: batch})

                    avg_cost += l
                    batchNum += batch_size

                avg_cost /= num_batches

#                 print("Epoch: {} Loss: {}".format(i + 1, avg_cost))
#             print("Predictions...")

            preds = session.run(self.decoder_op, feed_dict={self.X: User_Product_Matrix})
            predictions = predictions.append(pd.DataFrame(preds))

        return predictions


    def GetNextPredProduct(self, N, Pred_Matrix, Customer_Ids):

        # returns top N most likely to buy products for each user
        # Data structure : Dict with userID key and list of N productIDs as value

        Pred_Products = {}

        No_Users = Pred_Matrix.shape[0]
        No_Products = Pred_Matrix.shape[1]

        for user in range(No_Users) :
            Pred_Row = np.array(Pred_Matrix.iloc[user, :])
            Sorted_Row = np.argsort(Pred_Row)[::-1][:N]
            Sorted_Row += 1

            userID = Customer_Ids[user]
            Pred_Products[userID] = Sorted_Row

        return Pred_Products


    def run_model(self, User_Product_Matrix, Cluster):

        Cluster_Num = Cluster[0]
        UserID_List = Cluster[1]

        print("Constructing model with 2 encoder layer and 2 decoder layers..")
        self.construct_model()

        print ('Building optimizer, defining losses..')
        self.loss_optimize()

        print ('Ready to run..')
        predictions = self.run_session(User_Product_Matrix)

        print ('Got the predictions!')
        Pred_Products = self.GetNextPredProduct(20, predictions, UserID_List)

        print ("Writing to file..")
        pp.pprint(Pred_Products)
        write_dict_to_csv(Pred_Products, "./Autoencoder_Data/" + str(Cluster_Num)+"_preds.csv")

        print ('Success!')


def write_dict_to_csv(dict, path):
    w = csv.writer(open(path, "w"))
    for key, val in dict.items():
        w.writerow([key, val])

def Train_all_Clusters(Clusters):

    for Cluster in Clusters.items():

        Cluster_Num = Cluster[0]
        UserID_List = Cluster[1]

        FilePath = Folder_Path + str(Cluster_Num) + 'UP_Mat.csv'

        if os.path.exists(FilePath):
            print ('Loading User_Product_Matrix..')
            User_Product_Matrix = pd.read_csv(FilePath, sep=',')
        else:

            print ('Building User_Product_Matrix from pre-stored User_Product_Matrix_Train..')
            User_Product_Matrix = pd.DataFrame(columns=Columns)

            for UserID in UserID_List:
                row = UPM_Train.loc[UPM_Train[UserID_Col] == UserID]
                temp = pd.DataFrame(row)
                User_Product_Matrix = User_Product_Matrix.append(temp, ignore_index=True)

            print ('Storing Matrix..')
            if not os.path.exists(Folder_Path):
                os.mkdir(Folder_Path)
            User_Product_Matrix.to_csv(FilePath)


        print ('Matrix shape: ', User_Product_Matrix.shape)

        print ('Initializing Autoencoder parameters: weights, biases, X..')
        autoencoder = Autoencoder(User_Product_Matrix)
        autoencoder.run_model(User_Product_Matrix, Cluster)

#         print ('Storing model..')
#         path = './Autoencoders'
#         store_model(autoencoder, path, Cluster_num)


if __name__ == '__main__':

    UserID_Col = "CustomerID"
    ProductID_Col = "ProductID"
    Quantity_Col = "Quantity"

    Folder_Path = "./Clustering_Data/"

    ## Load clusters of training data(Buyer_Persona_Clustering)
    Clusters = pickle.load(open(Folder_Path + "Clusters.pkl","rb"))

    UPM_Train_Path = "./Matrix_Data/User_Product_Matrix.csv"
    UPM_Train = pd.read_csv(UPM_Train_Path, sep=',')
    Columns = list(UPM_Train.columns)

    Train_all_Clusters(Clusters)
