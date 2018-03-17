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



## This file imports the gold standard data for training the ML methods.

###### Workflow ######
##
## 1) get location of files to parse (DONE)
## 2) get location of output directory/create output directories (DONE)
## 3) import the list of positive Periods and Calendar-Intervals
## 3) For each FILE:
##      a) parse with stanford parser to get whitespace tokens and associated spans
##      b) import this into a refToken object list
##      c) parse with SUTime and import into a temporalEntity list
##      d) Compare SUTime spans with the refToken spans to mark which refToken has temporal information.
##      e) Loop through refTokens to find those in the positive list of Periods and Calendar Intervals.
##      f) Extract out features from the reftoken once we hit a period of interval and save to a global array.
## 6) Save positive results to a csv file.
##
## To use:

import sys
import os
import argparse
import csv
from nltk.stem.snowball import SnowballStemmer
from copy import deepcopy
from Chrono import chronoEntities
from Chrono import utils
from Chrono import temporalEntity
from Chrono import referenceToken

debug = False
## This method extracts the feature data from the XML files for ML training.
# @param INDIR The location of the directory with all the files in it.
# @param OUTDIR The location of the directory where you want all the output written.
# @param REFDIR The location of the gold standard XML files for evaluation.
# @return Anafora formatted XML files, one directory per file with one XML file in each directory.
# @return The precision and recall from comparing output results to the gold standard.
#####
## Pass in the list of files to train on
## Pass in the location of the gold standard files
## Only import the gold standard files that are in the training files
## The infiles variable need to contain the full path to the input files.

