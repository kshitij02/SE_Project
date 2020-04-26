
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


def getCommonComplements(current_ingredients, ModelPath):
    complements = []
    for ingredient in current_ingredients:
        complements.append(findComplementaryIngredients(ingredient, ModelPath))
    set1 = complements[0]
    set1 = set(set1)
    for i in range(1,len(complements),1):
        set2 = set1.intersection(set(complements[i]))
        set1 = set2
    return list(set1)


def suggest_recipe(current_ingredients, ModelPath, VectorsPath):
    complements = getCommonComplements(current_ingredients, ModelPath)
    print("COMPLEMENTS", complements)
    current_ingredients.extend(complements)
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
        x = cosine_similarity(current_sum,vector.reshape(1,-1))
        id_cos.append((x,recipe_id))
    id_cos = sorted(id_cos,reverse=True)
    count = 0
    for i in id_cos:
        recommended_recipes.append(i[1])
        count += 1
        if(count>10):
            break
    return recommended_recipes
