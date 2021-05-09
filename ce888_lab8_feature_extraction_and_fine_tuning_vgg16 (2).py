# -*- coding: utf-8 -*-
"""CE888_LAB8_FEATURE EXTRACTION AND FINE TUNING VGG16.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19MJh2WbjTczJGr7U4JEhBSgA1hwHgKJE

## Feature Extraction and Fine Tuning on Image Dataset with VGG16
"""

#import libraries 
import pandas as pd
import numpy as np
import os
import cv2
import glob
import seaborn as sns
import plotly.figure_factory as ff
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras import layers
from keras.layers import BatchNormalization
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, Input
from keras.layers import Dropout
from keras import models
from tensorflow.keras import Model
from keras import optimizers
from tensorflow.keras.applications import VGG16
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, classification_report
from sklearn.metrics import confusion_matrix

# # Load the Drive helper and mount
# from google.colab import drive
# drive.mount('/content/drive', force_remount=True)

# #unzip test file 
# from zipfile import ZipFile
# file_name = '/content/data'
# with ZipFile(file_name, 'r') as zip:
#   zip.extractall()
#   print('done')

#use glob to import images, creating arrays of images and corresponding labels 

import glob
Humans = glob.glob('/content/data/Humans/*.*')
cats = glob.glob('/content/data/cats/*.*')
dogs = glob.glob('/content/data/dogs/*.*')
horses = glob.glob('/content/data/horses/*.*')

data = []
labels = []


for i in Humans:   
    image=tf.keras.preprocessing.image.load_img(i, color_mode='rgb', 
    target_size= (224,224))
    image=np.array(image)
    data.append(image)
    labels.append(0)
for i in cats:   
    image=tf.keras.preprocessing.image.load_img(i, color_mode='rgb', 
    target_size= (224,224))
    image=np.array(image)
    data.append(image)
    labels.append(1)
for i in dogs:   
    image=tf.keras.preprocessing.image.load_img(i, color_mode='rgb', 
    target_size= (224,224))
    image=np.array(image)
    data.append(image)
    labels.append(2)
for i in horses:   
    image=tf.keras.preprocessing.image.load_img(i, color_mode='rgb', 
    target_size= (224,224))
    image=np.array(image)
    data.append(image)
    labels.append(3)

data = np.array(data)
labels = np.array(labels)

from sklearn.model_selection import train_test_split
X_train, X_test, ytrain, ytest = train_test_split(data, labels, test_size=0.2,
                                                random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train, ytrain, test_size=0.2,
                                                  random_state=42)

#print shape of arrays 
print(X_train.shape)
print(X_val.shape)
print(X_test.shape)
print(y_train.shape)
print(y_val.shape)
print(ytest.shape)

#display random iamges 
ims = X_train[np.random.choice(X_train.shape[0], 6, replace=False)]
fig, ax = plt.subplots(len(ims), figsize=(25, 25))
for i in range(6):
  ax[i].imshow(ims[i])

"""## VGG Feature Extraction """

## import VGG 16


from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Dense, Input, Flatten
from tensorflow.keras import Model
IMG_SIZE = 224
LR = 1e-4
img_input = Input(shape=(IMG_SIZE, IMG_SIZE, 3))

#set model 
model = VGG16(
    include_top=True,
    weights="imagenet",
    input_tensor=img_input,
    input_shape=None,
    pooling=None,
    classes=1000,
    classifier_activation="softmax",
)
model.summary()

#set last dense ouput layer 
last_layer = model.get_layer('fc2').output
out = Dense(4, activation='softmax', name='output')(last_layer)  
model = Model(img_input, out)

for layer in model.layers[:-1]:
	layer.trainable = False

model.summary()

#compile model 
model.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['acc'])

from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
my_callbacks = [
    EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
    ModelCheckpoint(filepath='/content/data', save_best_only=True)
]

#train model and save history 
history = model.fit(X_train, y_train,
                               batch_size=32,
                               epochs=10, 
                               validation_data=(X_val, y_val),
                               callbacks=my_callbacks)

#visualise performance 

acc = history.history['acc']
val_acc = history.history['val_acc']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(1, len(acc) + 1)

plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()

plt.figure()

plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()

# from sklearn.metrics import accuracy_score

# ## Test Accuracy
# predictions = model.predict(X_test)
# x = np.round(predictions)
# preds = np.where(x==1)[1]
# test_acc = accuracy_score(ytest, preds)

# from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

# precision, recall, f1score, _ = precision_recall_fscore_support(ytest, preds)

# # auc = roc_auc_score(ytest, preds)

# print("Train Accuracy:\t", acc[-1])
# print("Val Accuracy:\t", val_acc[-1])
# print("Test Accuracy:\t", test_acc)
# print("Precision:\t", precision)
# print("Recall:\t\t", recall)
# print("F1 Score:\t", f1score)
# # print("AUC:\t\t", auc)

val_loss, val_accuracy = model.evaluate(X_test, ytest)

"""##VGG16 For Fine_tuning """

#set model 
model = VGG16(
    include_top=True,
    weights="imagenet",
    input_tensor=img_input,
    input_shape=None,
    pooling=None,
    classes=1000,
    classifier_activation="softmax",
)


#set last layers, freeze remaining 
last_layer = model.get_layer('block5_pool').output
x= Flatten(name='flatten')(last_layer)
x = Dense(128, activation='relu', name='fc1')(x)
x = Dense(64, activation='relu', name='fc2')(x)
out = Dense(4, activation='softmax', name='output')(x) 
model = Model(img_input, out)

for layer in model.layers[:-3]:
	layer.trainable = False

#compile model 
model.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['acc'])

#set call backs and early stopping 
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
my_callbacks = [
    EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
    ModelCheckpoint(filepath='/content/data', save_best_only=True)
]

