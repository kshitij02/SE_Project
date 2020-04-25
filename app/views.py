# This is Main Controller of the webapp
from flask import Flask
from flask_nav.elements import Navbar, Subgroup, View, Link, Text, Separator
from flask import render_template
from flask import url_for, redirect, request, make_response,flash
import sqlalchemy
from app import app, db, nav

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from flask_login import current_user, login_user
from flask_wtf import FlaskForm
from flask_login import logout_user
from sqlalchemy import update
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import func
from sqlalchemy import desc
from sqlalchemy.orm import load_only
import json
import numpy as np
from app.models import User, Credentials, Product, Meal, MealDetails, Cart

from app.Meal_Recommender.Predict_Persona import*
from app.Meal_Recommender.Predict_Autoencoder import*

Absolute_Trained_Model_Path = "/Users/pranjali/Downloads/SE_Project_UI/app/Trained_Models/"

@app.route('/')
def firstpage():
    return render_template('FirstPage.html',title='First Page')


@app.route('/Registration')
def Registration():
    return render_template('Register.html',title='Registration Page')


@app.route('/FoodPreferenceForm')
def Food_Preference_Form():
    return render_template('Food_Preference.html',title='Food Choices Page')


@app.route('/Logging', methods = ['GET', 'POST'])
def Logging():
    return render_template('Login.html')


@app.route('/Food_Prefernce_Data', methods = ['GET', 'POST'])
def Food_Prefernce_Data():
    # Use post method as User Info should not be passed through URL.
    # 1. Get Food_Prefernce Form content by POST method.
    # 2. Add entry in User_Info table with user food_preference info and userid.
    # 3. Commit database changes.
    return render_template('Login.html')

@app.route('/Register', methods = ['GET', 'POST'])
def Register():
    # Use post method as User Info should not be passed through URL.
    # 1. Get Registration Form content by POST method.
    # 2. Encrypt Password and Add entry in Credentials table with EmailID and encrypted password.
    # 3. Add entry in User table with user registration info.
    # 4. Commit database changes.
    # 5. render FoodPreferenceForm page if successfully registered else display error message.

    if request.method == 'POST':
       if not request.form['name'] or not request.form['email'] or not request.form['password'] or not request.form['gender'] or not request.form['age']:
          flash('Please enter all the fields', 'error')
       else:
          password = request.form['password']
          # pw_hash = generate_password_hash(password)

          Num_Users = len(User.query.all())
          user1 = User(user_id = Num_Users+1 , name = request.form['name'], email_id = request.form['email'], gender = request.form['gender'], age = request.form['age'])
          # Credential1 = Credentials(user_id = Num_Users+1, email_id = request.form['email'], password = pw_hash)
          Credential1 = Credentials(user_id = Num_Users+1, email_id = request.form['email'], password = password)

          db.session.add(user1)
          db.session.add(Credential1)
          db.session.commit()

          flash('Record was successfully added')

    return render_template('Login.html')
    # return render_template('FoodPreferenceForm.html')


@app.route('/Login', methods = ['POST'])
def Login():
    # Use post method as User credentials should not be passed through URL.
    # 1. Get Form content (User credentials) by POST method.
    # 2. Authenticate user from database.
    # 3. Render HomePage if Authenticated
    # 4. Render Login Page again with error message

    form = FlaskForm()
    Authenticate = False

    if request.method == 'POST':
        emailid=request.form['email']
        password=request.form['password']

        print("Creds: ", emailid, password)

        users = User.query.filter(User.email_id==emailid).all()
        Creds = Credentials.query.filter(Credentials.email_id==emailid).all()

        # if user and Cred and check_password_hash(Cred.password, password):
        #     login_user(user)
        #     user.is_authenticated = True
        #     Authenticate = True
        #     flash('Successful login!')

        Check = False
        for user1 in Creds :
            if (user1.password == password):
                Check = True
                Auth_User = User.query.filter(User.user_id == user1.user_id).first()
                Cred = user1

        if Check and Cred and (Cred.password == password):
            login_user(Auth_User)
            Auth_User.is_authenticated = True
            print("Authenticated")
            Authenticate = True
            flash('Successful login!')

    if Authenticate == True :
        return redirect('/Home')
    else :
        return render_template('Login.html')


def GetAllProducts():
    # 1. Database query to fetch all products from Products table and return Subquery1_results
    Product_Tuples = Product.query.with_entities(Product.product_id, Product.name, Product.price).all()
    Product_List = []
    for i in range(1,len(Product_Tuples)):
        Product_List.append(list(Product_Tuples[i]))

    return Product_List

def GetPredictedProducts():
    # 1. Database query to fetch cart content fo current user
    Cart_Products = GetCurrentCart()
    All_Products = GetAllProducts()

    # 2. Create test vector for the user
    Col_List = [str(i) for i in range(1,621)]
    Test_Row = np.zeros(621)
    for product_id in Cart_Products:
        Test_Row[product_id] = 1
    Test_Row_DF = pd.DataFrame([Test_Row[1:]], columns=Col_List)

    # 3. Call Predict function of clustering model to assign cluster to the user
    Model_Predict = pickle.load(open(Absolute_Trained_Model_Path + "Clustering_Data/Clustering_Model.pkl","rb"))
    Clusters = pickle.load(open(Absolute_Trained_Model_Path + "Clustering_Data/Clusters.pkl","rb"))

    uid = current_user.get_id()
    User_Found = 0
    for cluster_id in Clusters.keys():
        if uid in Clusters[cluster_id]:
            Cluster_Label = [cluster_id]
            User_Found = 1

    if not User_Found:
        Cluster_Label = Predict_Cluster(Test_Row_DF, Model_Predict)

    # 4. Call corresponding AutoEncoder Model's predict function to get list of
    #    products user is most likely to but next
    Cluster = (Cluster_Label[0], Clusters[Cluster_Label[0]])

    Ingredient_Prediction = Products_prediction(Cluster, uid, Test_Row_DF.iloc[0], Col_List)

    # 5. Return lists
    Predicted_Products = []
    Cart_Product_obj = []
    for product_obj in All_Products:
        if product_obj[0] in Ingredient_Prediction:
            Predicted_Products.append(product_obj)
        if product_obj[0] in Cart_Products:
            Cart_Product_obj.append(product_obj)

    print("Cart Products: ", Cart_Product_obj)
    print("Predicted_Products: ", Predicted_Products)

    return Predicted_Products

