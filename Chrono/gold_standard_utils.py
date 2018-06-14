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



## Gold Standard Processing
## The functions in this file provide all the parsing for processing the gold standard files for ML methods.


import xmltodict
import csv
import os
import sys


## Iterates through all the gold standard XML files to parse out specified entities to save them to a tab delimited text file for ML method reference.  This function only need to be run once to generate all the files.
# @author Amy Olex
# @param path The path to the main folder where all the gold standard files are stored. Assumption is one folder per gold standard with only one xml file present in each folder.
def parseGoldEntities(path):
    # walk through all the folders to collect the xml file names
    print
    dirs = []
    files = []
    for root, dirs, files in os.walk(path, topdown=True):
        for subdir in dirs:
            for file in os.listdir(root+subdir):
                fname, ext = os.path.splitext(file)
                if ext == '.xml':
                    ## parse out the Calendar-Interval and Period entities for each file
                    extractPeriodCalInterval(root+subdir, file)
                    ## can add additional gold standard parsing here...


## Parses out the "Period" and "Calendar-Interval" entities to save them to a tab delimited text file for ML method reference.  This function only need to be run once to generate all the files.
# @author Amy Olex
# @param path The path to the gold standard file to be parsed.  
def extractPeriodCalInterval(path, file):   
    with open(path+"/"+file) as fd:
        doc = xmltodict.parse(fd.read())
	
    entities = doc['data']['annotations']['entity']

    my_golds = []
    for entity in entities:
        etype = entity['type']
        if etype in ['Calendar-Interval', 'Period']:
            start,end = entity['span'].split(",")
            value = entity['properties']['Type']
            my_golds.append({'type': etype, 'start': start, 'end':end, 'value': value})
    if len(my_golds) > 0:	
        keys = my_golds[0].keys()
        with open((path+'/period-interval.gold.csv'), 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(my_golds)
    else:
        open((path+'/period-interval.gold.csv'), 'w')

############

#path='/Users/alolex/Desktop/VCU_PhD_Work/Chrono/data/SemEval-OfficialTrain/'
path='/home/alolex/THYME_Data/THYMEColonFinal_Train/gold/'
#print(path)
parseGoldEntities(path)
