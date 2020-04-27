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
from app.models import User, Credentials, Product, Meal, MealDetails, Cart, UserDetails
import operator
from flask import jsonify

from app.Meal_Recommender.Predict_Ingredients import*
from app.Meal_Recommender.Predict_Recipes import*
from app.Meal_Recommender.Predict_Persona import*
from app.Meal_Recommender.Predict_Autoencoder import*
from app.Meal_Recommender.personalised_prediction import*

from app.Meal_Recommender.Predication_Transaction_History import *
Absolute_Trained_Model_Path = "/Users/pranjali/Downloads/SE_Project_UI/app/Trained_Models/"



@app.route('/')
def firstpage():
    return render_template('FirstPage.html',title='First Page')


@app.route('/Registration')
def Registration():
    return render_template('Register.html',title='Registration Page')

@app.route('/Logging', methods=["GET","POST"])
def Logging():
    return render_template('Login.html')

@app.route('/Food_Preference_Form', methods = ['GET', 'POST'])
def Food_Preference_Form():
    if request.method == 'POST':

        foodchoice = request.form.get('foodchoice')
        spiciness = request.form.get('spiciness')
        location = request.form.get('location')
        cuisines = request.form.getlist('cuisine')
        allergies = request.form.getlist('allergy')

        cuisines_str = ""
        for cuisine in cuisines:
            cuisines_str = cuisines_str + cuisine + ","

        if len(allergies) == 1:
            allergies_str = allergies[0]
        else:
            allergies_str = ""
            for allergy in allergies:
                allergies_str = allergies_str + allergy + ","

        Num_Users = int(max(Credentials.query.with_entities(Credentials.user_id))[0])
        UserDetail = UserDetails(user_id = Num_Users+1 , fav_cuisine = cuisines_str, spiciness = spiciness, food_choice = foodchoice, state = location, allergy = allergies_str)

        db.session.add(UserDetail)
        db.session.commit()

    return render_template('Login.html')

@app.route('/Food_Prefernce_Data', methods = ['GET', 'POST'])
def Food_Prefernce_Data():
    # Use post method as User Info should not be passed through URL.
    # 1. Get Food_Prefernce Form content by POST method.
    # 2. Add entry in User_Info table with user food_preference info and userid.
    # 3. Commit database changes.

    Rules_FilePath = Absolute_Trained_Model_Path + "Associative_Rules_Data/cuisines.csv"
    Predicted_Cuisines = Predict_Cuisines(Rules_FilePath)
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

          # Num_Users = len(User.query.all())
          Num_Users = int(max(Credentials.query.with_entities(Credentials.user_id))[0])
          user1 = User(user_id = Num_Users+1 , name = request.form['name'], email_id = request.form['email'], gender = request.form['gender'], age = request.form['age'])
          # Credential1 = Credentials(user_id = Num_Users+1, email_id = request.form['email'], password = pw_hash)
          Credential1 = Credentials(user_id = Num_Users+1, email_id = request.form['email'], password = password)

          db.session.add(user1)
          db.session.add(Credential1)
          db.session.commit()

          flash('Record was successfully added')

    # return render_template('Login.html')
    Product_List = GetAllProducts()
    return render_template('Food_Preference.html', ProductList = Product_List)


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
#
def GetProducts(ProductNames):
    Product_List = []
    for ProductName in ProductNames:
        product_n = Product.query.filter(Product.name == ProductName).first()
        if(product_n is not None):
            Product_Tuple = (product_n.product_id , product_n.name, product_n.price)
            print(Product_Tuple)
            Product_List.append(list(Product_Tuple))
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
    print("Type Test_Row_DF.iloc[0]: ", type(Test_Row_DF.iloc[0]))
    print("Test_Row_DF.iloc[0] shape: ", Test_Row_DF.iloc[0].shape)
    Ingredient_Prediction = Products_prediction(Cluster, uid, Test_Row_DF.iloc[0], Col_List, Absolute_Trained_Model_Path)

    # 5. Return lists
    Predicted_Products = []
    Cart_Product_obj = []
    for product_obj in All_Products:
        if product_obj[0] in Ingredient_Prediction:
            Predicted_Products.append(product_obj)
        if product_obj[0] in Cart_Products:
            Cart_Product_obj.append(product_obj)

    print("Cart Products: ", Cart_Product_obj)
    # print("Predicted_Products: ", Predicted_Products)

    return Predicted_Products

