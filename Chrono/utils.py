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



## Provides all helper functions for Chrono methods. 


import nltk
from nltk.tokenize import WhitespaceTokenizer
from nltk.stem.snowball import SnowballStemmer
# from Chrono import chronoEntities as t6
from Chrono import temporalTest as tt
import dateutil.parser
# import datetime
# from Chrono import TimePhrase_to_Chrono
from Chrono import TimePhraseEntity as tp
import re
import csv
from collections import OrderedDict
import numpy as np
#from word2number import w2n
from Chrono import w2ny as w2n
import string
import copy

## Parses a text file to idenitfy all tokens seperated by white space with their original file span coordinates.
# @author Amy Olex
# @param file_path The path and file name of the text file to be parsed.
# @return text String containing the raw text blob from reading in the file.
# @return tokenized_text A list containing each token that was seperated by white space.
# @return spans The coordinates for each token.
def getWhitespaceTokens(file_path):
    file = open(file_path, "r")
    text = file.read()
    span_generator = WhitespaceTokenizer().span_tokenize(text)
    spans = [span for span in span_generator]
    tokenized_text = WhitespaceTokenizer().tokenize(text)
    tags = nltk.pos_tag(tokenized_text)
    return text, tokenized_text, spans, tags

## Reads in the dct file and converts it to a datetime object.
# @author Amy Olex
# @param file_path The path and file name of the dct file.
# @return A datetime object
def getDocTime(file_path):
    file = open(file_path, "r")
    text = file.read()
    return(dateutil.parser.parse(text))

  
## Writes out the full XML file for all T6entities in list.
# @author Amy Olex
# @param chrono_list The list of Chrono objects needed to be written in the file.
# @param outfile A string containing the output file location and name.
def write_xml(chrono_list, outfile):
    fout = open(outfile + ".completed.xml", "w")
    fout.write("<data>\n<annotations>\n")
    for c in chrono_list :
        fout.write(str(c.print_xml()))
    
    fout.write("\n</annotations>\n</data>")
    fout.close()
 ####
 #END_MODULE
 ####   


## Marks all the reference tokens that show up in the TimePhrase entity list.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @param tpList The list of TimePhrase entities to compare against
### I don't think we need/use this any longer.  Maybe can be recycled for something else.
#def markTemporalRefToks(refToks, tpList):
#    for ref in refToks:
#        for tp in tpList:
#            tpStart, tpEnd = tp.getSpan()
#            if ref.spanOverlap(tpStart, tpEnd):
#                ref.setTemporal(True)
#        if ref.isTemporal() is None:
#            ref.setTemporal(False)
#    return refToks
####
#END_MODULE
####
    
## Takes in a text string and returns the numerical value
# @author Amy Olex
# @param text The string containing our number
# @return value The numerical value of the text string, None is returned if there is no number
def getNumberFromText(text):
    try :
        number = w2n.word_to_num(text)
    except ValueError:
        number = isOrdinal(text)                                                                                                                   

    return number
####
#END_MODULE
####  

## Function to identify an ordinal number
# @author Amy Olex
# @param text The text string to be tested for an ordinal.
def isOrdinal(text):
    text_lower = text.lower()
    if text_lower == '1st' or text_lower== 'first': #re.search('1st|first', text_lower) is not None):
        number = 1
    elif text_lower == '2nd' or text_lower== 'second':
        number = 2
    elif text_lower == '3rd' or text_lower== 'third':
        number = 3
    elif text_lower == '4th' or text_lower== 'fourth':
        number = 4
    elif text_lower == '5th' or text_lower== 'fifth':
        number = 5
    elif text_lower == '6th' or text_lower== 'sixth':
        number = 6
    elif text_lower == '7th' or text_lower== 'seventh':
        number = 7
    elif text_lower == '8th' or text_lower== 'eighth':
        number = 8
    elif text_lower == '9th' or text_lower== 'nineth':
        number = 9
    elif text_lower == '10th' or text_lower== 'tenth':
        number = 10
    elif text_lower == '11th' or text_lower== 'eleventh':
        number = 11
    elif text_lower == '12th' or text_lower== 'twelveth':
        number = 12
    elif text_lower == '13th' or text_lower== 'thirteenth':
        number = 13
    elif text_lower == '14th' or text_lower== 'fourteenth':
        number = 14
    elif text_lower == '15th' or text_lower== 'fifteenth':
        number = 15
    elif text_lower == '16th' or text_lower== 'sixteenth':
        number = 16
    elif text_lower == '17th' or text_lower== 'seventeenth':
        number = 17
    elif text_lower == '18th' or text_lower== 'eighteenth':
        number = 18
    elif text_lower == '19th' or text_lower== 'nineteenth':
        number = 19
    elif text_lower == '20th' or text_lower== 'twentieth':
        number = 20
    elif text_lower == '21st' or text_lower== 'twenty first':
        number = 21
    elif text_lower == '22nd' or text_lower== 'twenty second':
        number = 22
    elif text_lower == '23rd' or text_lower== 'twenty third':
        number = 23
    elif text_lower == '24th' or text_lower== 'twenty fourth':
        number = 24
    elif text_lower == '25th' or text_lower== 'twenty fifth':
        number = 25
    elif text_lower == '26th' or text_lower== 'twenty sixth':
        number = 26
    elif text_lower == '27th' or text_lower== 'twenty seventh':
        number = 27
    elif text_lower == '28th' or text_lower== 'twenty eighth':
        number = 28
    elif text_lower == '29th' or text_lower== 'twenty nineth':
        number = 29
    elif text_lower == '30th' or text_lower== 'thirtieth':
        number = 30
    elif text_lower == '31st' or text_lower== 'thirty first':
        number = 31
    else:
        number = None
    
    return number
       
