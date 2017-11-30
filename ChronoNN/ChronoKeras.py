from keras.models import Sequential
from keras.layers import Dense, Dropout
# from gensim.models import word2vec
from gensim.models.keyedvectors import KeyedVectors

import numpy as np
import csv
import string
import math
import random

np.random.seed(123)

def build_model(train_data, train_labels):
    dataset = np.loadtxt(train_data, delimiter=",",skiprows=1)
    labels = np.loadtxt(train_labels, delimiter=",")
    size = len(dataset[0,:])
    print("Size: {}".format(size))
    X = dataset[:, 0:size]
    Y = labels[:]
    # Build keras NN
    model = Sequential()
    model.add(Dense(size, input_shape=(size, ), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(size, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(size*2, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(size, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    model.fit(X, Y, epochs=3, batch_size=10)
    return model

def keras_evaluate(model,test_data,test_labels):
    scores = model.evaluate(test_data, test_labels)
    print("Test data accuracy: {}".format(scores[1]*100))
    return scores


def keras_classify(model,predict_data):
    X = []
    X.append(list(predict_data))
    X.append(list(predict_data))
    # print("Predicting on {}".format(X))
    prediction = model.predict(X,verbose=1)
    print("The prediction is: {}".format(np.round(prediction[0])))
    return np.round(prediction[0])