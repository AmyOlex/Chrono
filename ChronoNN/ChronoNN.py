## Deep neural network for classifying calendar-intervals and periods in tensorflow.  Takes a .csv file where the
# first line is the number of instances, number of features, and then a list of class labels.  All subsequent lines
# are the instance features with the last character as the class  Based on the tensorflow DNN tutorial found here:
# https://www.tensorflow.org/get_started/estimator
#---------------------------------------------------------------------------------------------------------
# Date: 9/19/17
#
# Programmer Name: Luke Maffey
#

## Superclass for all entities
#
# Entities are either an Interval, Period, Repeating-Interval, or Operator
# @param entityID Assigned ID number
# @param start_span The location of the first character
# @param end_span The location of the last character
# @param type The type of the entity
# @param parent_type The parent type of the entity

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

import numpy as np
import tensorflow as tf

# Data sets
TRAINING_DATA = "chrono_training_binary.csv"
LOGDIR = "/tmp/ChronoNN/"
TEST_DATA = "chrono_test_binary.csv"

def main():
    # If the training and test sets aren't stored locally, exit
    if not os.path.exists(TRAINING_DATA):
        print("File not found: {}".format(TRAINING_DATA))
        sys.exit()

    if not os.path.exists(TEST_DATA):
        print("File not found: {}".format(TEST_DATA))
        sys.exit()

    # Load datasets.
    training_set = tf.contrib.learn.datasets.base.load_csv_with_header(
        filename=TRAINING_DATA,
        target_dtype=np.int,
        features_dtype=np.int)
    test_set = tf.contrib.learn.datasets.base.load_csv_with_header(
        filename=TEST_DATA,
        target_dtype=np.int,
        features_dtype=np.int)

    # Specify that all features have real-value data
    feature_columns = [tf.feature_column.numeric_column("x", shape=[4])]

    # Build 3 layer DNN with 10, 20, 10 units respectively.
    classifier = tf.estimator.DNNClassifier(feature_columns=feature_columns,
                                            hidden_units=[10,20,10],
                                            n_classes=2,
                                            model_dir="/tmp/chrono_model")
    # Define the training inputs
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": np.array(training_set.data)},
        y=np.array(training_set.target),
        num_epochs=None,
        shuffle=True)

    # Train model.
    classifier.train(input_fn=train_input_fn, steps=2000)

    # Define the test inputs
    test_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": np.array(test_set.data)},
        y=np.array(test_set.target),
        num_epochs=1,
        shuffle=False)

    # Evaluate accuracy.
    accuracy_score = classifier.evaluate(input_fn=test_input_fn)["accuracy"]

    print("\nTest Accuracy: {0:f}\n".format(accuracy_score))

    # Classify two new samples.
    new_samples = np.array(
        [[0,1,1,1],
         [1,0,0,0]], dtype=np.int)
    predict_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": new_samples},
        num_epochs=1,
        shuffle=False)

    predictions = list(classifier.predict(input_fn=predict_input_fn))
    predicted_classes = [p["classes"] for p in predictions]

    print(
        "New Samples, Class Predictions:    {}\n"
            .format(predictions))

if __name__ == "__main__":
    main()