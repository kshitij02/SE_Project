# -*- coding: utf-8 -*-
"""Personalised_Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Z8yLj7vGxRW8dCbePakSJTr8AMl2_JvS
"""

import pandas as pd
import numpy as np
import itertools

def read_file(Rules_FilePath):
  dataset = pd.read_csv(Rules_FilePath)
  return dataset

def process_input_data(dataset):
  inp=dataset['Input'].values.tolist()
  ans=[]
  for i in range(len(inp)):
    li=[]
    strs=" "
    var=inp[i]
    for j in range(len(inp[i])):
      if var[j]==',':
        li.append(strs)
        strs=" "
      else:
        strs=strs+inp[i][j]
    li.append(strs)
    ans.append(li)
  for i in range(len(ans)):
    ans[i] = [x.strip(' ') for x in ans[i]]
  return ans

def process_output_data(dataset):
  ou=dataset['Output'].values.tolist()
  ans1=[]
  for i in range(len(ou)):
    lis=[]
    strs1=" "
    var=ou[i]
    for j in range(len(ou[i])):
      if var[j]==',':
        lis.append(strs1)
        strs1=" "
      else:
        strs1=strs1+ou[i][j]
    lis.append(strs1)
    ans1.append(lis)
  for i in range(len(ans1)):
    ans1[i] = [x.strip(' ') for x in ans1[i]]
  return ans1

def sort(data):
  for i in range(len(data)):
    data[i].sort()
  return data

def make_dict(ans,ans1):
  inps=[]
  for i in range(len(ans)):
    li=ans[i]
    listToStr = ','.join([str(elem) for elem in li])
    inps.append(listToStr)
  out={}
  for i in range(0,len(ans)):
    out[inps[i]]=(ans1[i])
  return out

def find_subsets(li,num):
  return list(itertools.combinations(li, num))

def Predict_Cuisines(Rules_FilePath, gender=None,fav_cuisine=None,spiciness=None,food_choice=None,allergy=None,state=None):
  dataset=read_file(Rules_FilePath)
  ans=process_input_data(dataset)
  ans1=process_output_data(dataset)
  ans_sort=sort(ans)
  ans1_sort=sort(ans1)
  out=make_dict(ans_sort,ans1_sort)
  li=[]
  if gender is not 'None':
    li.append(gender)
  if spiciness is not 'None':
    li.append(spiciness)
  if food_choice is not 'None':
    li.append(food_choice)
  if allergy is not 'None':
    li.append(allergy)
  if state is not 'None':
    li.append(state)
  length=len(fav_cuisine)
  for g1 in range(length):
    li.append(fav_cuisine[g1])
  li.sort()
  length_li=len(li)
  num=len(li)
  # print(li)
  num=num+1
  while num!=0:
    sub=find_subsets(li,num)
    # print(sub)
    for r1 in range(len(sub)):
      w1=[]
      for y1 in range(len(sub[r1])):
        w1.append(sub[r1][y1])
      w1.sort()
      # print(w1)
      if w1 in ans:
        # print(w1)
        listToStr = ','.join([str(elem) for elem in w1])
        # print(listToStr)
        return out[listToStr]
    num=num-1
