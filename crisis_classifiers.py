# -*- coding: utf-8 -*-
"""crisis_classifiers.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Cs_oWgovqd2GLQVQnShfXGaBProIQrS6

#Importing Libraries
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import re
from sklearn.preprocessing import OneHotEncoder
import plotly.offline as po
import plotly.graph_objs as pg

import nltk
nltk.download('stopwords')
#nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report

import pickle

"""#Functions"""

def graph_plot(x, y, title, x_label, y_label):
  fig, ax = plt.subplots(figsize = (30,10), sharey=True)
  ax.plot(x, y)
  ax.set_title(title)
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  ax.xaxis.set_tick_params(rotation=90)
  plt.show()

def graph_bar(x, y, title, x_label, y_label):
  fig, ax = plt.subplots(figsize = (30,10))
  ax.bar(x, y)
  ax.set_title(title)
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  ax.xaxis.set_tick_params(rotation=90)
  plt.show()

def mapa_event(event):
  data_mapa = dict(type='choropleth', 
            locations = group_country['iso'], 
            z = group_country[event], 
            text = group_country['country'])
  layout = dict(title = elem, 
              geo = dict( projection = {'type':'robinson'}, 
                         showlakes = True, 
                         lakecolor = 'rgb(0,191,255)'))
  x = pg.Figure(data = [data_mapa], 
              layout = layout)
  po.iplot(x)

rcParams.update({'font.size': 20})

"""# Loading dataset






"""

from google.colab import drive
drive.mount('/content/drive')

path = '/content/drive/MyDrive/Colab Notebooks/projekt koncowy/2019-08-13-2022-08-22 (1).csv'

"""# Observing the data"""

data = pd.read_csv(path)

data.columns

data.dtypes

data['event_date'] = pd.to_datetime(data['event_date'])

data.dtypes

df_0 = data.drop(columns = ['data_id','iso','event_id_cnty','event_id_no_cnty','time_precision','actor1','assoc_actor_1','actor2','assoc_actor_2','geo_precision','timestamp','fatalities','admin1','admin2','admin3','iso3'])
df_0.sample(3)

enc = OneHotEncoder()

df_1 = pd.DataFrame(enc.fit_transform(df_0[['event_type']]).toarray(), columns = enc.categories_)
df_1.columns = df_1.columns.map(''.join)
df_2 = pd.DataFrame(enc.fit_transform(df_0[['sub_event_type']]).toarray(), columns = enc.categories_)
df_2.columns = df_2.columns.map(''.join)
df = pd.concat((df_0['event_date'],df_0.drop(columns = ['event_date']), df_1, df_2) ,axis = 1)
df.sample(3)

"""# Visualizing data

##World map with the sum of the incidents
"""

group_country = df.groupby(['country']).sum().reset_index()
data_iso = data[['country','iso3']].drop_duplicates().sort_values('country').reset_index()
data_iso = data_iso[['iso3']]
group_country['iso'] = data_iso

for elem in df['event_type'].unique():  
  mapa_event(elem)
  print()

"""##Top5"""

print(f'Top 5 countries for all types of event')
print(df['country'].value_counts().head())
x_top_all = df['country'].value_counts().head().index
y_top_all = df['country'].value_counts().head().values
graph_bar(x_top_all, x_top_all, f'Top 5 countries for {elem}', '', 'Amount')
print()

for elem in df['event_type'].unique():
  print(f'Top 5 countries for {elem}')
  x_top = df[df['event_type']==elem]['country'].value_counts().head().index
  y_top = df[df['event_type']==elem]['country'].value_counts().head().values
  print(df[df['event_type']==elem]['country'].value_counts().head())
  graph_bar(x_top, y_top, f'Top 5 countries for {elem}', '', 'Amount')
  print()

"""##Distribution of incidents"""

start = df['event_date'].max()
end = df['event_date'].max()

df_event_date = df.groupby(['event_date']).sum().reset_index()
df_event_date.sample(3)

for elem in df['event_type'].unique():
  graph_plot(df_event_date['event_date'], df_event_date[elem], f'Amount of {elem} from {start} to {end}','', 'Amount')
  print()

"""## Total incidents per region"""

df_region = df.groupby(['region']).sum().reset_index()
df_region.sample(3)

for elem in df['event_type'].unique():  
  graph_bar(df_region['region'], df_region[elem], f'Amount of {elem} from {start} to {end} in all regions', '', 'Amount')
  print()

"""##Poland"""

df_poland = df[df['country']=='Poland']

df_poland_event_type_0 = df_poland['event_type'].unique()
amount_poland = []
event_type_poland = []

for elem in df_poland['event_type'].unique():
  event_type_poland.append(elem)
  amount_poland.append(df_poland[elem].sum())

graph_bar(event_type_poland, amount_poland, f'Amount of event type from {start} to {end} in Poland','', 'Amount')
print()

