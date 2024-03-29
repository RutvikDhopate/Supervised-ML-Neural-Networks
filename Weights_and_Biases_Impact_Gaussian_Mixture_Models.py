# -*- coding: utf-8 -*-
"""SML 4.3

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FdMGwUD_w8uOXJ7WL4Rx1hV9Lccsd52T
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Assume some parameters for Multivariate Normal Distribution
weights_0 = [0.5, 0.5]
means_0 = [[-1,-1], [1.5,1.5]]
covs_0 = [np.array([[2,0.5], [0.5,2]]), np.array([[4,1],[1,4]])]

weights_1 = [0.4, 0.6]
means_1 = [[3,3], [6,6]]
covs_1 = [np.array([[9,1],[1,6]]), np.array([[12,1],[1,4]])]

#Generate Training Data based on Class Conditionals
def create_training_data(samples, weights, means, covs, class_labels):
  samples_per_class = [samples*wt for wt in weights]
  sample = []
  for i in range(len(weights)):
    temp_sample = np.random.multivariate_normal(means[i], covs[i], int(samples_per_class[i]))
    sample.append(temp_sample)

  data = np.concatenate(sample, axis = 0)
  if class_labels == 1:
    labels = np.ones(samples)
  elif class_labels == 0:
    labels = np.zeros(samples)

  return data, labels

data_size = 2000
data_0, labels_0 = create_training_data(data_size, weights_0, means_0, covs_0, 0)
data_1, labels_1 = create_training_data(data_size, weights_1, means_1, covs_1, 1)

df_0 = pd.DataFrame(data_0, columns = ['x', 'y'])
df_1 = pd.DataFrame(data_1, columns = ['x', 'y'])

df_0['Label'] = labels_0
df_1['Label'] = labels_1

df_0 = df_0.sample(frac = 1)
df_1 = df_1.sample(frac= 1)

prob_0 = 0.51
prob_1 = 1-prob_0
# df = pd.concat([df_0, df_1], ignore_index = True)
df = pd.concat([df_0[:int(prob_0*data_size)], df_1[int(prob_1*data_size):]], ignore_index=True)

df = df.sample(frac = 1)
df.reset_index(inplace = True, drop = True)
df.Label = df.Label.astype('int')

plt.scatter(df['x'], df['y'], c=df['Label'])
plt.show()

df.shape

#Train Logistic Regression on Entire Data using Cross Validation
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score

X = df[['x','y']].values
y = df['Label'].values

model_lr = LogisticRegression()
cv_lr = cross_val_score(model_lr, X, y, cv = 10, scoring = "roc_auc")
model_lr.fit(X,y)
print(cv_lr)

#Naive Bayes using Cross Valition
model_nb = GaussianNB()
cv_nb = cross_val_score(model_nb, X, y, cv = 10, scoring = "roc_auc")
model_nb.fit(X,y)
print(cv_lr)

#2 layer non linear neural network using Cross Validation
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, roc_auc_score
from keras.wrappers.scikit_learn import KerasClassifier

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

roc_auc_scorer = make_scorer(roc_auc_score, greater_is_better = True)
def create_model():
  model_nn = Sequential()
  model_nn.add(Dense(32, activation = "sigmoid", input_shape = (2,)))
  model_nn.add(Dense(1, activation = "sigmoid"))

  model_nn.compile(optimizer = "adam", loss = "binary_crossentropy", metrics = ['accuracy'])
  return model_nn


keras_clf = KerasClassifier(build_fn = create_model, epochs = 10, batch_size = 25)
# model_nn = create_model()
cv_nn = cross_val_score(keras_clf, X_scaled ,y, cv = 10, scoring = roc_auc_scorer)
model_nn = create_model()
model_nn.fit(X_scaled, y, epochs = 25, batch_size = 25, verbose = 0)
print(cv_nn)

# Part a - Unbiased Test Data
# Generating test data based on same multivariate parameters like training and unbiased test data.
from sklearn.metrics import accuracy_score, roc_curve, auc

data_size = 2000
data_0, labels_0 = create_training_data(data_size, weights_0, means_0, covs_0, 0)
data_1, labels_1 = create_training_data(data_size, weights_1, means_1, covs_1, 1)

df_0 = pd.DataFrame(data_0, columns = ['x', 'y'])
df_1 = pd.DataFrame(data_1, columns = ['x', 'y'])

df_0['Label'] = labels_0
df_1['Label'] = labels_1

df_0 = df_0.sample(frac = 1)
df_1 = df_1.sample(frac= 1)

prob_0 = 0.50
prob_1 = 1-prob_0

# df = pd.concat([df_0, df_1], ignore_index = True)
test_df = pd.DataFrame()
test_df = pd.concat([df_0[:int(prob_0*data_size)], df_1[int(prob_1*data_size):]], ignore_index=True)
test_df = test_df.sample(frac = 1)
test_df.reset_index(inplace = True, drop = True)
test_df.Label = test_df.Label.astype('int')

test_df

test_X = scaler.fit_transform(test_df[['x','y']].values)
test_y = test_df['Label'].values

#Predicting from the above three fit models and getting accuracy
#Logistic Regression
y_pred_lr = model_lr.predict(test_X)
acc_lr = accuracy_score(test_y, y_pred_lr.round())
fpr_test, tpr_test, thresholds_test = roc_curve(test_y, y_pred_lr)
roc_auc_lr = auc(fpr_test,tpr_test)
print("Logistic Regression Accuracy: " ,acc_lr, "LR Area Under ROC Curve: ", roc_auc_lr)

#Naive Bayes
y_pred_nb = model_nb.predict(test_X)
acc_nb = accuracy_score(test_y, y_pred_nb.round())
fpr_test, tpr_test, thresholds_test = roc_curve(test_y, y_pred_nb)
roc_auc_nb = auc(fpr_test,tpr_test)

print("Naive Bayes Accuracy: " ,acc_nb, "NB Area Under ROC Curve: ", roc_auc_nb)

#Neural Network
y_pred_nn = model_nn.predict(test_X)
acc_nn = accuracy_score(test_y, y_pred_nn.round())
fpr_test, tpr_test, thresholds_val = roc_curve(test_y, y_pred_nn)
roc_auc_nn = auc(fpr_test,tpr_test)

print("Neural Network Accuracy: " ,acc_nn, "NN Area Under ROC Curve: ", roc_auc_nn)

# Part b - Biased Test Data according to Label shift
# Generating test data based on same multivariate parameters like training and biased test data but changing the prob_0 to 0.75.
from sklearn.metrics import accuracy_score, roc_curve, auc

data_size = 2000
data_0, labels_0 = create_training_data(data_size, weights_0, means_0, covs_0, 0)
data_1, labels_1 = create_training_data(data_size, weights_1, means_1, covs_1, 1)

df_0 = pd.DataFrame(data_0, columns = ['x', 'y'])
df_1 = pd.DataFrame(data_1, columns = ['x', 'y'])

df_0['Label'] = labels_0
df_1['Label'] = labels_1

df_0 = df_0.sample(frac = 1)
df_1 = df_1.sample(frac= 1)

prob_0 = 0.75
prob_1 = 1-prob_0

# df = pd.concat([df_0, df_1], ignore_index = True)
test_df = pd.DataFrame()
test_df = pd.concat([df_0[:int(prob_0*data_size)], df_1[int(prob_1*data_size):]], ignore_index=True)
test_df = test_df.sample(frac = 1)
test_df.reset_index(inplace = True, drop = True)
test_df.Label = test_df.Label.astype('int')

test_df

test_X = scaler.fit_transform(test_df[['x','y']].values)
test_y = test_df['Label'].values

count = 0
for i in range(test_df.shape[0]):
  if count < 1000:
    if test_df['Label'][i] == 1:
      test_df.loc[i,'Label'] = 0
    else:
      test_df.loc[i,'Label'] = 1
      count+=1

#Predicting from the above three fit models and getting accuracy
#Logistic Regression
y_pred_lr = model_lr.predict(test_X)
acc_lr = accuracy_score(test_y, y_pred_lr.round())
fpr_test, tpr_test, thresholds_test = roc_curve(test_y, y_pred_lr)
roc_auc_lr = auc(fpr_test,tpr_test)
print("Logistic Regression Accuracy: " ,acc_lr, "LR Area Under ROC Curve: ", roc_auc_lr)

#Naive Bayes
y_pred_nb = model_nb.predict(test_X)
acc_nb = accuracy_score(test_y, y_pred_nb.round())
fpr_test, tpr_test, thresholds_test = roc_curve(test_y, y_pred_nb)
roc_auc_nb = auc(fpr_test,tpr_test)

print("Naive Bayes Accuracy: " ,acc_nb, "NB Area Under ROC Curve: ", roc_auc_nb)

#Neural Network
y_pred_nn = model_nn.predict(test_X)
acc_nn = accuracy_score(test_y, y_pred_nn.round())
fpr_test, tpr_test, thresholds_val = roc_curve(test_y, y_pred_nn)
roc_auc_nn = auc(fpr_test,tpr_test)

print("Neural Network Accuracy: " ,acc_nn, "NN Area Under ROC Curve: ", roc_auc_nn)

plt.scatter(test_df['x'], test_df['y'], c=test_df['Label'], cmap='viridis')

#Part c - Covariate shift Bias Model
#Unchanged posteriors but assuming Single variable Gaussian priors.

data1 = np.random.normal(loc = -2, scale = 1, size = 2000)
data2 = np.random.normal(loc = 2, scale = 4, size = 2000)

from scipy.stats import multivariate_normal
c1_mn_dist1 = multivariate_normal(mean = [3,3], cov = [[9,1],[1,6]])
c1_mn_dist2 = multivariate_normal(mean = [6,6], cov = [[4,1],[1,4]])

c0_mn_dist1 = multivariate_normal(mean = [-1,-1], cov = [[2,0.5],[0.5,2]])
c0_mn_dist2 = multivariate_normal(mean = [1.5,1.5], cov = [[9,1],[1,4]])

test_label = []
for i in range(len(data1)):
  posterior1 = (c1_mn_dist1.pdf(data1[i])+c1_mn_dist2.pdf(data1[i]))*prob_1/((c1_mn_dist1.pdf(data1[i])+c1_mn_dist2.pdf(data1[i]))*prob_1 + (c0_mn_dist1.pdf(data1[i])+c0_mn_dist2.pdf(data1[i]))*prob_0)
  posterior2 = (c1_mn_dist1.pdf(data2[i])+c1_mn_dist2.pdf(data2[i]))*prob_1/((c1_mn_dist2.pdf(data2[i])+c1_mn_dist2.pdf(data2[i]))*prob_1 + (c0_mn_dist1.pdf(data2[i])+c0_mn_dist2.pdf(data2[i]))*prob_0)
  if posterior1 > posterior2:
    test_label.append(1)
  else:
    test_label.append(0)


test_df = pd.DataFrame()
test_df['x'] = data1
test_df['y'] = data2
test_df['Label'] = test_label

test_X = test_df[['x','y']].values
test_y = test_df['Label'].values

#Predicting from the above three fit models and getting accuracy
#Logistic Regression
y_pred_lr = model_lr.predict(test_X)
acc_lr = accuracy_score(test_y, y_pred_lr.round())
fpr_test, tpr_test, thresholds_test = roc_curve(test_y, y_pred_lr)
roc_auc_lr = auc(fpr_test,tpr_test)
print("Logistic Regression Accuracy: " ,acc_lr, "LR Area Under ROC Curve: ", roc_auc_lr)

#Naive Bayes
y_pred_nb = model_nb.predict(test_X)
acc_nb = accuracy_score(test_y, y_pred_nb.round())
fpr_test, tpr_test, thresholds_test = roc_curve(test_y, y_pred_nb)
roc_auc_nb = auc(fpr_test,tpr_test)

print("Naive Bayes Accuracy: " ,acc_nb, "NB Area Under ROC Curve: ", roc_auc_nb)

#Neural Network
y_pred_nn = model_nn.predict(test_X)
acc_nn = accuracy_score(test_y, y_pred_nn.round())
fpr_test, tpr_test, thresholds_val = roc_curve(test_y, y_pred_nn)
roc_auc_nn = auc(fpr_test,tpr_test)

print("Neural Network Accuracy: " ,acc_nn, "NN Area Under ROC Curve: ", roc_auc_nn)

plt.scatter(test_df['x'], test_df['y'], c=test_df['Label'], cmap='viridis')

#Part d - Test data is biased according
# Generating test data based on some random parameters of Multivariate Normal Distribution.
#Assume some parameters for Multivariate Normal Distribution
weights_0 = [0.31, 0.69]
means_0 = [[-3,4], [1.23,4.5]]
covs_0 = [np.array([[1,2], [2,9]]), np.array([[2,4],[4,3]])]

weights_1 = [0.12, 0.88]
means_1 = [[12,-3], [0,6]]
covs_1 = [np.array([[2,4],[4,5]]), np.array([[6,1],[1,9]])]

data_size = 2000
data_0, labels_0 = create_training_data(data_size, weights_0, means_0, covs_0, 0)
data_1, labels_1 = create_training_data(data_size, weights_1, means_1, covs_1, 1)

df_0 = pd.DataFrame(data_0, columns = ['x', 'y'])
df_1 = pd.DataFrame(data_1, columns = ['x', 'y'])

df_0['Label'] = labels_0
df_1['Label'] = labels_1

df_0 = df_0.sample(frac = 1)
df_1 = df_1.sample(frac= 1)

prob_0 = 0.51
prob_1 = 1-prob_0
# df = pd.concat([df_0, df_1], ignore_index = True)
test_df = pd.DataFrame()
test_df = pd.concat([df_0[:int(prob_0*data_size)], df_1[int(prob_1*data_size):]], ignore_index=True)

test_df = test_df.sample(frac = 1)
test_df.reset_index(inplace = True, drop = True)
test_df.Label = test_df.Label.astype('int')

test_df['Label'] = np.zeros(test_df.shape)
for i in range(df.shape[0]):
  test_df.loc[i,'Label'] = np.random.randint(0,2)

#Predicting from the above three fit models and getting accuracy
#Logistic Regression
y_pred_lr = model_lr.predict(test_X)
acc_lr = accuracy_score(test_y, y_pred_lr.round())
fpr_test, tpr_test, thresholds_test = roc_curve(test_y, y_pred_lr)
roc_auc_lr = auc(fpr_test,tpr_test)
print("Logistic Regression Accuracy: " ,acc_lr, "LR Area Under ROC Curve: ", roc_auc_lr)

#Naive Bayes
y_pred_nb = model_nb.predict(test_X)
acc_nb = accuracy_score(test_y, y_pred_nb.round())
fpr_test, tpr_test, thresholds_test = roc_curve(test_y, y_pred_nb)
roc_auc_nb = auc(fpr_test,tpr_test)

print("Naive Bayes Accuracy: " ,acc_nb, "NB Area Under ROC Curve: ", roc_auc_nb)

#Neural Network
y_pred_nn = model_nn.predict(test_X)
acc_nn = accuracy_score(test_y, y_pred_nn.round())
fpr_test, tpr_test, thresholds_val = roc_curve(test_y, y_pred_nn)
roc_auc_nn = auc(fpr_test,tpr_test)

print("Neural Network Accuracy: " ,acc_nn, "NN Area Under ROC Curve: ", roc_auc_nn)

plt.scatter(test_df['x'], test_df['y'], c=test_df['Label'])









