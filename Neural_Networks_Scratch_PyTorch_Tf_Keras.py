# -*- coding: utf-8 -*-
"""SML Assignment 4 - Problem 1

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12GCW7rs334siUz7P9w5IhNtD35KQYl4k
"""

# In order to avoid CV issues for using Keras Classifier, make sure tensorflow version is 2.9.0 or higher. I used 2.9.0
# Data Preparation
import pandas as pd
import numpy as np
# Neural Network
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
# Performance
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_curve, auc, make_scorer, roc_auc_score
#Model Performance
from sklearn.model_selection import cross_val_score, cross_val_predict
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.pipeline import Pipeline

dataset_size = [250, 1000, 10000]
h1_nodes = [1, 4, 12]
h2_nodes = [0,3]
acc, balanced_acc, area_uc, cv_acc, cv_roc, true_acc, size, h1_node, h2_node = [], [], [], [], [], [], [], [], []
for d_size in dataset_size:
  for h1 in h1_nodes:
    for h2 in h2_nodes:
      # Generate data based on the figure
      x = np.random.uniform(low = -6, high = 6, size = d_size)
      y = np.random.uniform(low = -4, high = 4, size = d_size)

      # Define a function to check if the generated point lies in the square (Class: Positive) or outside (Class: Negative)
      def point_in_square(bl, tr, point):
        if (point[0] > bl[0] and point[0] < tr[0] and point[1] > bl[1] and point[1] < tr[1]):
          return True
        else:
          return False

      # Define a function to generate the training data (With noise introduced)
      # The data_type parameter can only take 2 values "train" or "validation"
      def create_data(x,y,data_type):
        df = pd.DataFrame()
        df['x'] = x
        df['y'] = y
        part_a = [[(-4,0),(-1,3)],[(-2,-4),(1,-1)],[(2,-2),(5,1)]]
        part_b = [[(-4,2),(-3,3)],[(-1,-3),(0,-2)],[(2,-1),(2,1)]]
        # point_combinations = [[(-4,0),(-1,3)],[(-2,-4),(1,-1)],[(2,-2),(5,1)],[(-4,2),(-3,3)],[(-1,-3),(0,-2)],[(2,-1),(2,1)]]
        num = 1
        for point in part_b:
          bl = point[0]
          tr = point[1]
          label = []
          # print(num)
          for i in range(len(x)):
            if point_in_square(bl,tr,[x[i],y[i]]) == True:
              label.append(True)
            else:
              label.append(False)
          col_name = "case_"+str(num)
          # print(col_name)
          df[col_name] = label
          num = num + 1

        label = []
        for i in range(df.shape[0]):
          temp = []
          for j in range(2,df.shape[1]):
            temp.append(df.iloc[i,j])
          if True in temp:
            label.append(1)
          else:
            label.append(0)

        df["Label"] = label
        temp_df = df
        df = temp_df[['x','y','Label']]
        df
        # print(df['Label'].value_counts())

        if data_type == "train":
        #Find Class Distribution and Change the Class Labels to introduce noise
          class_dist = df['Label'].value_counts()
          neg = round(class_dist.max()*0.03)
          pos = round(class_dist.min()*0.01)
          print("Values to change from class 0: ", neg)
          print("Values to change from class 1: ", pos)

          changed_pos, changed_neg = 0, 0
          for i in range(df.shape[0]):
            if df['Label'][i] == 1:
              if changed_pos < pos:
                df.loc[i,'Label'] = 0
                changed_pos+=1
            else:
              if changed_neg < neg:
                df.loc[i,'Label'] = 1
                changed_neg+=1

          # print(df["Label"].value_counts())
          return df
        else:
          return df

      df = create_data(x,y,"train")

      # Build a single and double hidden layer Neural Network:
      # Splitting data into train, test and dev sets
      X = df[['x','y']].values
      y = df['Label'].values
      df

      scaler = StandardScaler()
      X_scaled = scaler.fit_transform(X)

      X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size = 0.25) #Separate Test Set
      X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2) #Validation Set While Training

      #Building a Simple Neural Network with early stopping criterion
      # def create_model(model_type):
      #   model = Sequential()
      #   model.add(Dense(16, activation = "tanh", input_shape = (2,)))
      #   model.add(Dense(h1, activation = "tanh"))
      #   if h2 != 0:
      #     model.add(Dense(h2, activation = "tanh"))
      #   model.add(Dense(1, activation = "sigmoid"))
      #   model.compile(optimizer = "adam", loss = "binary_crossentropy", metrics = ['accuracy'])
      #   if model_type == "train":
      #     early_stopping = tf.keras.callbacks.EarlyStopping(monitor = "val_loss", patience = 5, restore_best_weights = True)
      #     model.fit(X_train, y_train, epochs = 100, batch_size = 25, validation_data = (X_val, y_val), callbacks = [early_stopping], verbose = 0)
      #     return model
      #   else:
      #     return model


      # model = create_model("train")
      # print(model.summary())
      model = Sequential()
      model.add(Dense(16, activation = "tanh", input_shape = (2,)))
      model.add(Dense(h1, activation = "tanh"))
      if h2 != 0:
        model.add(Dense(h2, activation = "tanh"))
      model.add(Dense(1, activation = "sigmoid"))
      model.compile(optimizer = "adam", loss = "binary_crossentropy", metrics = ['accuracy'])

      early_stopping = tf.keras.callbacks.EarlyStopping(monitor = "val_loss", patience = 5, restore_best_weights = True)

      model.fit(X_train, y_train, epochs = 100, batch_size = 25, validation_data = (X_val, y_val), callbacks = [early_stopping], verbose = 0)

      loss, accuracy = model.evaluate(X_test, y_test)
      print(loss, accuracy)

      #Performance Criteria - Accuracy, Balanced Accuracy, Area under ROC curve

      y_pred = model.predict(X_test)
      accuracy = accuracy_score(y_test, y_pred.round())
      balanced_accuracy = balanced_accuracy_score(y_test, y_pred.round())

      fpr, tpr, thresholds = roc_curve(y_test, y_pred)
      roc_auc = auc(fpr,tpr)

      print("Accuracy: " ,accuracy, ", Balanced Accuracy: ", balanced_accuracy, "Area Under ROC Curve: ", roc_auc)

      # plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
      # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
      # plt.xlabel('False Positive Rate')
      # plt.ylabel('True Positive Rate')
      # plt.title('Receiver Operating Characteristic (ROC) Curve')
      # plt.show()

      #Model Performace - Cross Validation

      # X = df[['x','y']].values
      # y = df['Label'].values
      roc_auc_scorer = make_scorer(roc_auc_score, greater_is_better = True)

      def create_model():
        model = Sequential()
        model.add(Dense(16, activation='tanh', input_shape=(2,)))
        model.add(Dense(h1, activation='tanh'))
        if h2 != 0:
          model.add(Dense(h2, activation = 'tanh'))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

      keras_clf = KerasClassifier(build_fn = create_model, epochs = 10, batch_size = 25)

      # 5-Fold Cross Validation
      cross_val_accuracy = cross_val_score(keras_clf, X_scaled,y, cv = 5, scoring = "accuracy")
      cross_val_roc_auc = cross_val_score(keras_clf, X_scaled,y, cv = 5, scoring = roc_auc_scorer)

      print("CV Accuracy: ", cross_val_accuracy, ", CV ROC AUC: ", cross_val_roc_auc)
      print("####################### Model Compilation and Results Generated Successfully ##############################")


      #Performance of Performance Evaluation
      # Generating a Huge Dataset 3000 points without noise to calculate true accuracy for the model
      a = np.random.uniform(low = -6, high = 6, size = 6000)
      b = np.random.uniform(low = -4, high = 4, size = 6000)
      val_df = create_data(a,b,"validation")

      X_val_scaled = scaler.fit_transform(val_df[['x','y']].values)
      y_val = val_df['Label'].values

      y_val_pred = model.predict(X_val_scaled)
      accuracy_val = accuracy_score(y_val, y_val_pred.round())
      balanced_accuracy_val = balanced_accuracy_score(y_val, y_val_pred.round())

      fpr_val, tpr_val, thresholds_val = roc_curve(y_val, y_val_pred)
      roc_auc_val = auc(fpr_val,tpr_val)

      print("True Accuracy: " ,accuracy_val, ",True Balanced Accuracy: ", balanced_accuracy_val, "True Area Under ROC Curve: ", roc_auc_val)

      acc.append(accuracy)
      balanced_acc.append(balanced_accuracy)
      area_uc.append(roc_auc)
      cv_acc.append(cross_val_accuracy)
      cv_roc.append(cross_val_roc_auc)
      true_acc.append(accuracy_val)
      size.append(d_size)
      h1_node.append(h1)
      h2_node.append(h2)