# Returns Object of products with Given Product Name
def GetProductObject(ProductName):
    # 1. Database query to fetch current cart products for the user
    product_n = Product.query.filter(Product.name == ProductName).first()
    Product_Tuple = [product_n.product_id , product_n.name, product_n.price]
    return Product_Tuple

# Returns List Product Objects on basis Apriori On Transaction History
def GetPredictedProductsBasedOnTransactionHistory():
    # Get Current Cart Product ID's
    Cart_Products = GetCurrentCart()
    # Get Current Cart Product Name's
    Cart_Products_Names=[]
    for cart_item in Cart_Products:
        Cart_Products_Names.append(GetProductName(cart_item))
    Cart_Products_Names.sort()
    Cart_Products_Names_Str=",".join(Cart_Products_Names)
    # Get Predicated_Product_Names_List

    Predicated_Products_Name=reterving_results_form_transaction_history(Cart_Products_Names_Str,Absolute_Trained_Model_Path)

    # Get Predicated_Product_Names_List to Predicated_Object_List

    Predicted_Products=[]
    for product in Predicated_Products_Name:
        if product not in Cart_Products_Names:
            Predicted_Products.append(GetProductObject(product))

    return Predicted_Products


def GetSimilarProducts(ProductID):
    Product_Name = GetProductName(ProductID)

    # 2. Database query to fetch user's personal info
    # 3. Call predict fuction of corresponding embedding model (Input: results from step 1)
    # 4. Filter results obtained in step 3 according to the info fetchd in step 2 (eg. Allergies)
    # 5. return final list
    ModelPath = Absolute_Trained_Model_Path + "Recommender_Data/word2vec_cl_new_ng7.model"
    return findSimilarIngredients(Product_Name, ModelPath)

def GetComplementaryProducts(ProductID):
    Product_Name = GetProductName(ProductID)

    # 2. Database query to fetch user's personal info
    # 3. Call predict fuction of corresponding embedding model (Input: results from step 1)
    # 4. Filter results obtained in step 3 according to the info fetchd in step 2 (eg. Allergies)
    # 5. return final list
    ModelPath = Absolute_Trained_Model_Path + "Recommender_Data/word2vec_cl_new_ng7.model"
    return findComplementaryIngredients(Product_Name, ModelPath)

def GetRecipeRecommendations(Cart_Products,Predicted_Products):
    # 1. Database query to fetch cart content fo current user
    Cart_Product_Names = []
    for ProductID in Cart_Products:
        Cart_Product_Names.append(GetProductName(ProductID))
    Predicted_Product_Names = []
    for Product in Predicted_Products:
        Predicted_Product_Names.append(Product[1])



    # 2. Call GetPredictedProducts() to get predicted products
    # 3. Database query to fetch user's personal info
    # 4. Call predict fuction of corresponding embedding model (Input: results from step 1 and step 2)
    # 5. Filter results obtained in step 4 according to the info fetchd in step 3 (eg. Allergies, fav_Cuisine)
    # 6. return final list
    ModelPath = Absolute_Trained_Model_Path + "Recommender_Data/word2vec_cl_new_ng7.model"
    VectorPath = Absolute_Trained_Model_Path + "Recommender_Data/culinaryDB_new_vectors.pkl"

    return suggest_recipe(Cart_Product_Names,Predicted_Product_Names, ModelPath, VectorPath)


def GetRecipesFromDBUtil(product_meal):
    # INTERSECTION
    Meal_Names = []
    Meal_Details = []
    if(len(product_meal) == 1):
        mcount = 1
        for meal_id in product_meal[0]:
            meal_n = MealDetails.query.filter(MealDetails.meal_id == meal_id).first()
            Meal_Names.append([meal_id,meal_n.name])
            mcount += 1
            if mcount > 5:
                break
    else:
        set1 = set(product_meal[0])
        for i in range(1,len(product_meal),1):
            set2 = set1.intersection(set(product_meal[i]))
            set1 = set2
        mcount = 1
        for meal_id in set1:
            meal_n = MealDetails.query.filter(MealDetails.meal_id == meal_id).first()
            Meal_Names.append([meal_id,meal_n.name])
            mcount += 1
            if mcount > 5:
                break
    # UNION
    meal_count = dict()
    for list_l in product_meal:
        for l in list_l:
            if l not in meal_count:
                meal_count[l] = 1
            else:
                meal_count[l] += 1
    meal_count = sorted(meal_count.items(), key=operator.itemgetter(1),reverse=True)
    meal_ids = []
    count = 1
    for i in meal_count:
        meal_ids.append(i[0])
        count += 1
        if count > 5:
            break
    for meal_id in meal_ids:
        meal_n = MealDetails.query.filter(MealDetails.meal_id == meal_id).first()
        Meal_Names.append([meal_id,meal_n.name])
    return Meal_Names