####
#END_MODULE
####    
  
## Function to get the integer representation of a text month
# @author Amy Olex  
# @param text The text string to be converted to an integer.
def getMonthNumber(text):
    month_dict = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10,'November':11, 'December':12}
    return month_dict[text]
   
## Function to determine if the input span overlaps this objects span
# @author Amy Olex
# @param sp1 a 2-tuple with the first start and end span
# @param sp2 a 2-tuple with the second start and end span
# @output True or False
def overlap(sp1, sp2) :
    x=set(range(int(sp1[0]), int(sp1[1])))
    y=set(range(int(sp2[0]), int(sp2[1])))
    if list(set(x) & set(y)) != []:
        return True
    else:
        return False 
        
        
        
## Function to extract prediction features
# @author Amy Olex
# @param reftok_list The full document being parsed as a list of tokens.
# @param reftok_idx The index of the target token in the reference list.
# @param feature_dict A dictionary with the features to be extracted listed as the keys and the values all set to zero.
# @return A dictionary with the features as keys and the values set to 0 if not present, and 1 if present for the target word.
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
######
## END Function
###### 


## Function that get the list of features to extract from the input training data matrix file.
# @author Amy Olex
# @param data_file The name and path the the data file that contains the training matrix.  The first row is assumed to be the list of features.
# @return A dictionary with all the features stored as keys and the values set to zero.
def get_features(data_file):
    ## Import csv files
    data_list = []
    with open(data_file) as file:
        reader = csv.DictReader(file)
        data_list = [row for row in reader]

    ## Create the empty orderedDict to pass back for use in the other methods.
    dict_keys = data_list[0].keys()

    dic = OrderedDict(zip(dict_keys, list(np.repeat('0',len(dict_keys)))))
    
    return(dic)
######
## END Function
###### 

## Marks all the reference tokens that are identified as temporal.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @return modified list of reftoks
def markTemporal(refToks):
    for ref in refToks:
        #mark if numeric
        ref.setNumeric(numericTest(ref.getText(), ref.getPos()))
        #mark if temporal
        ref.setTemporal(temporalTest(ref.getText()))
        
    return refToks
####
#END_MODULE
####

## Tests to see if the token is a number.
# @author Amy Olex
# @param tok The token string
# @return Boolean true if numeric, false otherwise
def numericTest(tok, pos):
    
    if pos == "CD":
        return True
    else:
        #remove punctuation
        tok = tok.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))).strip()
    
        #test for a number
        #tok.strip(",.")
        val = getNumberFromText(tok)
        #print("Testing Number: Tok: " + tok + "  Val:" + str(val))
        if val is not None:
            return True
        return False
####
#END_MODULE
#### 


## Tests to see if the token is a temporal value.
# @author Amy Olex
# @param tok The token string
# @return Boolean true if temporal, false otherwise
def temporalTest(tok):
    #remove punctuation
    #tok = tok.translate(str.maketrans("", "", string.punctuation))
    
    #if the token has a dollar sign or percent sign it is not temporal
    m = re.search('[#$%]', tok)
    if m is not None:
        return False
    
    #look for date patterns mm[/-]dd[/-]yyyy, mm[/-]dd[/-]yy, yyyy[/-]mm[/-]dd, yy[/-]mm[/-]dd
    m = re.search('([0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4})', tok)
    if m is not None:
        return True
    #looks for a string of 8 digits that could possibly be a date in the format 19980304 or 03041998 or 980304
    m = re.search('([0-9]{4,8})', tok)
    if m is not None:
        if tt.has24HourTime(m.group(0)):
            return True
        if tt.hasDateOrTime(m.group(0)):
            return True
    
    #look for time patterns hh:mm:ss
    m = re.search('([0-9]{2}:[0-9]{2}:[0-9]{2})', tok)
    if m is not None:
        return True
     
   
    if tt.hasTextMonth(tok):
        return True
    if tt.hasDayOfWeek(tok):
        return True
    if tt.hasPeriodInterval(tok):
        return True
    if tt.hasAMPM(tok):
        return True
    if tt.hasPartOfWeek(tok):
        return True
    if tt.hasSeasonOfYear(tok):
        return True
    if tt.hasPartOfDay(tok):
        return True
    if tt.hasTimeZone(tok):
        return True
    if tt.hasTempText(tok):
        return True
    if tt.hasModifierText(tok):
        return True
    
    