final_df = pd.DataFrame()
final_df["Dataset_Size"] = size
final_df["H1_Nodes"] = h1_node
final_df["H2_Nodes"] = h2_node
final_df["Accuracy"] = acc
final_df["Balanced Accuracy"] = balanced_acc
final_df["ROC_AUC"] = area_uc
final_df["CV_Accuracy"] = cv_acc
final_df["CV_ROC"] = cv_roc
final_df["True_Accuracy"] = true_acc

final_df

final_df_part_b = final_df

from google.colab import drive
drive.mount('/content/gdrive')

final_df_part_b.to_csv('/content/gdrive/My Drive/SML Assignment 4/Part_B_Results.csv', index=True, header = True)

def create_model():
  model = Sequential()
  model.add(Dense(16, activation = "tanh", input_shape = (2,)))
  model.add(Dense(h1, activation = "tanh"))
  if h2 != 0:
    model.add(Dense(h2, activation = "tanh"))
  model.add(Dense(1, activation = "tanh"))
  model.compile(optimizer = "adam", loss = "binary_crossentropy", metrics = ['accuracy'])
  return model

######## Individual Code Blocks

import pandas as pd
import numpy as np

x = np.random.uniform(low = -6, high = 6, size = 10000)
y = np.random.uniform(low = -4, high = 4, size = 10000)