df_event_date_poland = df_poland.groupby(['event_date']).sum().reset_index()

graph_plot(df_event_date_poland['event_date'], df_event_date_poland['Protests'], f'Amount of Protests from to {end}', '', 'Amount')

"""#Model NLP

##Preproccesing
"""

data_model = data[['event_type','notes']]
data_model.sample(3)

data_model['event_type'].value_counts()

limit = min(data_model['event_type'].value_counts())
limit

data_model_limit_1 = data_model[data_model['event_type']=='Riots'].sample(limit)
data_model_limit_2 = data_model[data_model['event_type']=='Strategic developments'].sample(limit)
data_model_limit_3 = data_model[data_model['event_type']=='Protests'].sample(limit)
data_model_limit_4 = data_model[data_model['event_type']=='Violence against civilians'].sample(limit)
data_model_limit_5 = data_model[data_model['event_type']=='Battles'].sample(limit)
data_model_limit_6 = data_model[data_model['event_type']=='Explosions/Remote violence'].sample(limit)

data_model_limit = pd.concat([data_model_limit_1,data_model_limit_2,data_model_limit_3,data_model_limit_4,data_model_limit_5,data_model_limit_6],  ignore_index=True)
data_model_limit['event_type'].value_counts()

data_model_limit = data_model_limit.sample(frac=1).reset_index(drop=True)
data_model_limit

X_0 = data_model_limit['notes']
y = data_model_limit['event_type']

"""###Regex"""

re_1 = re.compile(r'\d\d\d\d.\s(.*).\[.*$')
re_2 = re.compile(r'\d\d\d\d.\s(.*).')
re_3 = re.compile(r'\W\s(.*).')
re_4 = re.compile(r'\W\s(.*).\[.*$')

def f_regex(x):
  try:
    re = re_1.search(x).group(1)
  except:
    try:
      re = re_2.search(x).group(1)
    except:
        try:
         re = re_3.search(x).group(1) 
        except:
          try:
            re = re_4.search(x).group(1) 
          except:
            re = x
  return re

X_re = X_0.apply(f_regex)

"""###Small letter"""

X_lower = X_re.map(lambda x: x.lower())

"""###Tokenize"""

X_tokenize = X_lower.map(lambda x: word_tokenize(x))

"""###Stopwords and lemmatize"""

stopWords = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

interpunction = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', ':', ';', '<', '=', '>', '?', '@', '[', '', ']', '^', '_', '`', '{', '|', '}', '~']
X_lematizer = []
X = []

for n in range(len(X_tokenize)):
  for m in range(len(X_tokenize[n])):
    X_lematizer.append([])
    if X_tokenize[n][m] not in stopWords:
      if X_tokenize[n][m].isdigit()==False:
        if X_tokenize[n][m] not in interpunction:
            X_lematizer[n].append(lemmatizer.lemmatize(X_tokenize[n][m]))
  X.append(' '.join(X_lematizer[n]))

"""##Train/test split"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)

"""##TFIDF"""

tfidf = TfidfVectorizer()
tfidf.fit(X_train)

X_train_tf = tfidf.transform(X_train)
X_test_tf = tfidf.transform(X_test)

"""##Logistic regression"""

lr = LogisticRegression(max_iter = len(X))
lr.fit(X_train_tf, y_train)
y_pred_lr = lr.predict(X_test_tf)

print(classification_report(y_test, y_pred_lr))

"""##RandomForestClassifier"""

rfc = RandomForestClassifier(n_estimators=50, max_depth=5, min_samples_split=5)
rfc.fit(X_train_tf, y_train)
y_pred_rfc = rfc.predict(X_test_tf)

print(classification_report(y_test, y_pred_rfc))

"""##Naive Bayes"""

mnb = MultinomialNB()
mnb.fit(X_train_tf, y_train)
y_pred_mnb = mnb.predict(X_test_tf)

print(classification_report(y_test, y_pred_mnb))

"""#Testing best model for random examples"""

best_model = lr

print('Enter your text: ')
test_bm = [input()]
X_lower = test_bm[0].lower()
X_tokenize = word_tokenize(X_lower)

X_lematizer = []
X = []


for m in range(len(X_tokenize)):
  if X_tokenize[m] not in stopWords:
    if X_tokenize[m].isdigit()==False:
      if X_tokenize[m] not in interpunction:
          X_lematizer.append(lemmatizer.lemmatize(X_tokenize[m]))
X = [' '.join(X_lematizer)]

X_test_bm = tfidf.transform(X)
y_pred_bm = best_model.predict(X_test_bm)
print()
print(f'Predicted class is {y_pred_bm}')
print()
print(best_model.classes_)
print()
y_pred_bm = best_model.predict_proba(X_test_bm)
print()
print(y_pred_bm)