####
#END_MODULE
#### 

## Takes in a Reference List that has had numeric and temporal tokens marked, and identifies all the 
## temporal phrases by finding consecutive temporal tokens.
# @author Amy Olex
# @param chroList The list of temporally marked reference tokens
# @return A list of temporal phrases for parsing
def getTemporalPhrases(chroList, doctime):
    #TimePhraseEntity(id=id_counter, text=j['text'], start_span=j['start'], end_span=j['end'], temptype=j['type'], tempvalue=j['value'], doctime=doctime)
    id_counter = 0
    
    phrases = [] #the empty phrases list of TimePhrase entities
    tmpPhrase = [] #the temporary phrases list.
    inphrase = False
    for n in range(0,len(chroList)):
        #if temporal start building a list 
        #print("Filter Start Phrase: " + str(chroList[n]))   
        if chroList[n].isTemporal():
            #print("Is Temporal: " + str(chroList[n]))
            if not inphrase:
                inphrase = True
            #in phrase, so add new element
            tmpPhrase.append(copy.copy(chroList[n]))
            # test to see if a new line is present.  If it is AND we are in a temporal phrase, end the phrase and start a new one.
            # if this is the last token of the file, end the phrase.
            if n == len(chroList)-1:
                if inphrase:
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False
            else:
                s1,e1 = chroList[n].getSpan()
                s2,e2 = chroList[n+1].getSpan()
                if e1+1 != s2 and inphrase:
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False
                
            
        elif chroList[n].isNumeric():
            #print("Not Temporal, but Numeric: " + str(chroList[n]))
            #if the token has a dollar sign or percent sign do not count it as temporal
            m = re.search('[#$%]', chroList[n].getText())
            if m is None:
                #print("No #$%: " + str(chroList[n]))
                #check for the "million" text phrase
                answer = next((m for m in ["million", "billion", "trillion"] if m in chroList[n].getText().lower()), None)
                if answer is None:
                    #print("No million/billion/trillion: " + str(chroList[n]))
                    if not inphrase:
                        inphrase = True
                    #in phrase, so add new element
                    tmpPhrase.append(copy.copy(chroList[n]))
            # test to see if a new line is present.  If it is AND we are in a temporal phrase, end the phrase and start a new one.
            # if this is the last token of the file, end the phrase.
            if n == len(chroList)-1:
                if inphrase:
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False
            else:
                s1,e1 = chroList[n].getSpan()
                s2,e2 = chroList[n+1].getSpan()
                if e1+1 != s2 and inphrase:
                    # print("has new line: " + str(chroList[n]))
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False
        else:
            #current element is not temporal, check to see if inphrase
            #print("Not Temporal, or numeric " + str(chroList[n]))
            if inphrase:
                #set to False, add tmpPhrase as TimePhrase entitiy to phrases, then reset tmpPhrase
                inphrase = False
                #check to see if only a single element and element is numeric, then do not add.
                if len(tmpPhrase) != 1:
                    #print("multi element phrase ")
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                elif not tmpPhrase[0].isNumeric():
                    #print("not numeric: " + str(chroList[n-1]))
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                elif tmpPhrase[0].isNumeric() and tmpPhrase[0].isTemporal():
                    #print("temporal and numeric: " + str(chroList[n-1]))
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                else:
                    #print("Element not added: " + str(chroList[n-1]))
                    tmpPhrase = []
        
            
    return phrases

####
#END_MODULE
#### 


## Takes in a list of reference tokens identified as a temporal phrase and returns one TimePhraseEntity.
# @author Amy Olex
# @param items The list of reference tokesn
# @param counter The ID this TimePhrase entity should have
# @param doctime The document time.
# @return A single TimePhrase entity with the text span and string concatenated.
def createTPEntity(items, counter, doctime):
    start_span, tmp = items[0].getSpan()
    tmp, end_span = items[len(items)-1].getSpan()
    text = ""
    for i in items:
        text = text + ' ' + i.getText()
    
    return tp.TimePhraseEntity(id=counter, text=text.strip(), start_span=start_span, end_span=end_span, temptype=None, tempvalue=None, doctime=doctime)

####
#END_MODULE
####   


## Takes in a reference list of tokens, a start span and an end span
# @author Amy Olex
# @param ref_list The list of reference tokens we want an index for.
# @param start_span The start span of the token we need to find in ref_list
# @param end_span The ending span of the token we need to find
# @return Returns the index of the ref_list token that overlaps the start and end spans provided, or -1 if not found.
def getRefIdx(ref_list, start_span, end_span):
    for i in range(0,len(ref_list)):
        if(overlap(ref_list[i].getSpan(),(start_span,end_span))):
            return i              
    return -1
    
####
#END_MODULE
####           
                
        
    
    
    