def GetRecipesFromDB(Cart_Products,Predicted_Products):
    Meal_Names = []
    # Meals from current cart
    product_meal = []
    for product_id in Cart_Products:
        meal_n = Meal.query.filter(Meal.product_id == product_id).all()
        meal_ids = []
        for meal in meal_n:
            meal_ids.append(meal.meal_id)
        product_meal.append(meal_ids)
    if len(product_meal):
        Meal_Names.extend(GetRecipesFromDBUtil(product_meal))

    # Meals from common ingredients of current cart and predicted products
    Common_Products = []
    for Product in Predicted_Products:
        if Product[0] in Cart_Products:
            Common_Products.append(Product[0])
    product_meal = []
    for product_id in Common_Products:
        meal_n = Meal.query.filter(Meal.product_id == product_id).all()
        meal_ids = []
        for meal in meal_n:
            meal_ids.append(meal.meal_id)
        product_meal.append(meal_ids)
    if len(product_meal):
        Meal_Names.extend(GetRecipesFromDBUtil(product_meal))

    if(len(Meal_Names) == 0):
        Product_Ids = []
        for Product in Predicted_Products:
            Product_Ids.append(Product[0])
        product_meal = []
        for product_id in Product_Ids:
            meal_n = Meal.query.filter(Meal.product_id == product_id).all()
            meal_ids = []
            for meal in meal_n:
                meal_ids.append(meal.meal_id)
            product_meal.append(meal_ids)
        Meal_Names.extend(GetRecipesFromDBUtil(product_meal))
    return Meal_Names

# Returns id of products in current cart
def GetCurrentCart():
    # 1. Database query to fetch current cart products for the user

    uid = current_user.get_id()
    Cart_Products_Ids = Cart.query.filter(Cart.user_id == uid).all()
    Cart_Products = []
    for product in Cart_Products_Ids:
        Cart_Products.append(product.product_id)

    return Cart_Products


# Returns name of product
def GetProductName(ProductID):
    # 1. Database query to fetch current cart products for the user
    product_n = Product.query.filter(Product.product_id == ProductID).first()
    return product_n.name

def GetMealDetails(MealIDs):
    # 1. Database query to fetch current cart products for the user
    Meal_Names = []
    Meal_Details = []
    for MealID in MealIDs:
        meal_n = MealDetails.query.filter(MealDetails.meal_id == MealID).first()
        # print("RECIPE NAME", meal_n.name)
        Meal_Names.append([MealID,meal_n.name])
        # ingredients = Meal.query.filter(Meal.meal_id == MealID).all()
        # ingredient_list = []
        # for ingredient in ingredients:
        #     ingredient_list.append(ingredient.product_id)
        # Meal_Details.append([MealID,ingredient_list])
            # print(GetProductName(ingredient.product_id))
    # return Meal_Names,Meal_Details
    return Meal_Names

def GetUserDetails():
    uid = current_user.get_id()
    userdetails_n = UserDetails.query.filter(UserDetails.user_id == uid).first()
    user_n = User.query.filter(User.user_id == uid).first()
    if(userdetails_n is not None):
        User_Details = (userdetails_n.user_id , userdetails_n.fav_cuisine, userdetails_n.spiciness,
            userdetails_n.food_choice,userdetails_n.state, userdetails_n.allergy, user_n.gender)
        return User_Details
    else:
        return None

def Predict_Cuisines(User_Details):
    Model_Path = Absolute_Trained_Model_Path + "Associative_Rules_Data/cuis_data.pkl"
    with open(Model_Path,'rb') as f:
        cuisine_model = pickle.load(f)
    return cuisine_model[User_Details[0]]