def createMLTrainingMatrix(infiles, gold_folder, ext="", save = False, output = "aquaint_train", window = 3):
    ### Algorithm
    ## For each input file:
    ##      1) parse text to refTokens list
    ##      2) parse SUTime to identify temporal tokens
    ##      3) Import gold standard file
    ##      4) Get list of periods and intervals with start and end coords
    ##      5) For each period/interval:
    ##          - Create feature vector
    ##          - Save features to global list
    ##      6) Write gold features to a csv file for import by other scripts to train ML methods.
    
    ## define list of dictionary feature vectors 
    obs_list = []  ### This is the list of features for each observation
    category = []  ### This is the category of the observation.  1 for period, 0 otherwise. Note that the unknowns are being grouped in with the calendar-interval category.  probably need to parse that out later or change up the algorithm to not be a binary classifier.
    
    features = {'feat_numeric':0, 'feat_temp_context':0, 'feat_temp_self':0}  ### This is the full list of features.  I will use the key values to get the individual feature vectors.

    if(save):
        outfile = open("./gold-standard-parsing.txt", 'w') 
 
    ## Loop through each file and parse
    for f in range(0,len(infiles)) :
        print("ML Parsing "+ infiles[f] +" ...")
        
        ## parse out the doctime
        doctime = utils.getDocTime(infiles[f] + ".dct")
        if(debug) : print(doctime)
        
        ## parse out reference tokens
        text, tokens, spans, tags = utils.getWhitespaceTokens(infiles[f]+ext)
        my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, span=spans, pos=tags)
        
        
        ## mark all ref tokens if they are numeric or temporal
        chroList = utils.markTemporal(my_refToks)
        
        
        ## import gold standard data
        gold_file = os.path.join(gold_folder + os.path.split(infiles[f])[1],"period-interval.gold.csv")
        gold_list=[]
         
        if os.path.exists(gold_file):
            if(save):
                outfile.write("\n$$$$$$$$$$$\nProcessing: "+gold_file)
            with open(gold_file) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    gold_list.append({'type': row['type'], 'start': row['start'], 'end':row['end'], 'value':row['value']})
                    if(save):
                        outfile.write("\n"+str(row))
    
            ## loop through each reftoken term and see if it overlaps with a gold token
            for r in range(0,len(chroList)):
                reftok = chroList[r]
                ref_s, ref_e = reftok.getSpan()
                # loop through each gold instance and find the one that overlaps with the current reftok.
                for g in gold_list:
                   # print(str(g))
                    if utils.overlap([ref_s,ref_e], [int(g['start']),int(g['end'])] ):
                        this_obs = {}
                        # if the gold token overlaps with the current reftok we need to extract the features from the reftok and add it to the list
                        
                        if(save):
                            outfile.write("\nPrevious Token: " + str(chroList[max(r-1, 0)]))
                            outfile.write("\nTarget Token: "+str(reftok))
                            #print("Length: "+ str(len(my_refToks)) + "Last: "+str(min(r+1, len(my_refToks))))
                            outfile.write("\nNext Token: " + str(chroList[min(r+1, len(my_refToks)-1)])+"\n")
                        
                        ### Identify Temporal features
                        this_obs = extract_temp_features(chroList, r, 3, this_obs)
                        
                        ### Extract all words within a N-word window
                        this_obs, observations = extract_bow_features(chroList, r, window, features, this_obs)
                        
                        ### Determine if there is a numeric before or after the target word.
                        this_obs = extract_numeric_feature(chroList, r, this_obs)
                        
                        ### Stem and extract the actual word
                        this_obs, observations = extract_stem_feature(chroList[r], features, this_obs)
                        
                        ### Get the correct type 
                        if(g['type']=='Period'):
                            category.append(1)
                        else:
                            category.append(0)
                        
                        obs_list.append(this_obs)
                    
    ## Ok, I have all the features.  Now I just need to put them all together in a matrix.
    print("features length: " + str(len(features.keys())))
    print("obs_list length: " + str(len(obs_list)))
    print("category length: " + str(len(category)))
    
    ## Now I need to loop through the obs_list to create a list of features that contain all feature elements.
    full_obs_list = [] # a list of tuples
    for i in range(0,len(obs_list)):
        feats = deepcopy(features)
        feats.update(obs_list[i])
        #full_obs_list.append((feats, category[i]))
        full_obs_list.append(feats)
    
    ## Now print the list of tuples to a file, then return the list.
    keys = full_obs_list[0].keys()
    with open(output+'_data.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(full_obs_list)
    
    with open(output+'_class.csv','w') as output_file:
        for c in category:
            output_file.write("%s\n" % c)
    
    ### Now return the feature list and the categories
    return(full_obs_list, category)

######
## END Function
###### 

## This method processes the target word by lower casing and stemming the word.
# @author Amy Olex 
# @param reftok the target token to be stemmed
# @param obs_dict The global dictionary to be updated with the unique observations from this method.
# @return Returns a dictionary with the stemmed word and a value of 1. Also returns the updated observation dictionary.
# Note: Add in this method to extract any potential numbers from a merged phrase.  E.g. "twoweeks" needs to extract "two"
# and add it to the dictionary.  Need to convert it to a number as well before adding.
def extract_stem_feature(reftok, obs_dict, obs_list):
    my_str = reftok.getText().lower()
    for r in ["quarter","decades","decade","yesterday","yesterdays","today","todays","day","week","month","year","daily","weekly","monthly","yearly","century","minute","second","hour","hourly","days","weeks","months","years","centuries", "minutes","seconds","hours"]:
        idx = my_str.find(r)
        if(idx >= 0):
            obs_dict.update({r:0})
            obs_list.update({r:1})
            return(obs_list, obs_dict)

    stemmer = SnowballStemmer("english")
    #print(stemmer.stem(reftok.getText().lower()))
    obs_dict.update({stemmer.stem(reftok.getText().lower()): 0})
    obs_list.update({stemmer.stem(reftok.getText().lower()): 1})
    
    return(obs_list, obs_dict)
    
######
## END Function
######  


## This method determines if the target word has a numeric feature directly before or after it.
# @author Amy Olex
# @param reftok_list The list of reference tokens.
# @param reftok_idx The index of the target token that overlaps with the gold standard.
# @return Returns a boolean value of 1 if a numeric feature exists, 0 otherwise.
def extract_numeric_feature(reftok_list, reftok_idx, obs_list):
    ## identify numeric feature
    before = max(reftok_idx-1,0)
    after = min(reftok_idx+1,len(reftok_list)-1)
    
    if(before != reftok_idx and isinstance(utils.getNumberFromText(reftok_list[before].getText()), (int))):
        obs_list.update({'feat_numeric':1})
        return(obs_list)
    elif(after != reftok_idx and isinstance(utils.getNumberFromText(reftok_list[after].getText()), (int))):
        obs_list.update({'feat_numeric':1})
        return(obs_list)
    else:
        obs_list.update({'feat_numeric':0})
        return(obs_list)
######
## END Function
######  


## This method extracts all words within n-word window before and after the target word.
# @author Amy Olex
# @param reftok_list The list of reference tokens.
# @param reftok_idx The index of the target token that overlaps with the gold standard.
# @param window The number of tokens to search before and after.
# @param obs_dict The global dictionary to be updated with the unique observations from this method.
# @return Returns a dictionary with the word as the key and a 1 as the value., also returns the updated observation dict.
# Note: All numeric values are converted to their integer form before being added to the dictionaries.
def extract_bow_features(reftok_list, reftok_idx, window, obs_dict, obs_list):
    ## identify bow feature
    #this_bow = {}
    
    start = max(reftok_idx-window,0)
    end = min(reftok_idx+(window+1),len(reftok_list)-1)
    
    for r in range(start, end):
        if r != reftok_idx:
            num_check = utils.getNumberFromText(reftok_list[r].getText())
            if(isinstance(num_check, (int))):
                #this_bow[num_check] = 1
                obs_list.update({num_check: 1})
                obs_dict.update({num_check: 0})
            else:
                #this_bow[reftok_list[r].getText()] = 1
                obs_list.update({reftok_list[r].getText(): 1})
                obs_dict.update({reftok_list[r].getText(): 0})
    #print(str(this_bow))
    return(obs_list, obs_dict)
######
## END Function
######  


 
                        
## This method extracts the temporal features from the data set for a given instance of period or interval.  It extracts whether or not the target token itself is identified as a temporal phrase, and if there are any temporal words within a window of 3 before and 3 after.
# @author Amy Olex
# @param reftok_list The list of reference tokens.
# @param reftok_idx The index of the target token that overlaps with the gold standard.
# @param window The number of tokens to search before and after for temporal features.
# @return Returns two boolean values t_self and t_context.  1 if a temporal feature was found, and 0 otherwise.
def extract_temp_features(reftok_list, reftok_idx, window, obs_list):
    ## identify temp_self feature
    t_self = 0
    t_context = 0
    
    if reftok_list[reftok_idx].isTemporal():
        t_self = 1
    
    ## identify temp_context within 3 words to either side of the target.
    start = max(reftok_idx-window,0)
    end = min(reftok_idx+(window+1),len(reftok_list)-1)
    for r in range(start, end):
        if r != reftok_idx:
            if reftok_list[r].isTemporal():
                t_context = 1
                break
    obs_list.update({'feat_temp_context':t_context})
    obs_list.update({'feat_temp_self':t_self})
    return(obs_list)
    #return({'feat_temp_context':t_context}, {'feat_temp_self':t_self})
######
## END Function
######   
    
 
if __name__ == "__main__":
    
    ## Parse input arguments
    parser = argparse.ArgumentParser(description='Parse a directory of files to identify and normalize temporal information.')
    parser.add_argument('-i', metavar='inputdir', type=str, help='path to the input directory.', required=True)
    parser.add_argument('-x', metavar='fileExt', type=str, help='input file extension if exists. Default is and empty string', required=False, default="")
    parser.add_argument('-o', metavar='outputFilePrefix', type=str, help='The output file name prefix with path if needed.', required=True)
    parser.add_argument('-g', metavar='goldStandard', type=str, help='path to the gold standard directory.', required=True)
    parser.add_argument('-w', metavar='windowSize', type=str, help='An integer representing the window size for context feature extraction. Default is 3.', required=False, default=3)
    
    args = parser.parse_args()
    ## Now we can access each argument as args.i, args.o, args.r
    
    ## Get list of folder names in the input directory
    indirs = []
    infiles = []
    outfiles = []
    outdirs = []
    goldfiles = []
    for root, dirs, files in os.walk(args.i, topdown = True):
       for name in dirs:
           
          indirs.append(os.path.join(root, name))
          infiles.append(os.path.join(root,name,name))
          outfiles.append(os.path.join(args.o,name,name))
          outdirs.append(os.path.join(args.o,name))
          goldfiles.append(os.path.join(args.g,name,"period-interval.gold.csv"))
          if not os.path.exists(os.path.join(args.o,name)):
              os.makedirs(os.path.join(args.o,name))
    
    ## Create the training data matrix and write to a file
    train_data, train_class = createMLTrainingMatrix(infiles, args.g, args.x, False, args.o, int(args.w))
    print("Completed creating ML training matrix files.")   
    
    
    
    
    