def point_in_square(bl, tr, point):
  if (point[0] > bl[0] and point[0] < tr[0] and point[1] > bl[1] and point[1] < tr[1]):
    return True
  else:
    return False

# case1, case2, case3, case4, case5, case6 = [], [], [], [], [], []
# for i in range(len(x)):
#   bl = (-4,0)
#   tr = (-1,3)
#   # print(point_in_square(bl, tr, [x[i],y[i]]))

df = pd.DataFrame()
df['x'] = x
df['y'] = y
df

part_a = [[(-4,0),(-1,3)],[(-2,-4),(1,-1)],[(2,-2),(5,1)]]
part_b = [[(-4,2),(-3,3)],[(-1,-3),(0,-2)],[(2,-1),(3,0)]]
# point_combinations = [[(-4,0),(-1,3)],[(-2,-4),(1,-1)],[(2,-2),(5,1)],[(-4,2),(-3,3)],[(-1,-3),(0,-2)],[(2,-1),(2,1)]]
num = 1
for point in part_b:
  bl = point[0]
  tr = point[1]
  label = []
  # print(num)
  for i in range(len(x)):
    if point_in_square(bl,tr,[x[i],y[i]]) == True:
      label.append(True)
    else:
      label.append(False)
  col_name = "case_"+str(num)
  # print(col_name)
  df[col_name] = label
  num = num + 1

df

label = []
for i in range(df.shape[0]):
  temp = []
  for j in range(2,df.shape[1]):
    temp.append(df.iloc[i,j])
  if True in temp:
    label.append(1)
  else:
    label.append(0)

df["Label"] = label
temp_df = df
df = temp_df[['x','y','Label']]
df
print(df['Label'].value_counts())

#Find Class Distribution and Change the Class Labels to introduce noise
class_dist = df['Label'].value_counts()
neg = round(class_dist.max()*0.03)
pos = round(class_dist.min()*0.01)
print(neg, pos)

