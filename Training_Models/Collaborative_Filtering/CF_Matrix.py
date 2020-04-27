from Data_Operations import*
import numpy as np
import pandas as pd

class CF_Matrix:

    def __init__(self):

        self.Rows = 0
        self.Cols = 0
        self.Matrix = None

    ## Get quantity of product Prod_id purchased by user Cust_id
    def Get_Quantity(self, Data, UserID_Col, ProductID_Col, Cust_id, Prod_id, Quantity_Col):

        Cust_Id_Filter = Data.loc[Data[UserID_Col]==Cust_id]
        Prod_Id_Filter = Cust_Id_Filter.loc[Cust_Id_Filter[ProductID_Col]==Prod_id]
        Prod_Quantity = np.sum(Prod_Id_Filter[Quantity_Col])
        return Prod_Quantity

    ## Binary_Flag = 1 : Cell contains 1 if product is purchased by user
    ## Binary_Flag = 0 : Cell contains quantity of products is purchased by user
    def Build_User_Product_Matrix(self, Data, UserID_Col, ProductID_Col, Quantity_Col, Binary_Flag):

        Customer_Ids = Data[UserID_Col].unique()
        Product_Ids = Data[ProductID_Col].unique()

        self.Matrix = np.zeros((self.Rows, self.Cols))

        for i in range(len(Customer_Ids)):
            Cust_Id = Customer_Ids[i]
            for Prod_Id in Product_Ids:

                Prod_Quantity = self.Get_Quantity(Data, UserID_Col, ProductID_Col, Cust_Id, Prod_Id, Quantity_Col)

                if Prod_Quantity > 0:
                    if Binary_Flag:
                        self.Matrix[i][Prod_Id] = 1
                    else:
                        self.Matrix[i][Prod_Id] = Prod_Quantity

def Create_Purchase_Matrix():

    Sales_data = Load_Data(Sales_filepath, Sales_Col_list, seperator=",")
    Products_data = Load_Data(Products_filepath, Products_Col_list, seperator=",")
    User_data = Load_Data(Users_filepath, Users_Col_list, seperator=";")

    ## Analysis of No. of purchase orders per customer.
    ## Instead of whole data, using only N users' data with maximum purchase orders
    Num_Orders_List, Cust_Id_List = VisualizeSalesPerCustomer(Sales_data, UserID_Col)

    ## Pre-Processing: Combine all data files in one consistent, sort and drop rows with missing value
    Combined_Data = Combine_Data(Sales_data, User_data, Products_data, Cust_Id_List, UserID_Col, ProductID_Col)
    Processed_Data = Data_Processing(Combined_Data)

    ## Create User_Product Matrix for CF
    User_Product_Mat = CF_Matrix()
    User_Product_Mat.Rows = len(Cust_Id_List)
    User_Product_Mat.Cols = Products_data.shape[0]
    User_Product_Mat.Build_User_Product_Matrix(Processed_Data, UserID_Col, ProductID_Col, Quantity_Col, Binary_Flag=1)

    return User_Product_Mat.Matrix, Cust_Id_List, list(Products_data[ProductID_Col])

## Create User_PersonalInformation Matrix based on information filled by users
def Create_User_Matrix():
    return

def Store_Matrix(Data_Matrix, UserID_List, DataFrame_Header, FilePath):

    Matrix_DataFrame = []
    for i in range(len(UserID_List)):
        DF_Row = [UserID_List[i]]
        DF_Row.extend(list(User_Product_Matrix[i]))
        Matrix_DataFrame.append(DF_Row)

    User_Product_Dataframe = pd.DataFrame(Matrix_DataFrame, columns=DataFrame_Header)
    User_Product_Dataframe.to_csv(FilePath)


Data_Folder_Path = "/Users/pranjali/Downloads/SE_Project/Data/SalesDB/"

Sales_filepath = Data_Folder_Path + "new_Reduced_sales.csv"
Sales_Col_list = ["SalesID", "CustomerID", "ProductID", "Quantity", "SalesDate"]

Products_filepath = Data_Folder_Path + "new_products.csv"
Products_Col_list = ["ProductID", "ProductName", "CategoryID", "IsAllergic"]

Users_filepath = Data_Folder_Path + "customers.csv"
Users_Col_list = ["CustomerID", "FirstName", "LastName", "CityID"]

UserID_Col = "CustomerID"
ProductID_Col = "ProductID"
Quantity_Col = "Quantity"

User_Product_Matrix, UserID_List, ProductID_List = Create_Purchase_Matrix()

Attribute_List = [UserID_Col]
for i in ProductID_List:
    Attribute_List.append(i)

Store_Matrix(User_Product_Matrix, UserID_List, Attribute_List, "./Matrix_Data/User_Product_Matrix.csv")
# Store_Matrix(User_Product_Matrix[:1600], UserID_List[:1600], Attribute_List, "./Matrix_Data/User_Product_Matrix_Train.csv")
# Store_Matrix(User_Product_Matrix[1600:], UserID_List[1600:], Attribute_List, "./Matrix_Data/User_Product_Matrix_Test.csv")
