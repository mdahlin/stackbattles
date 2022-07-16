# importing the required libraries
import pandas as pd
import numpy as np
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost.sklearn import XGBRegressor
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn import tree
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
import pickle as pkl

with open("model_data.pkl", 'rb') as pkl_file:
    data = pkl.load(pkl_file)


X = data.drop('wins', 1)
y = data["wins"]

X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = .2, random_state=42)

shap.initjs()

xgb_model = XGBRegressor(n_estimators=1000, max_depth=10, learning_rate =0.001, randomstate=0)
results = xgb_model.fit(X_train, y_train)

y_predict = xgb_model.predict(X_test)

print(mean_squared_error(y_test, y_predict)**(0.5))
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_train)
print(shap_values)
#shap.summary_plot(shap_values, features = X_train, feature_names = X_train.columns)


