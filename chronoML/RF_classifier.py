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

### SVM_classifier
### This program takes in 2 text files and trains the SciKitLearn SVM Classifier.
### 

from sklearn.ensemble import RandomForestClassifier
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
    
    classifier = RandomForestClassifier(n_estimators=100, n_jobs=-1)
    classifier.fit(X, y)
    
    dict_keys = data_list[0].keys()

    dic = OrderedDict(zip(dict_keys, np.repeat('0',len(dict_keys))))
    
    return(classifier, dic)
    