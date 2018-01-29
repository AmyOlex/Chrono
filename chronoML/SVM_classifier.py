### SVM_classifier
### Author: Amy Olex
### 1/29/18
### This program takes in 2 text files and trains the SciKitLearn SVM Classifier.
### 

from sklearn import svm
import csv
from collections import OrderedDict
import numpy as np


def build_model(data_file, class_file):
    ## Import csv files
    data_list = []
    with open(data_file) as file:
        reader = csv.DictReader(file)
        data_list = [row for row in reader]
    y = []
    with open(class_file) as f:
        for line in f.readlines():
            y.append(int(line.strip()))
    
    X = []
    for row in data_list:
        X.append([int(i) for i in row.values()])
    
    classifier = svm.LinearSVC(max_iter=3, C=.05)
    classifier.fit(X, y)
    
    dict_keys = data_list[0].keys()

    dic = OrderedDict(zip(dict_keys, np.repeat('0',len(dict_keys))))
    
    return(classifier, dic)
    