def GetSimilarProducts():
    # 1. Database query to fetch cart content fo current user
    # 2. Database query to fetch user's personal info
    # 3. Call predict fuction of corresponding embedding model (Input: results from step 1)
    # 4. Filter results obtained in step 3 according to the info fetchd in step 2 (eg. Allergies)
    # 5. return final list
    return

def GetComplementaryProducts():
    # 1. Database query to fetch cart content fo current user
    # 2. Database query to fetch user's personal info
    # 3. Call predict fuction of corresponding embedding model (Input: results from step 1)
    # 4. Filter results obtained in step 3 according to the info fetchd in step 2 (eg. Allergies)
    # 5. return final list
    return

def GetRecipeRecommendations():
    # 1. Database query to fetch cart content fo current user
    # 2. Call GetPredictedProducts() to get predicted products
    # 3. Database query to fetch user's personal info
    # 4. Call predict fuction of corresponding embedding model (Input: results from step 1 and step 2)
    # 5. Filter results obtained in step 4 according to the info fetchd in step 3 (eg. Allergies, fav_Cuisine)
    # 6. return final list
    return

def GetCurrentCart():
    # 1. Database query to fetch current cart products for the user

    uid = current_user.get_id()
    Cart_Products_Ids = Cart.query.filter(Cart.user_id == uid).all()

    Cart_Products = []
    for product in Cart_Products_Ids:
        Cart_Products.append(product.product_id)

    return Cart_Products


@app.route('/Home', methods = ['GET', 'POST'])
def LoadHomePage():
    # 1. call GetAllProducts() to get all products
    # 2. call GetCurrentCart() to get cart products
    # 3. render HomePage page with parameter value = above product list and cart list.

    All_Products = GetAllProducts()
    Cart_Products = GetCurrentCart()

    # For now, Only products are displayed with status (added or not in cart) here,
    # If part of screen is dedicated to display recommendations, AJAX is need to be used
    # Recommendations list will also need to be passed to page for OPTION 1

    return render_template('HomePage.html', ProductList=All_Products, Cart_Products=Cart_Products, Heading="All Products")


@app.route('/AddToCart/<ProductID>', methods = ['GET', 'POST'])
def AddToCart(ProductID):
    # 1. Get current User's ID to add product in particular user's cart.
    # 2. Get ProductID as a parameter.
    # 3. Add new entry in Cart table with above UserID and ProductID.
    # 4. Commit database after above entry.

    # For now: OPTION 1
    # 5. call GetPredictedProducts() and calculate runtime r1
    # 6. call GetSimilarProducts() and calculate runtime r2
    # 7. call GetComplementaryProducts() and calculate runtime r3
    # 8. call GetRecipeRecommendations() and calculate runtime r4
    # 9. Display result on terminal along with runtime (r1+r2, r1+r3, r1+r4)

    # Ideally, one of the function will be called out of step 6, 7, 8
    # according to the tab selected by the user in recommendatioin part of the page
    # and view will be updated with the new recommendations

    uid = current_user.get_id()
    CartObject = Cart(user_id = uid, product_id = ProductID)
    db.session.add(CartObject)
    db.session.commit()

    print("Added to Cart ProductID: ", ProductID)

    NextBuyProducts = GetPredictedProducts()

    return redirect('/Home')


def SearchProduct(SearchText):
    # 1. Database query to search products starting with / contains / similar to searchtext
    # 2. call GetCurrentCart() to get cart products
    # 3. Give output of step 1 and 2 as parameters to HomePage.html in below render_template call
    return render_template('HomePage.html', ProductList=Searched_products, Cart_Products=Cart_Products, Heading="Searched Products")


@app.route('/ViewCart', methods = ['GET', 'POST'])
def ViewCart():
    # 1. call GetCurrentCart() to get cart products
    # 2. Get corresponding product names from product detail table.
    # 3. render CartDetailPage with parameter = List of product names in cart.
    # 4. You can pass ProductID list along with is as list of key:value pair if ids are also required.

    return render_template('CartDetailPage.html', CartList=Cart_Product_Names)


## For now this function is not called as recommendations will be displayed on terminal only.
@app.route('/AddMissingProduct/<RecipeID>', methods = ['GET', 'POST'])
def AddMissingProduct(RecipeID):
    # 1. call GetCurrentCart() to get cart products
    # 2. Get RecipeID as paramter.
    # 3. DB query to get missing productIDs using above RecipeID and List of Cart ProductIDs.
    # 4. DB Query to get corresponding Product Names from Product Detail table.
    # 5. render HomePage page with parameter value = above queried list.

    return render_template('HomePage.html', ProductList=Missing_products, Cart_Products=Cart_Products, Heading="Missing Products")

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    return render_template('firstpage.html', message = "Logged out successfully")