changed_pos, changed_neg = 0, 0
for i in range(df.shape[0]):
  if df['Label'][i] == 1:
    if changed_pos < pos:
      df.loc[i,'Label'] = 0
      changed_pos+=1
  else:
    if changed_neg < neg:
      df.loc[i,'Label'] = 1
      changed_neg+=1

print(df["Label"].value_counts())

import matplotlib.pyplot as plt
import matplotlib.colors

plt.scatter(df['x'][df['Label'] == 0], df['y'][df['Label'] == 0], color='red', label='Class 0')
plt.scatter(df['x'][df['Label'] == 1], df['y'][df['Label'] == 1], color='blue', label='Class 1')
plt.show()

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# df['Label'].replace('+1', 1, inplace=True)
# df['Label'].replace('-1', 0, inplace=True)
X = df[['x','y']].values
y = df['Label'].values
df

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size = 0.25) #Separate Test Set
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2) #Validation Set While Training

#Building a Simple Neural Network

model = Sequential()
model.add(Dense(16, activation = "tanh", input_shape = (2,)))
model.add(Dense(4, activation = "tanh"))
model.add(Dense(3, activation = "tanh"))
model.add(Dense(1, activation = "sigmoid"))
model.compile(optimizer = "adam", loss = "binary_crossentropy", metrics = ['accuracy'])

early_stopping = tf.keras.callbacks.EarlyStopping(monitor = "val_loss", patience = 5, restore_best_weights = True)

model.fit(X_train, y_train, epochs = 100, batch_size = 25, validation_data = (X_val, y_val), callbacks = [early_stopping], verbose = 0)

loss, accuracy = model.evaluate(X_test, y_test)
print(loss, accuracy)

#Performance Criteria - Accuracy, Balanced Accuracy, Area under ROC curve
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_curve, auc

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred.round())
balanced_accuracy = balanced_accuracy_score(y_test, y_pred.round())

fpr, tpr, thresholds = roc_curve(y_test, y_pred)
roc_auc = auc(fpr,tpr)

print("Accuracy: " ,accuracy, ", Balanced Accuracy: ", balanced_accuracy, "Area Under ROC Curve: ", roc_auc)

plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.show()

#Model Performace - Cross Validation
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import make_scorer, roc_auc_score
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.pipeline import Pipeline

# X = df[['x','y']].values
# y = df['Label'].values
roc_auc_scorer = make_scorer(roc_auc_score, greater_is_better = True)

