
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
from .Predict_Ingredients import *
import operator


def getCommonComplements(current_ingredients, ModelPath):
    complements = []
    for ingredient in current_ingredients:
        complements.append(findComplementaryIngredients(ingredient, ModelPath))
    complement_count = dict()
    for list_l in complements:
        for l in list_l:
            if l not in complement_count:
                complement_count[l] = 1
            else:
                complement_count[l] += 1
    complement_count = sorted(complement_count.items(), key=operator.itemgetter(1),reverse=True)
    count = 1
    complements = []
    for i in complement_count:
        complements.append(i[0])
        count += 1
        if count > 20:
            break
    return complements


def suggest_recipe(current_ingredients,predicted_ingredients, ModelPath, VectorsPath):
    if(len(current_ingredients) == 0):
        complements = getCommonComplements(predicted_ingredients, ModelPath)
        complements = complements[:5]
        current_ingredients = predicted_ingredients 
    else:       
        complements = getCommonComplements(current_ingredients, ModelPath)
        complements = set(complements)
        complements = complements.intersection(set(predicted_ingredients))
    current_ingredients.extend(list(complements))
    recommended_recipes = []
    id_vector = dict()
    with open(VectorsPath,'rb') as f:
        id_vector = pickle.load(f)
    model = Word2Vec.load(ModelPath)
    model.init_sims(replace=True)
    n = len(current_ingredients)
    current_sum = np.zeros(100)
    for ingredient in current_ingredients:
        vector = model.wv[ingredient]
        current_sum = np.add(current_sum,vector)
    current_sum = current_sum/n
    current_sum = current_sum.reshape(1,-1)
    id_cos = []
    for recipe_id in id_vector:
        vector = id_vector[recipe_id]
        flag = 0
        for v in vector:
            if math.isnan(v):
                flag = 1
                break
        if flag == 1:
            continue
        # x = cosine_similarity(current_sum,vector.reshape(1,-1))
        x = np.dot(current_sum,vector.reshape(-1,1))
        id_cos.append((x,recipe_id))
    id_cos = sorted(id_cos,reverse=True)
    count = 0
    for i in id_cos:
        recommended_recipes.append(i[1])
        count += 1
        if(count>20):
            break
    return recommended_recipes