def Rank_By_Cuisine(cuisines,Recommendations):
    temp_cuisines = []
    for cuisine in cuisines:
        temp_cuisines.append(cuisine[1:-1])
    cuisine = temp_cuisines
    new_Recommendations = []
    data_path = Absolute_Trained_Model_Path+"/Associative_Rules_Data/Cuisines_Mapping.pkl"
    with open(data_path,'rb') as f:
        cuisine_mapping = pickle.load(f)
    meal_cuisines = []
    for i in Recommendations:
        meal_id = i[0]
        meal_cuisine = MealDetails.query.with_entities(MealDetails.meal_id == meal_id, MealDetails.cuisine).first()
        meal_cuisines.append((cuisine_mapping[meal_cuisine[1]],i))
    for i in meal_cuisines:
        for j in i[0]:
            if j in cuisine:
                new_Recommendations.append(i[1]) 
    for i in Recommendations:
        if i not in new_Recommendations:
            new_Recommendations.append(i)
    return new_Recommendations

def Filter_By_FoodChoice(food_choice,Recommendations):
    food_choice = food_choice.strip()
    nonveg = 'Non - Vegetarian'
    egg = 'Eggiterian'
    veg = 'Vegetarian'
    if((food_choice != egg) and (food_choice != veg)):
        return Recommendations
    data_path = Absolute_Trained_Model_Path+"/Recommender_Data/Food_Category.json"
    with open(data_path,'r') as f:
        food_choice_data = json.load(f)
    new_Recommendations = []
    for i in Recommendations:
        meal_id = i[0]
        ingredients = Meal.query.filter(Meal.meal_id == meal_id).all()
        ingredient_names = []
        for ingredient in ingredients:
            product_n = Product.query.filter(Product.product_id == ingredient.product_id).first()
            ingredient_names.append(product_n.name)
        if(food_choice == egg or food_choice == veg):
            if(len(set(ingredient_names).intersection(set(food_choice_data["Non-Veg"])))):
                continue
            else:
                if(food_choice == veg):
                    if(len(set(ingredient_names).intersection(set(food_choice_data["Egg"])))):
                        continue
                    else:
                        new_Recommendations.append(i)
                else:
                    new_Recommendations.append(i)
    return new_Recommendations


def Personalise_Recommendations(Recipe_Recommendations,DB_Recipe_Recommendations):
    User_Details = GetUserDetails()
    if User_Details is None:
        return Recipe_Recommendations,DB_Recipe_Recommendations
    else:
        cuisines = Predict_Cuisines(User_Details)
        Recipe_Recommendations = Filter_By_FoodChoice(User_Details[3],Recipe_Recommendations)
        DB_Recipe_Recommendations = Filter_By_FoodChoice(User_Details[3],DB_Recipe_Recommendations)
        return Rank_By_Cuisine(cuisines,Recipe_Recommendations),Rank_By_Cuisine(cuisines,DB_Recipe_Recommendations)


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
    uid = current_user.get_id()
    CartObject = Cart(user_id = uid, product_id = ProductID)
    db.session.add(CartObject)
    db.session.commit()


    print("ProductID: ", ProductID)
    # For now: OPTION 1
    # 5. call GetPredictedProducts() and calculate runtime r1
    # 6. call GetSimilarProducts() and calculate runtime r2
    # 7. call GetComplementaryProducts() and calculate runtime r3
    # 8. call GetRecipeRecommendations() and calculate runtime r4
    # 9. Display result on terminal along with runtime (r1+r2, r1+r3, r1+r4)

    # Ideally, one of the function will be called out of step 6, 7, 8
    # according to the tab selected by the user in recommendatioin part of the page
    # and view will be updated with the new recommendations

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
    Cart_Product_Ids = GetCurrentCart()

    # 2. Get corresponding product names from product detail table.
    Cart_Products = [[-1,'Dummy',100]] ## Dummy product added because of Jinja issue,
    for product_id in Cart_Product_Ids :
        Cart_Product = Product.query.filter(Product.product_id==product_id).first()
        Cart_Products.append([Cart_Product.product_id, Cart_Product.name, Cart_Product.price])

    # 3. render CartDetailPage with parameter = List of product names in cart.
    # 4. You can pass ProductID list along with is as list of key:value pair if ids are also required.
    return render_template('CartDetailPage.html', CartList=Cart_Products)


