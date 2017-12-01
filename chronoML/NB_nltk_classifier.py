### NB_nltk_classifier
### Author: Amy Olex
### 11/25/17
### This program takes in 2 text files and trains the NLTK NB Classifier.
### 

from nltk.classify import NaiveBayesClassifier
import nltk.classify.util
import nltk
import csv
from collections import OrderedDict
import numpy as np


def build_model(data_file, class_file):
    ## Import csv files
    data_list = []
    with open(data_file) as file:
        reader = csv.DictReader(file)
        data_list = [row for row in reader]
    class_list = []
    with open(class_file) as f:
        for line in f.readlines():
            class_list.append(int(line.strip()))
    
    ## Create the input for the classifier
    NB_input = []
    if(len(data_list)==len(class_list)):
        for i in range(0,len(data_list)):
            NB_input.append((data_list[i],class_list[i]))
    
    ## Train the classifier and return it along with the ordered dictionary keys.
    classifier = NaiveBayesClassifier.train(NB_input)
    print('accuracy:', nltk.classify.util.accuracy(classifier, NB_input))
    ## Create the empty orderedDict to pass back for use in the other methods.
    dict_keys = data_list[0].keys()

    dic = OrderedDict(zip(dict_keys, np.repeat('0',len(dict_keys))))
    
    return(classifier, dic, NB_input)
    