def create_model():
    model = Sequential()
    model.add(Dense(16, activation='tanh', input_shape=(X_scaled.shape[1],)))
    model.add(Dense(4, activation='tanh'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

keras_clf = KerasClassifier(build_fn = create_model, epochs = 10, batch_size = 25)

cross_val_accuracy = cross_val_score(keras_clf, X_scaled,y, cv = 5, scoring = "accuracy")
cross_val_roc_auc = cross_val_score(keras_clf, X_scaled,y, cv = 5, scoring = roc_auc_scorer)

print("CV Accuracy: ", cross_val_accuracy, ", CV ROC AUC: ", cross_val_roc_auc)

#Performance of Performance Evaluation
# Generating large dataset
def create_val_data(a,b):
  df = pd.DataFrame()
  df['x'] = a
  df['y'] = b
  part_a = [[(-4,0),(-1,3)],[(-2,-4),(1,-1)],[(2,-2),(5,1)]]
  part_b = [[(-4,2),(-3,3)],[(-1,-3),(0,-2)],[(2,-1),(2,1)]]
  # point_combinations = [[(-4,0),(-1,3)],[(-2,-4),(1,-1)],[(2,-2),(5,1)],[(-4,2),(-3,3)],[(-1,-3),(0,-2)],[(2,-1),(2,1)]]
  num = 1
  for point in part_b:
    bl = point[0]
    tr = point[1]
    label = []
    # print(num)
    for i in range(len(a)):
      if point_in_square(bl,tr,[a[i],b[i]]) == True:
        label.append(True)
      else:
        label.append(False)
    col_name = "case_"+str(num)
    # print(col_name)
    df[col_name] = label
    num = num + 1

  label = []
  for i in range(df.shape[0]):
    temp = []
    for j in range(2,df.shape[1]):
      temp.append(df.iloc[i,j])
    if True in temp:
      label.append(1)
    else:
      label.append(0)

  df["Label"] = label
  temp_df = df
  df = temp_df[['x','y','Label']]
  df
  print(df['Label'].value_counts())

  #Find Class Distribution and Change the Class Labels to introduce noise
  # class_dist = df['Label'].value_counts()
  # neg = round(class_dist.max()*0.03)
  # pos = round(class_dist.min()*0.01)
  # print(neg, pos)

  # changed_pos, changed_neg = 0, 0
  # for i in range(df.shape[0]):
  #   if df['Label'][i] == 1:
  #     if changed_pos < pos:
  #       df.loc[i,'Label'] = 0
  #       changed_pos+=1
  #   else:
  #     if changed_neg < neg:
  #       df.loc[i,'Label'] = 1
  #       changed_neg+=1

  # print(df["Label"].value_counts())
  return df



a = np.random.uniform(low = -6, high = 6, size = 6000)
b = np.random.uniform(low = -4, high = 4, size = 6000)
val_df = create_val_data(a,b)

X_val_scaled = scaler.fit_transform(val_df[['x','y']].values)
y_val = val_df['Label'].values

y_val_pred = model.predict(X_val_scaled)
accuracy_val = accuracy_score(y_val, y_val_pred.round())
balanced_accuracy_val = balanced_accuracy_score(y_val, y_val_pred.round())

fpr_val, tpr_val, thresholds_val = roc_curve(y_val, y_val_pred)
roc_auc_val = auc(fpr_val,tpr_val)

print("Accuracy: " ,accuracy_val, ", Balanced Accuracy: ", balanced_accuracy_val, "Area Under ROC Curve: ", roc_auc_val)

import matplotlib.pyplot as plt
import matplotlib.colors

val_df['Predicted'] = y_val_pred.round()
val_df['Predicted'] = val_df['Predicted'].astype('int')

plt.scatter(val_df['x'][val_df['Predicted'] == 0], val_df['y'][val_df['Predicted'] == 0], color='red', label='Class 0')
plt.scatter(val_df['x'][val_df['Predicted'] == 1], val_df['y'][val_df['Predicted'] == 1], color='blue', label='Class 1')
plt.show()

val_df['Predicted'].value_counts()

########

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import accuracy_score, mean_squared_error, balanced_accuracy_score, roc_curve, confusion_matrix, auc
from tqdm import tqdm_notebook
from sklearn.neural_network import MLPClassifier

from sklearn.preprocessing import OneHotEncoder
from sklearn.datasets import make_blobs

X = df[["x","y"]]
y = df["Label"]
labels = ["-1","+1"]
X_train, X_val, Y_train, Y_val = train_test_split(X, y, test_size = 0.25)
print(X_train.shape, X_val.shape)

clf = MLPClassifier(activation= "tanh", hidden_layer_sizes=(12,3), max_iter=1000, early_stopping=True, random_state=42)

clf.fit(X_train, Y_train)

pred = clf.predict(X_val)

accuracy_score(pred,Y_val)

balanced_accuracy_score(pred,Y_val)

cf_matrix = confusion_matrix(Y_val,pred)
cf_matrix

y_true_binary = [1 if label == '+1' else 0 for label in Y_val]
fpr, tpr, thresholds = roc_curve(y_true_binary, clf.predict_proba(X_val)[:, 1], pos_label=1)
# fpr, tpr, thresholds = roc_curve(y_true_binary, clf.predict_proba(X_val)[:, 1], pos_label="+1")

roc_auc = auc(tpr, fpr)

plt.figure(figsize=(8, 6))
plt.plot(tpr, fpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()

import tensorflow as tf
print(tf.__version__)





