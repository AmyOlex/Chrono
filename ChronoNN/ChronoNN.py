## Deep neural network for classifying calendar-intervals and periods in tensorflow.  Takes a .csv file where the
# first line is the number of instances, number of features, and then a list of class labels.  All subsequent lines
# are the instance features with the last character as the class  Based on the tensorflow DNN tutorial found here:
# https://www.tensorflow.org/get_started/estimator
#---------------------------------------------------------------------------------------------------------
# Date: 9/19/17
#
# Programmer Name: Luke Maffey
# *******CURRENTLY UNUSED DO NOT USE**************

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

import numpy as np
import tensorflow as tf

## Trains a classifier with the training data passed.  Once trained, you must delete the LOGDIR or specify a new one
# if you want to train it again or it will break when it sees there's already something in the folder
# @param TRAINING_DATA The .csv file to use for training
# @param LOGDIR Where to store the neural network's configuration
# @param layers An array of the hidden layers of the neural network
# @return Returns a classifier
def build_model(TRAINING_DATA = "chrono_training_binary.csv",LOGDIR="/tmp/ChronoNN/", layers=[5]):
    # If the training and test sets aren't stored locally, exit
    if not os.path.exists(TRAINING_DATA):
        print("File not found: {}".format(TRAINING_DATA))
        sys.exit()

    # Load datasets.
    training_set = tf.contrib.learn.datasets.base.load_csv_with_header(
        filename=TRAINING_DATA,
        target_dtype=np.int,
        features_dtype=np.int)

    num_features = np.array(training_set.data).shape[1]

    # Specify that all features have real-value data
    feature_columns = [tf.feature_column.numeric_column("x", shape=[num_features])]

    # Build DNN with "hidden_units" layers and nodes.
    classifier = tf.estimator.DNNClassifier(feature_columns=feature_columns,
                                            hidden_units=layers,
                                            n_classes=2,
                                            model_dir=LOGDIR)
    # Define the training inputs
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": np.array(training_set.data)},
        y=np.array(training_set.target),
        num_epochs=None,
        shuffle=True)

    # Train model.
    classifier.train(input_fn=train_input_fn, steps=2000)

    return classifier

## Prints the accuracy of your classifier on a test set
# @param classifier A tensorflow classifier
# @param TEST_DATA The filename where the data is found
def test_model(classifier, TEST_DATA = "chrono_test_binary.csv"):
    if not os.path.exists(TEST_DATA):
        print("File not found: {}".format(TEST_DATA))
        sys.exit()

    test_set = tf.contrib.learn.datasets.base.load_csv_with_header(
        filename=TEST_DATA,
        target_dtype=np.int,
        features_dtype=np.int)
    # Define the test inputs
    test_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": np.array(test_set.data)},
        y=np.array(test_set.target),
        num_epochs=1,
        shuffle=False)
    # Evaluate accuracy.
    accuracy_score = classifier.evaluate(input_fn=test_input_fn)["accuracy"]

    print("\nTest Accuracy: {0:f}\n".format(accuracy_score))


## Classifies the samples passed with the classifier passed
# @param classifier A tensorflow classifier
# @param samples A numpy array of features
# @return A numpy array of predicted classes
def classify(classifier, samples):
    predict_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": samples},
        num_epochs=1,
        shuffle=False)

    predictions = classifier.predict(input_fn=predict_input_fn)
    return predictions
