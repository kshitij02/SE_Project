import pandas as pd
import numpy as np
import json
import pickle
import gensim
from gensim.models import Word2Vec
from gensim.models.keyedvectors import KeyedVectors
import csv
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import math

# def findIngredientId(ingredients):
#     with open('/Trained_Models/culinaryDB_new_products_id.pkl','rb') as f:
#         product_id = pickle.load(f)
#     ingredient_ids = []
#     for ingredient in ingredients:
#         ingredient_ids.append(product_id[ingredient])
#     return ingredient_ids

def findSimilarIngredientsUtil(current_ingredient,ModelPath, number_of_items=10):
    model = Word2Vec.load(ModelPath)
    model.init_sims(replace=True)
    current_vector = model.wv.get_vector(current_ingredient)
    vectors = []
    vectors = model.wv.vectors
    distances = np.dot(vectors,current_vector)
    sorted_distances = gensim.matutils.argsort(distances, topn=number_of_items+1, reverse=True)
    smallest_distances = sorted_distances[:number_of_items+1]
    similar_ingredients = []
    for i in smallest_distances:
        if i != model.wv.vocab[current_ingredient].index:
            similar_ingredients.append(model.wv.index2word[i])
    return similar_ingredients

def findComplementaryIngredientsUtil(current_ingredient, ModelPath, number_of_items=10):
    model = Word2Vec.load(ModelPath)
    # model.init_sims(replace=True)
    current_vector = model.wv.get_vector(current_ingredient)
    vectors = []
    vectors=model.trainables.syn1neg
    distances = np.dot(vectors,current_vector)
    sorted_distances = gensim.matutils.argsort(distances, topn=number_of_items+1, reverse=True)
    smallest_distances = sorted_distances[:number_of_items+1]
    complementary_ingredients = []
    for i in smallest_distances:
        if i != model.wv.vocab[current_ingredient].index:
            complementary_ingredients.append(model.wv.index2word[i])
    return complementary_ingredients

def findSimilarIngredients(current_ingredient, ModelPath):
    # similar_ingredients = dict()
    # for ingredient in current_ingredients:
    #     similar_ingredients[ingredient] = findSimilarIngredientsUtil(ingredient)
    # return similar_ingredients
    return findSimilarIngredientsUtil(current_ingredient, ModelPath)

def findComplementaryIngredients(current_ingredient, ModelPath):
    # complementary_ingredients = []
    # for ingredient in current_ingredients:
    #     complementary_ingredients.append(findComplementaryIngredientsUtil(ingredient))
    # return complementary_ingredients
    return findComplementaryIngredientsUtil(current_ingredient, ModelPath)
