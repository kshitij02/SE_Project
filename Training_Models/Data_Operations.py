import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv

def Load_Data(Csv_Path, ColumnList, seperator=None):

    print("Loading data from ", Csv_Path)
    if seperator==None:
        Data = pd.read_csv(Csv_Path)[ColumnList]
    else:
        Data = pd.read_csv(Csv_Path, sep=seperator)[ColumnList]
    print ("number of rows, cols ", Data.shape)

    return Data

def VisualizeSalesPerCustomer(Sales_data, UserID_Col):

    Sales_Data_Idx = pd.Index(Sales_data[UserID_Col])

    Num_Orders_per_cust = Sales_Data_Idx.value_counts()
    Num_Orders_List = Num_Orders_per_cust.tolist()
    Cust_Id_List = Num_Orders_per_cust.index.values.tolist()

    return Num_Orders_List, Cust_Id_List

def Plot_Graph(x, y, xlabel='Customer ID', ylabel='No. of Orders', title='Customer Purchase Orders Analysis'):

    plt.figure(figsize=(10,8))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    index = np.arange(len(x))
    plt.bar(index,y)
    plt.show()

def Combine_Data(Sales_data, User_data, Products_data, Cust_Id_List, UserID_Col, ProductID_Col):

    Sales_data_filtered = Sales_data[Sales_data[UserID_Col].isin(Cust_Id_List)]
    User_Sales_Data = pd.merge(Sales_data_filtered, User_data, on=UserID_Col)
    User_Product_Sales_Data = pd.merge(User_Sales_Data, Products_data, on=ProductID_Col)

    return User_Product_Sales_Data

def Data_Processing(Data):

    SortedData = Data.sort_values(["CustomerID", "SalesDate", "SalesID", "ProductID"], ascending=[True, True, True, True])
    Final_Data = Data.dropna(subset=["CustomerID", "SalesID", "ProductID","SalesDate", "Quantity"])
    return Data
