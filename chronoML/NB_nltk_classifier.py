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



### NB_nltk_classifier
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
    