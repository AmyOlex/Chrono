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


import csv
from collections.__init__ import OrderedDict

import numpy as np
from Chrono.ChronoUtils.parse_text import getNumberFromText
from nltk import SnowballStemmer


def extract_prediction_features(reftok_list, reftok_idx, feature_dict) :

    reftok = reftok_list[reftok_idx]
    window = 5

    ### Extract the stem feature
    my_str = reftok.getText()
    stemmer = SnowballStemmer("english")
    my_stem = stemmer.stem(reftok.getText().lower())
    if(my_stem in feature_dict.keys()):
        feature_dict[my_stem] = '1'


    ### identify the numeric feature
    before = max(reftok_idx-1,0)
    after = min(reftok_idx+1,len(reftok_list)-1)

    if(before != reftok_idx and isinstance(getNumberFromText(reftok_list[before].getText()), (int))):
        feature_dict['feat_numeric'] = '1'
    elif(after != reftok_idx and isinstance(getNumberFromText(reftok_list[after].getText()), (int))):
        feature_dict['feat_numeric'] = '1'
    else:
        feature_dict['feat_numeric'] = '0'


    ## identify bow feature
    start = max(reftok_idx-window,0)
    end = min(reftok_idx+(window+1),len(reftok_list)-1)

    for r in range(start, end):
        if r != reftok_idx:
            num_check = getNumberFromText(reftok_list[r].getText())
            if(isinstance(num_check, (int))):
                if(num_check in feature_dict.keys()):
                    feature_dict[num_check] = '1'
            else:
                txt = reftok_list[r].getText()
                if(txt in feature_dict.keys()):
                    feature_dict[txt] = '1'

    ## identify temp_self feature
    if reftok.isTemporal():
        feature_dict['feat_temp_self'] = '1'

    ## identify temp_context within 3 words to either side of the target.
    start = max(reftok_idx-window,0)
    end = min(reftok_idx+(window+1),len(reftok_list)-1)
    for r in range(start, end):
        if r != reftok_idx:
            if reftok_list[r].isTemporal():
                feature_dict['feat_temp_context'] = '1'
                break

    return(feature_dict)


def get_features(data_file):
    ## Import csv files
    with open(data_file) as file:
        reader = csv.DictReader(file)
        data_list = [row for row in reader]

    ## Create the empty orderedDict to pass back for use in the other methods.
    dict_keys = data_list[0].keys()

    dic = OrderedDict(zip(dict_keys, list(np.repeat('0',len(dict_keys)))))

    return(dic)