#train model and save history 
history = model.fit(X_train, y_train,
                               batch_size=32,
                               epochs=10, 
                               validation_data=(X_val, y_val),
                               callbacks=my_callbacks)

#visualise performance 
import matplotlib.pyplot as plt

acc = history.history['acc']
val_acc = history.history['val_acc']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(1, len(acc) + 1)

plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()

plt.figure()

plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()

## performance metrics 
predictions = model.predict(X_test)
x = np.round(predictions)
preds = np.where(x==1)[1]
test_acc = accuracy_score(ytest, preds)

from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

precision, recall, f1score, _ = precision_recall_fscore_support(ytest, preds)

# auc = roc_auc_score(ytest, preds)

print("Train Accuracy:\t", acc[-1])
print("Val Accuracy:\t", val_acc[-1])
print("Test Accuracy:\t", test_acc)
print("Precision:\t", precision)
print("Recall:\t\t", recall)
print("F1 Score:\t", f1score)
# print("AUC:\t\t", auc)

"""##Feature extraction on VGG19"""

model = tf.keras.applications.VGG19(
    include_top=True,
    weights="imagenet",
    input_tensor=img_input,
    input_shape=None,
    pooling=None,
    classes=1000,
    classifier_activation="softmax",
)

# model.summary()
#set last layers, freeze remaining 
last_layer = model.get_layer('predictions').output
out = Dense(4, activation='softmax', name='output')(last_layer) 
model = Model(img_input, out)

for layer in model.layers[:-1]:
	layer.trainable = False

# for i, layer in enumerate(model.layers):
#   print(i, layer.name, "-", layer.trainable)

#compile model 
model.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['acc'])

#set call backs and early stopping 
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
my_callbacks = [
    EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
    ModelCheckpoint(filepath='/content/data', save_best_only=True)
]

#train model and save history 
history = model.fit(X_train, y_train,
                               batch_size=32,
                               epochs=10, 
                               validation_data=(X_val, y_val),
                               callbacks=my_callbacks)

#visualise performance 
import matplotlib.pyplot as plt

acc = history.history['acc']
val_acc = history.history['val_acc']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(1, len(acc) + 1)

plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()

plt.figure()

plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()

val_loss, val_accuracy = model.evaluate(X_test, ytest)

"""## Fine Tuning on VGG19"""

#set model 
model = tf.keras.applications.VGG19(
    include_top=True,
    weights="imagenet",
    input_tensor=img_input,
    input_shape=None,
    pooling=None,
    classes=1000,
    classifier_activation="softmax",
)


#set last layers, freeze remaining 
last_layer = model.get_layer('block5_pool').output
x= Flatten(name='flatten')(last_layer)
x = Dense(128, activation='relu', name='fc1')(x)
x = Dense(64, activation='relu', name='fc2')(x)
out = Dense(4, activation='softmax', name='output')(x) 
model = Model(img_input, out)

for layer in model.layers[:-3]:
	layer.trainable = False

#compile model 
model.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['acc'])

#set call backs and early stopping 
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
my_callbacks = [
    EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
    ModelCheckpoint(filepath='/content/data', save_best_only=True)
]

#train model and save history 
history = model.fit(X_train, y_train,
                               batch_size=32,
                               epochs=10, 
                               validation_data=(X_val, y_val),
                               callbacks=my_callbacks)

#visualise performance 
import matplotlib.pyplot as plt

acc = history.history['acc']
val_acc = history.history['val_acc']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(1, len(acc) + 1)

plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()

plt.figure()

plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()

val_loss, val_accuracy = model.evaluate(X_test, ytest)

"""#ResNet50 Feature Extraction """

#set model 
model = tf.keras.applications.ResNet50(
    include_top=True,
    weights="imagenet",
    input_tensor=img_input,
    input_shape=None,
    pooling=None,
    classes=1000,
    classifier_activation="softmax",
)

# model.summary()
#set last layers, freeze remaining 
last_layer = model.get_layer('predictions').output
out = Dense(4, activation='softmax', name='output')(last_layer) 
model = Model(img_input, out)

for layer in model.layers[:-3]:
	layer.trainable = False

#compile model 
model.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['acc'])

#set call backs and early stopping 
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
my_callbacks = [
    EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
    ModelCheckpoint(filepath='/content/data', save_best_only=True)
]

#train model and save history 
history = model.fit(X_train, y_train,
                               batch_size=32,
                               epochs=10, 
                               validation_data=(X_val, y_val),
                               callbacks=my_callbacks)

val_loss, val_accuracy = model.evaluate(X_test, ytest)

"""#Resnet 50 Fine_tuning """

#set model 
model = tf.keras.applications.ResNet50(
    include_top=True,
    weights="imagenet",
    input_tensor=img_input,
    input_shape=None,
    pooling=None,
    classes=1000,
    classifier_activation="softmax",
)

# model.summary()
#set last layers, freeze remaining 
last_layer = model.get_layer('avg_pool').output
x= Flatten(name='flatten')(last_layer)
x = Dense(128, activation='relu', name='new dense layer')(x)
x = Dense(64, activation='relu', name='new dense layer ')(x)
out = Dense(4, activation='softmax', name='output')(x) 
model = Model(img_input, out)

for layer in model.layers[:-3]:
	layer.trainable = False

#compile model 
model.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['acc'])

#set call backs and early stopping 
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
my_callbacks = [
    EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
    ModelCheckpoint(filepath='/content/data', save_best_only=True)
]

#train model and save history 
history = model.fit(X_train, y_train,
                               batch_size=32,
                               epochs=10, 
                               validation_data=(X_val, y_val),
                               callbacks=my_callbacks)

val_loss, val_accuracy = model.evaluate(X_test, ytest)