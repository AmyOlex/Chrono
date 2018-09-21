# Copyright (c) 2018
# Amy L. Olex, Virginia Commonwealth University
# alolex at vcu.edu
#
# Luke Maffey, Virginia Commonwealth University
# maffeyl at vcu.edu
#
# Nicholas Morton,  Virginia Commonwealth University
# nmorton at vcu.edu
#
# Bridget T. McInnes, Virginia Commonwealth University
# btmcinnes at vcu.edu
#
# This file is part of Chrono
#
# Chrono is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Chrono is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Chrono; if not, write to
#
# The Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330,
# Boston, MA  02111-1307, USA.

from keras import Sequential, preprocessing
from keras.layers import SimpleRNN, Dense
import numpy as np


## Builds and trains the neural network with the given training data
# @param A 3D array
# @return The neural network classifier, pass this to classify
def build_model(train_data, train_labels):
    print("Reading training data...")
    X = preprocessing.sequence.pad_sequences(train_data, value=False, padding='post', maxlen=13)
    Y = np.array(train_labels)
    # print(X.shape)

    print("Building RNN...")
    model = Sequential()
    model.add(SimpleRNN(1, activation="relu", input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    print("Training...")
    model.fit(X, Y, epochs=100, batch_size=10)
    print("Model: ")
    print(model.summary())
    return model


## Evaluate the given model on a test set
# @param model The model to be evaluated
# @param test_data A CSV with the test data
# @param train_labels A CSV with the test labels
# @return Prints and returns the accuracy of the model on the test data
# def evaluate(model, test_data, test_labels):
#     scores = model.evaluate(test_data, test_labels)
#     print("Test data accuracy: {}".format(scores[1] * 100))
#     return scores


## Classfy a single sample
# @param model The model to be used
# @param predcit_data A numpy array with the sample to be classified
# @return A 0 or 1 for which class was predicted
def classify(model, predict_data):
    longest=13
    # Keras wants a list of numpy arrays
    padding = longest-len(predict_data)
    X = np.pad(predict_data,[(0,padding),(0,0)],mode="constant")
    X = np.expand_dims(X, axis=0)
    print("Predicting on {}".format(X))
    prediction = model.predict(X, verbose=1)
    print("The prediction is: {}".format(np.round(prediction[0])))
    return np.round(prediction[0])