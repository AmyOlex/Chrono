import numpy as np
import csv
import nltk
import nltk.classify.util
from nltk.classify import DecisionTreeClassifier
from collections import OrderedDict

def build_dt_model(data_file, class_file):
    #import data and class files
    data = []
    classes = []
    
    with open(data_file) as dFile:
        reader = csv.DictReader(dFile)
        data = [row for row in reader]
    
    with open(class_file) as cFile:
        for line in cFile.readlines():
            classes.append(int(line.strip()))
    
    #create classifier input
    DT_Input = []
    
    if(len(data) == len(classes)):
        for i in range(0,len(data)):
            DT_Input.append((data[i],classes[i]))
            
    #Train Classifier
    classifier = DecisionTreeClassifier.train(DT_Input)
    
    #Create orderedDict
    dict_keys = data[0].keys()
    
    ordDict = OrderedDict(zip(dict_keys, np.repeat(0,len(dict_keys))))
    
    return(classifier,ordDict)
