## This file imports the gold standard data for training the ML methods.
#
# Date: 11/18/17
#
# Programmer Name: Amy Olex

###### Workflow ######
##
## 1) get location of files to parse (DONE)
## 2) get location of output directory/create output directories (DONE)
## 3) import the list of positive Periods and Calendar-Intervals
## 3) For each FILE:
##      a) parse with stanford parser to get whitespace tokens and associated spans
##      b) import this into a refToken object list
##      c) parse with SUTime and import into a sutimeEntity list
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
from task6 import t6Entities
from task6 import utils
from task6 import sutimeEntity
from task6 import referenceToken
from task6 import sutime_wrapper

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

def createMLTrainingMatrix(infiles, gold_folder, jars, save = False):
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
        outfile = open("/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/CMSC516-SemEval2018-Task6/gold-standard-parsing.txt", 'w') 
 
    ## Loop through each file and parse
    for f in range(0,len(infiles)) :
        print("ML Parsing "+ infiles[f] +" ...")
        
        ## parse out the doctime
        doctime = utils.getDocTime(infiles[f] + ".dct")
        if(debug) : print(doctime)
        
        ## parse out reference tokens
        text, tokens, spans = utils.getWhitespaceTokens(infiles[f])
        my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, span=spans, remove_stopwords="/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/CMSC516-SemEval2018-Task6/task6/stopwords_short2.txt")
        if(debug) :
            print("REFERENCE TOKENS:\n")
            for tok in my_refToks : print(tok)
        
        ## Replace all punctuation with spaces
        my_refToks = referenceToken.replacePunctuation(my_refToks)
        
        ## Convert to lowercase
        my_refToks = referenceToken.lowercase(my_refToks)
        
        ## parse out SUTime entities
        json_str = sutime_wrapper.callSUTimeParse(infiles[f], jars)
        suList = sutimeEntity.import_SUTime(sut_json=json_str, doctime=doctime)
        if(debug) : 
            print("SUTIME ENTITIES:\n")
            for s in suList : print(s)
        
        ## mark all reference tokens that overlap with the sutime spans
        my_refToks = utils.markTemporalRefToks(my_refToks, suList)
        if(debug) : 
            for tok in my_refToks : print(tok)
        
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
            for r in range(0,len(my_refToks)):
                reftok = my_refToks[r]
                ref_s, ref_e = reftok.getSpan()
                # loop through each gold instance and find the one that overlaps with the current reftok.
                for g in gold_list:
                   # print(str(g))
                    if utils.overlap([ref_s,ref_e], [int(g['start']),int(g['end'])] ):
                        this_obs = {}
                        # if the gold token overlaps with the current reftok we need to extract the features from the reftok and add it to the list
                        
                        if(save):
                            outfile.write("\nPrevious Token: " + str(my_refToks[max(r-1, 0)]))
                            outfile.write("\nTarget Token: "+str(reftok))
                            #print("Length: "+ str(len(my_refToks)) + "Last: "+str(min(r+1, len(my_refToks))))
                            outfile.write("\nNext Token: " + str(my_refToks[min(r+1, len(my_refToks)-1)])+"\n")
                        
                        ### Identify Temporal features
                        this_obs = extract_temp_features(my_refToks, r, 5, this_obs)
                        
                        ### Extract all words within a N-word window
                        this_obs, observations = extract_bow_features(my_refToks, r, 5, features, this_obs)
                        
                        ### Determine if there is a numeric before or after the target word.
                        this_obs = extract_numeric_feature(my_refToks, r, this_obs)
                        
                        ### Stem and extract the actual word
                        this_obs, observations = extract_stem_feature(my_refToks[r], features, this_obs)
                        
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
    with open('aquaint_train_data.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(full_obs_list)
    
    with open('aquaint_train_class.csv','w') as output_file:
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
    my_str = reftok.getText()
    for r in ["day","week","year","month","hour","minute","second"]:
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
    
    
    
    
    
    
    
