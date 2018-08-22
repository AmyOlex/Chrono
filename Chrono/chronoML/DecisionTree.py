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



### DT_nltk_classifier
### This program takes in 2 text files and trains the NLTK DT Classifier.
### 

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
    
    ordDict = OrderedDict(zip(dict_keys, np.repeat('0',len(dict_keys))))
    
    return(classifier,ordDict)