## For now this function is not called as recommendations will be displayed on terminal only.
@app.route('/AddMissingProduct/<RecipeID>', methods = ['GET', 'POST'])
def AddMissingProduct(RecipeID):
    # 1. call GetCurrentCart() to get cart products
    Cart_Product_Ids = GetCurrentCart()

    # 2. Get RecipeID as parameter.
    RecipeID = int(RecipeID)

    # 3. DB query to get missing productIDs using above RecipeID and List of Cart ProductIDs.
    # 4. DB Query to get corresponding Product Names from Product Detail table.

    Meal_Products = Meal.query.filter(Meal.meal_id == RecipeID).all()
    Meal_Product_Ids = []
    for product in Meal_Products:
        Meal_Product_Ids.append(product.product_id)

    Missing_products = []
    for meal_product in Meal_Product_Ids :
        if meal_product not in Cart_Product_Ids:
            Missing_product = Product.query.filter(Product.product_id==meal_product).first()
            Missing_products.append([Missing_product.product_id, Missing_product.name, Missing_product.price])

    # 5. render HomePage page with parameter value = above queried list.
    return render_template('HomePage.html', ProductList=Missing_products, Cart_Products=Cart_Product_Ids, Heading="Missing Products")

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    user = current_user
    user.is_authenticated = False
    logout_user()
    return render_template('firstpage.html', message = "Logged out successfully")

@app.route('/ViewSimilar/<ProductID>', methods = ['GET', 'POST'])
def SimilarProducts(ProductID):
    Cart_Product_Ids = GetCurrentCart()
    Similar_Products = GetSimilarProducts(ProductID)
    Similar_Products = GetProducts(Similar_Products)
    # return jsonify(ProductList=All_Products, Cart_Products=Cart_Products)
    return render_template('HomePage.html', ProductList=Similar_Products, Cart_Products=Cart_Product_Ids, Heading="Similar Products")

@app.route('/ViewComplement/<ProductID>', methods = ['GET', 'POST'])
def ComplementProducts(ProductID):
    Cart_Product_Ids = GetCurrentCart()
    Complement_Products = GetComplementaryProducts(ProductID)
    Complement_Products = GetProducts(Complement_Products)
    # return jsonify(ProductList=All_Products, Cart_Products=Cart_Products)
    return render_template('HomePage.html', ProductList=Complement_Products, Cart_Products=Cart_Product_Ids, Heading="Complement Products")

@app.route('/Recommendations', methods = ['GET', 'POST'])
def Recommendations():
    Predicted_Products = []
    Cart_Product_Ids = GetCurrentCart()
    Predicted_Products = GetPredictedProducts()
    print("COLLABORATIVE FILTERING RESULTS", Predicted_Products)
    AR_Predicted_Products = GetPredictedProductsBasedOnTransactionHistory()
    print("ASSOCIATIVE RULE RESULTS", AR_Predicted_Products)
    Predicted_Products.extend(AR_Predicted_Products)
    Recipe_Recommendations = GetRecipeRecommendations(Cart_Product_Ids,Predicted_Products)
    Recipe_Recommendations = GetMealDetails(Recipe_Recommendations)
    DB_Recipe_Recommendations = GetRecipesFromDB(Cart_Product_Ids,Predicted_Products)
    Cart_Products = []
    for product_id in Cart_Product_Ids:
        Cart_Products.append([product_id,GetProductName(product_id)])
    Recipe_Recommendations,DB_Recipe_Recommendations = Personalise_Recommendations(Recipe_Recommendations,DB_Recipe_Recommendations)
    if len(Recipe_Recommendations)>10:
        Recipe_Recommendations = Recipe_Recommendations[:10]
    if len(DB_Recipe_Recommendations)>10:
        DB_Recipe_Recommendations = DB_Recipe_Recommendations[:10]
    return render_template('MealRecommendation.html',MealList = Recipe_Recommendations,DbMealList = DB_Recipe_Recommendations,CartProducts = Cart_Products)

@app.route('/RemoveFromCart/<ProductID>', methods = ['GET', 'POST'])
def RemoveFromCart(ProductID):
    uid = current_user.get_id()
    CartObject = Cart.query.filter(Cart.user_id == uid).filter(Cart.product_id == ProductID).first()
    db.session.delete(CartObject)
    db.session.commit()
    return redirect('/Home')

@app.route('/AddMealToCart/<MealId>',methods = ['GET', 'POST'])
def AddMealToCart(MealId):
    uid = current_user.get_id()
    Cart_Product_Ids = GetCurrentCart()
    Meal_Products = Meal.query.filter(Meal.meal_id == MealId).all()
    Meal_Product_Ids = []
    for product in Meal_Products:
        Meal_Product_Ids.append(product.product_id)
    for product_id in Meal_Product_Ids:
        if product_id not in Cart_Product_Ids:
            CartObject = Cart(user_id = uid, product_id = product_id)
            db.session.add(CartObject)
            db.session.commit()
    return redirect('/Home')
