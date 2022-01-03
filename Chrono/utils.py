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
from nltk.tokenize import sent_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize.util import align_tokens
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
import dateutil.parser as dup
import datetime
import inspect
import os
from Chrono.ChronoBert import SentenceObj



## Load the dictionary files

global dictpath
thisfilename = inspect.getframeinfo(inspect.currentframe()).filename
thispath = os.path.dirname(os.path.abspath(thisfilename))
dictpath = os.path.join(thispath,"../dictionary")

global APPROX2
global APPROX3
global APPROX10
global PERIODINT

APPROX2 = [line.rstrip() for line in open(os.path.join(dictpath,"Approximation2.txt"), "r")]
APPROX3 = [line.rstrip() for line in open(os.path.join(dictpath,"Approximation3.txt"), "r")]
APPROX10 = [line.rstrip() for line in open(os.path.join(dictpath,"Approximation10.txt"), "r")]
PERIODINT = [line.rstrip() for line in open(os.path.join(dictpath,"Period-Interval.txt"), "r")]


## Parses a text file to idenitfy all sentences, then identifies all tokens in each sentence seperated by white space with their original file span coordinates.
# @author Amy Olex
# @param file_path The path and file name of the text file to be parsed.
# @return text String containing the raw text blob from reading in the file.
# @return tokenized_text A list containing each token that was seperated by white space.
# @return spans The coordinates for each token.
def getWhitespaceTokens2(file_path):
    file = open(file_path, "r")
    raw_text = file.read()
    ## Testing the replacement of all "=" signs by spaces before tokenizing.
    text = raw_text.translate(str.maketrans("=", ' '))
    
    ## Tokenize the sentences
    sentences = sent_tokenize(text)

    ## Then create a new sentence list by breaking down those with new lines.
    new_sent_list = []
    for s in sentences:
        #print(s)
        if "\n" in s:
            new_sent_list.extend(s.split("\n"))
        else:
            new_sent_list.append(s)
    
    ## Get spans of the sentences
    sent_spans = align_tokens(new_sent_list, text)
    
    ## create empty arrays for white space tokens and sentence delimiters
    tokenized_text = []
    rel_text_spans = []
    abs_text_spans = []
    
    ## Loop through each sentence and get the tokens and token spans
    for s in range(0,len(new_sent_list)):
        # get the tokens and token spans within the sentence
        toks = WhitespaceTokenizer().tokenize(new_sent_list[s])
        span_generator = WhitespaceTokenizer().span_tokenize(new_sent_list[s])
        rel_spans = [span for span in span_generator]
        
        # convert the relative spans into absolute spans
        abs_spans = []
        for start, end in rel_spans:
            abs_spans = abs_spans + [(sent_spans[s][0]+start, sent_spans[s][0]+end)]
        
        tokenized_text = tokenized_text + toks
        abs_text_spans = abs_text_spans + abs_spans
        rel_text_spans = rel_text_spans + rel_spans
    
    ## Now we have the token list and the spans.  We should be able to continue finding sentnence boundaries as before
    tags = nltk.pos_tag(tokenized_text)
    sent_boundaries = [0] * len(tokenized_text)
    sent_membership = [0] * len(tokenized_text)

    ## figure out which tokens are at the end of a sentence
    tok_counter = 0

    for s in range(0,len(new_sent_list)):
        sent = new_sent_list[s]
        print(sent)
        sent_split = WhitespaceTokenizer().tokenize(sent)
        nw_idx = len(sent_split) + tok_counter - 1
        sent_boundaries[nw_idx] = 1
        sent_membership[tok_counter:nw_idx + 1] = [s] * ((nw_idx + 1) - tok_counter)
        tok_counter = tok_counter + len(sent_split)

    #for s in range(0, len(sentences)):
    #    sent = sentences[s]
    #
    #    if "\n" in sent:
    #        sent_newline = sent.split("\n")
    #        for sn in sent_newline:
    #            sent_split = WhitespaceTokenizer().tokenize(sn)
    #            nw_idx = len(sent_split) + tok_counter - 1
    #            sent_boundaries[nw_idx] = 1
    #            sent_membership[tok_counter:nw_idx + 1] = [s] * ((nw_idx + 1) - tok_counter)
    #            tok_counter = tok_counter + len(sent_split)
    #
    #    else:
    #        sent_split = WhitespaceTokenizer().tokenize(sent)
    #        nw_idx = len(sent_split) + tok_counter - 1
    #        sent_boundaries[nw_idx] = 1
    #        sent_membership[tok_counter:nw_idx + 1] = [s] * ((nw_idx + 1) - tok_counter)
    #        tok_counter = tok_counter + len(sent_split)
            
    return raw_text, text, tokenized_text, abs_text_spans, rel_text_spans, tags, sent_boundaries, new_sent_list, sent_membership

 ####
 #END_MODULE
 #### 

## Reads in the dct file and converts it to a datetime object.
# @author Amy Olex
# @param file_path The path and file name of the dct file.
# @return A datetime object
def getDocTime(file, i2b2):
    file = open(file, "r")
    lines = file.readlines()
    print("In get DocTime. Admit Date: " + lines[1])
    print("In get DocTime. Discharge Date: " + lines[3])
    return(dateutil.parser.parse(lines[1]))

 ####
 #END_MODULE
 #### 

## Writes out the full XML file in i2b2 format with all timex entities.
# @author Amy Olex
# @param text The raw text of the document.
# @param phrase_list The parsed temporal phrases as a list of TimePhraseEntity objects with timex metadata.
# @param outfile A string containing the output file location and beginning of file name.
def write_i2b2(text, phrase_list, outfile):
    outname = outfile.replace(".txt", "")
    fout = open(outname, "w")
    
    fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<ClinicalNarrativeTemporalAnnotation>\n<TEXT><![CDATA[\n")
    
    fout.write(text)
    fout.write("\n")
    fout.write("]]></TEXT>\n<TAGS>\n")
    print("Phrase list length: " + str(len(phrase_list)))
    for c in phrase_list :
        fout.write(c.i2b2format())
        fout.write("\n")
    
    fout.write("</TAGS>\n</ClinicalNarrativeTemporalAnnotation>")
    
    fout.close()
 ####
 #END_MODULE
 ####  
 
 
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
    month_dict = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10,'November':11, 'December':12,
                  'JANUARY':1, 'FEBRUARY':2, 'MARCH':3, 'APRIL':4, 'MAY':5, 'JUNE':6, 'JULY':7, 'AUGUST':8, 'SEPTEMBER':9, 'OCTOBER':10,'NOVEMBER':11, 'DECEMBER':12, 
                  'january':1, 'february':2, 'march':3, 'april':4, 'june':6, 'july':7, 'august':8, 'september':9, 'october':10,'november':11, 'december':12,
                  'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'Jun':6, 'Jul':7, 'Aug':8, 'Sept':9, 'Sep':9, 'Oct':10,'Nov':11, 'Dec':12,
                  'jan':1, 'feb':2, 'mar':3, 'apr':4, 'jun':6, 'jul':7, 'aug':8, 'sept':9, 'sep':9, 'oct':10,'nov':11, 'dec':12,
                  'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'JUN':6, 'JUL':7, 'AUG':8, 'SEPT':9, 'SEP':9, 'OCT':10,'NOV':11, 'DEC':12,
                  '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, '11':11, '12':12,
                  '01':1, '02':2, '03':3, '04':4, '05':5, '06':6, '07':7, '08':8, '09':9, '10':10, '11':11, '12':12}
    try:
        value = month_dict[text]
    except KeyError:
        value = 100
    
    return value
   
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
def markTemporal(refToks, include_relative = True):
    for ref in refToks:
        #mark if numeric
        ref.setNumeric(numericTest(ref.getText(), ref.getPos()))
        #mark if temporal
        ref.setTemporal(temporalTest(ref.getText(), include_relative))
    
    ## read in the link terms dictionary
    terms = open("dictionary/LinkTerms.txt", 'r').read().split()
    
    
    ## Now go through the list again and mark all linking words a, an, in, of that appear between 2 temporal and or number tokens.
    for i in range(1, len(refToks)-1):
        if (refToks[i-1].isNumeric() or refToks[i-1].isTemporal()) and (refToks[i+1].isNumeric() or refToks[i+1].isTemporal()) and (refToks[i].getText() in terms):
            refToks[i].setLinkTerm(1)
        
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
def temporalTest(tok, include_relative=True):
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
    
    #look for date patterns mm[/-]dd, mm[/-]yy, mm[/-]yyyy
    m = re.search('([0-9]{1,2}[-/][0-9]{2,4})', tok)
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
    if tt.hasTempText(tok) and include_relative:
        return True
    if tt.hasModifierText(tok):
        return True
    if tt.hasClinAbr(tok):
        return True
    
    return False

####
#END_MODULE
#### 

## Takes in a Reference List that has had numeric and temporal tokens marked, and identifies all the 
## temporal phrases by finding consecutive temporal tokens.
# @author Amy Olex
# @param chroList The list of temporally marked reference tokens
# @return A list of temporal phrases for parsing
def getTemporalPhrases(chroList, sent_list, doctime):
    #TimePhraseEntity(id=id_counter, text=j['text'], abs_start_span=j['start'], abs_end_span=j['end'], type=j['type'], value=j['value'], doctime=doctime)
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
                    phrases.append(createTPEntity(tmpPhrase, id_counter, sent_list, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False
            else:
                s1,e1 = chroList[n].getSpan()
                s2,e2 = chroList[n+1].getSpan()
                
                #if e1+1 != s2 and inphrase:
                if chroList[n].getSentBoundary() and inphrase:
                    #print("Found Sentence Boundary Word!!!!!!!!!")
                    phrases.append(createTPEntity(tmpPhrase, id_counter, sent_list, doctime))
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
                    phrases.append(createTPEntity(tmpPhrase, id_counter, sent_list, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False
            else:
                s1,e1 = chroList[n].getSpan()
                s2,e2 = chroList[n+1].getSpan()
                
                #if e1+1 != s2 and inphrase:
                if chroList[n].getSentBoundary() and inphrase:
                    #print("Found Sentence Boundary Word!!!!!!!!!")
                    phrases.append(createTPEntity(tmpPhrase, id_counter, sent_list, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False
        
        ## Now look for a linking term.  Only continue the phrase if the term is surrounded by numeric or temporal tokens. 
        ## Also, only consider linking terms if we are already in a phrase.
        elif chroList[n].isLinkTerm() and inphrase:
            if (chroList[n-1].isTemporal() or chroList[n-1].isNumeric()) and (chroList[n+1].isTemporal() or chroList[n+1].isNumeric()):
                tmpPhrase.append(copy.copy(chroList[n]))
        
        else:
            #current element is not temporal, check to see if inphrase
            #print("Not Temporal, or numeric " + str(chroList[n]))
            if inphrase:
                #set to False, add tmpPhrase as TimePhrase entitiy to phrases, then reset tmpPhrase
                inphrase = False
                #check to see if only a single element and element is numeric, then do not add.
                if len(tmpPhrase) != 1:
                    #print("multi element phrase ")
                    phrases.append(createTPEntity(tmpPhrase, id_counter, sent_list, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                elif not tmpPhrase[0].isNumeric():
                    #print("not numeric: " + str(chroList[n-1]))
                    phrases.append(createTPEntity(tmpPhrase, id_counter, sent_list, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                elif tmpPhrase[0].isNumeric() and tmpPhrase[0].isTemporal():
                    #print("temporal and numeric: " + str(chroList[n-1]))
                    phrases.append(createTPEntity(tmpPhrase, id_counter, sent_list, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                else:
                    #print("Element not added: " + str(chroList[n-1]))
                    tmpPhrase = []
        
            
    return phrases

####
#END_MODULE
#### 


## Takes in a Reference List that has had numeric and temporal tokens marked, and identifies all the
## temporal phrases by finding consecutive temporal tokens.
## it also extracts and saves related sentence information for later processing with BERT.
# @author Amy Olex
# @param chroList The list of temporally marked reference tokens
# @return A list of temporal phrases for parsing
def getTemporalPhrasesWithSents(chroList, doctime):
    # TimePhraseEntity(id=id_counter, text=j['text'], abs_start_span=j['start'], abs_end_span=j['end'], type=j['type'], value=j['value'], doctime=doctime)
    id_counter = 0

    phrases = []  # the empty phrases list of TimePhrase entities
    tmpPhrase = []  # the temporary phrases list.
    inphrase = False
    for n in range(0, len(chroList)):
        # if temporal start building a list
        # print("Filter Start Phrase: " + str(chroList[n]))
        if chroList[n].isTemporal():
            # print("Is Temporal: " + str(chroList[n]))
            if not inphrase:
                inphrase = True
            # in phrase, so add new element
            tmpPhrase.append(copy.copy(chroList[n]))
            # test to see if a new line is present.  If it is AND we are in a temporal phrase, end the phrase and start a new one.
            # if this is the last token of the file, end the phrase.
            if n == len(chroList) - 1:
                if inphrase:
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False
            else:
                s1, e1 = chroList[n].getSpan()
                s2, e2 = chroList[n + 1].getSpan()

                # if e1+1 != s2 and inphrase:
                if chroList[n].getSentBoundary() and inphrase:
                    # print("Found Sentence Boundary Word!!!!!!!!!")
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False


        elif chroList[n].isNumeric():
            # print("Not Temporal, but Numeric: " + str(chroList[n]))
            # if the token has a dollar sign or percent sign do not count it as temporal
            m = re.search('[#$%]', chroList[n].getText())
            if m is None:
                # print("No #$%: " + str(chroList[n]))
                # check for the "million" text phrase
                answer = next((m for m in ["million", "billion", "trillion"] if m in chroList[n].getText().lower()),
                              None)
                if answer is None:
                    # print("No million/billion/trillion: " + str(chroList[n]))
                    if not inphrase:
                        inphrase = True
                    # in phrase, so add new element
                    tmpPhrase.append(copy.copy(chroList[n]))
            # test to see if a new line is present.  If it is AND we are in a temporal phrase, end the phrase and start a new one.
            # if this is the last token of the file, end the phrase.
            if n == len(chroList) - 1:
                if inphrase:
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False
            else:
                s1, e1 = chroList[n].getSpan()
                s2, e2 = chroList[n + 1].getSpan()

                # if e1+1 != s2 and inphrase:
                if chroList[n].getSentBoundary() and inphrase:
                    # print("Found Sentence Boundary Word!!!!!!!!!")
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inphrase = False

        ## Now look for a linking term.  Only continue the phrase if the term is surrounded by numeric or temporal tokens.
        ## Also, only consider linking terms if we are already in a phrase.
        elif chroList[n].isLinkTerm() and inphrase:
            if (chroList[n - 1].isTemporal() or chroList[n - 1].isNumeric()) and (
                    chroList[n + 1].isTemporal() or chroList[n + 1].isNumeric()):
                tmpPhrase.append(copy.copy(chroList[n]))

        else:
            # current element is not temporal, check to see if inphrase
            # print("Not Temporal, or numeric " + str(chroList[n]))
            if inphrase:
                # set to False, add tmpPhrase as TimePhrase entitiy to phrases, then reset tmpPhrase
                inphrase = False
                # check to see if only a single element and element is numeric, then do not add.
                if len(tmpPhrase) != 1:
                    # print("multi element phrase ")
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                elif not tmpPhrase[0].isNumeric():
                    # print("not numeric: " + str(chroList[n-1]))
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                elif tmpPhrase[0].isNumeric() and tmpPhrase[0].isTemporal():
                    # print("temporal and numeric: " + str(chroList[n-1]))
                    phrases.append(createTPEntity(tmpPhrase, id_counter, doctime))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                else:
                    # print("Element not added: " + str(chroList[n-1]))
                    tmpPhrase = []

    return phrases


####
# END_MODULE
####

## Takes in a reference list and returns an updated reference list with sentence membership
## along with a list of sentences as strings.
# @author Amy Olex
# @param refToks: The list of reference tokens
# @return updated_refToks: The list of reference tokens updated to include sentence membership
# @return sentList: a list of strings where each string is a sentence.
def getSentList(refToks):
    sents = []




####
# END_MODULE
####

## Takes in a list of reference tokens identified as a temporal phrase and returns one TimePhraseEntity.
# @author Amy Olex
# @param items The list of reference tokens
# @param counter The ID this TimePhrase entity should have
# @param sent_list The list of sentences with full text.
# @param doctime The document time.
# @return A single TimePhrase entity with the text span and string concatenated.
def createTPEntity(items, counter, sent_list, doctime):
    abs_start_span, tmp = items[0].getSpan()
    tmp, abs_end_span = items[len(items)-1].getSpan()
    rel_start, tmp = items[0].getRelSpan()
    tmp, rel_end = items[len(items) - 1].getRelSpan()
    abs_token_idx_start = items[0].getID()
    abs_token_idx_end = items[len(items)-1].getID()
    rel_token_idx_start = items[0].getRelID()
    rel_token_idx_end = items[len(items)-1].getRelID()
    sent_idx = items[0].getSentMembership()
    text = ''
    for i in items:
        text = text + ' ' + i.getText()
    
    return tp.TimePhraseEntity(id=counter, text=text.strip(), abs_start_span=abs_start_span, abs_end_span=abs_end_span,
                               rel_start_span=rel_start, rel_end_span=rel_end, abs_token_idx_start=abs_token_idx_start,
                               abs_token_idx_end=abs_token_idx_end, rel_token_idx_start=rel_token_idx_start,
                               rel_token_idx_end=rel_token_idx_end, type=None, mod=None, value=None,
                               sent_membership=sent_idx, sent_text=sent_list[sent_idx], doctime=doctime)

####
#END_MODULE
####   


## Takes in a reference list of tokens, a start span and an end span
# @author Amy Olex
# @param ref_list The list of reference tokens we want an index for.
# @param abs_start_span The start span of the token we need to find in ref_list
# @param abs_end_span The ending span of the token we need to find
# @return Returns the index of the ref_list token that overlaps the start and end spans provided, or -1 if not found.
def getRefIdx(ref_list, start_span, end_span):
    for i in range(0,len(ref_list)):
        if(overlap(ref_list[i].getSpan(),(start_span,end_span))):
            return i              
    return -1
    
####
#END_MODULE
####           

## Identifies the local span of the serach_text in the input "text"
# @author Amy Olex
# @param text The text to be searched
# @param search_text The text to search for.
# @return The start index and end index of the search_text string.
def calculateSpan(text, search_text):
    try:
        start_idx = text.index(search_text)
        end_idx = start_idx + len(search_text)
    except ValueError:
        return None, None

    return start_idx, end_idx


## Takes in list of ChronoEntities and identifies sub-intervals within the list
# @author Amy Olex
# @param list of ChronoEntities
# @return List of ChronoEntities with sub-intervals assigned
def getEntityTypes(chrono_list):
    year = None
    month = None
    day = None
    hour = None
    minute = None
    second = None
    daypart = None
    dayweek = None
    interval = None
    period = None
    nth = None
    nxt = None
    this = None
    tz = None
    ampm = None
    modifier = None
    last = None
    
    entity_count = 0
   
    
    ## loop through all entities and pull out the approriate IDs
    for e in range(0,len(chrono_list)):
        #print(chrono_list[e].get_id())
        e_type = chrono_list[e].get_type()
        #print("E-type: " + e_type)
        
        if e_type == "Two-Digit-Year" or e_type == "Year":
            year = e
            entity_count = entity_count + 1
            # print("YEAR VALUE: " + str(chrono_list[e].get_value()))
        elif e_type == "Month-Of-Year":
            # print("FOUND Month")
            month = e
            entity_count = entity_count + 1
        elif e_type == "Day-Of-Month":
            day = e
            entity_count = entity_count + 1
        elif e_type == "Hour-Of-Day":
            hour = e
            entity_count = entity_count + 1
        elif e_type == "Minute-Of-Hour":
            minute = e
            entity_count = entity_count + 1
        elif e_type == "Second-Of-Minute":
            second = e
            entity_count = entity_count + 1
        elif e_type == "Part-Of-Day":
            daypart = e
            entity_count = entity_count + 1
        elif e_type == "Day-Of-Week":
            dayweek = e
            entity_count = entity_count + 1
        elif e_type == "Calendar-Interval":
            interval = e
            entity_count = entity_count + 1
        elif e_type == "Period":
            period = e
            entity_count = entity_count + 1
        elif e_type == "NthFromStart":
            nth = e
            entity_count = entity_count + 1
        elif e_type == "Next":
            nxt = e
            entity_count = entity_count + 1
        elif e_type == "This":
            this = e
            entity_count = entity_count + 1
        
        elif e_type == "Time-Zone":
            tz = e
            entity_count = entity_count + 1
        elif e_type == "AMPM-Of-Day":
            ampm = e
            entity_count = entity_count + 1
        elif e_type == "Modifier":
            modifier = e
            entity_count = entity_count + 1
        elif e_type == "Last":
            last = e
            entity_count = entity_count + 1
            
    return(year,month,day,hour,minute,second,daypart,dayweek,interval,period,nth,nxt,this,tz,ampm,modifier,last,entity_count)
    

## Takes in list of ChronoEntities and returns the values, blank string if no value
# @author Amy Olex
# @param list of ChronoEntities
# @return String of entity values
def getEntityValues(chrono_list):
    year = ""
    month = ""
    day = ""
    hour = ""
    minute = ""
    second = ""
    daypart = ""
    dayweek = ""
    interval = ""
    period = ""
    nth = ""
    nxt = ""
    this = ""
    tz = ""
    ampm = ""
    modifier = ""
    last = ""
   
    ## loop through all entities and pull out the approriate IDs
    for e in range(0,len(chrono_list)):
        #print(chrono_list[e].get_id())
        e_type = chrono_list[e].get_type()
        #print("E-type: " + e_type)
        
        if e_type == "Two-Digit-Year" or e_type == "Year":
            year = chrono_list[e].get_value()

            # print("YEAR VALUE: " + str(chrono_list[e].get_value()))
        elif e_type == "Month-Of-Year":
            # print("FOUND Month")
            month = chrono_list[e].get_value()
            
        elif e_type == "Day-Of-Month":
            day = chrono_list[e].get_value()
           
        elif e_type == "Hour-Of-Day":
            hour = chrono_list[e].get_value()
            
        elif e_type == "Minute-Of-Hour":
            minute = chrono_list[e].get_value()
            
        elif e_type == "Second-Of-Minute":
            second = chrono_list[e].get_value()
            
        elif e_type == "Part-Of-Day":
            daypart = chrono_list[e].get_value()
            
        elif e_type == "Day-Of-Week":
            dayweek = chrono_list[e].get_value()
            
        elif e_type == "Calendar-Interval":
            interval = chrono_list[e].get_value()
            
        elif e_type == "Period":
            period = chrono_list[e].get_value()
            
        elif e_type == "NthFromStart":
            nth = chrono_list[e].get_value()
            
        elif e_type == "Next":
            nxt = chrono_list[e].get_value()
            
        elif e_type == "This":
            this = chrono_list[e].get_value()
            
        
        elif e_type == "Time-Zone":
            tz = chrono_list[e].get_value()
            
        elif e_type == "AMPM-Of-Day":
            ampm = chrono_list[e].get_value()
            
        elif e_type == "Modifier":
            modifier = chrono_list[e].get_value()
            
        elif e_type == "Last":
            last = chrono_list[e].get_value()
            
            
    return(year,month,day,hour,minute,second,daypart,dayweek,interval,period,nth,nxt,this,tz,ampm,modifier,last)


## Takes in list of ChronoEntities associated with a temporal phrase and returns the associated numbers, blank string if no value
# @author Amy Olex
# @param list of ChronoEntities
# @return Individual ChornoEntities attached to associated concept.
def getPhraseEntities(chrono_list):
    year = ""
    month = ""
    day = ""
    hour = ""
    minute = ""
    second = ""
    daypart = ""
    dayweek = ""
    interval = ""
    period = ""
    nth = ""
    nxt = ""
    this = ""
    tz = ""
    ampm = ""
    modifier = ""
    last = ""
   
    ## loop through all entities and pull out the approriate IDs
    for e in range(0,len(chrono_list)):
        #print(chrono_list[e].get_id())
        e_type = chrono_list[e].get_type()
        #print("E-type: " + e_type)
        
        if e_type == "Two-Digit-Year" or e_type == "Year":
            year = chrono_list[e]

        elif e_type == "Month-Of-Year":
            
            month = chrono_list[e]
            
        elif e_type == "Day-Of-Month":
            day = chrono_list[e]
           
        elif e_type == "Hour-Of-Day":
            hour = chrono_list[e]
            
        elif e_type == "Minute-Of-Hour":
            minute = chrono_list[e]
            
        elif e_type == "Second-Of-Minute":
            second = chrono_list[e]
            
        elif e_type == "Part-Of-Day":
            daypart = chrono_list[e]
            
        elif e_type == "Day-Of-Week":
            dayweek = chrono_list[e]
            
        elif e_type == "Calendar-Interval":
            interval = chrono_list[e]
            
        elif e_type == "Period":
            period = chrono_list[e]
            
        elif e_type == "NthFromStart":
            nth = chrono_list[e]
            
        elif e_type == "Next":
            nxt = chrono_list[e]
            
        elif e_type == "This":
            this = chrono_list[e]
                
        elif e_type == "Time-Zone":
            tz = chrono_list[e]
            
        elif e_type == "AMPM-Of-Day":
            ampm = chrono_list[e]
            
        elif e_type == "Modifier":
            modifier = chrono_list[e]
            
        elif e_type == "Last":
            last = chrono_list[e]
            
            
    return(year,month,day,hour,minute,second,daypart,dayweek,interval,period,nth,nxt,this,tz,ampm,modifier,last)

   
## Takes in list of ChronoEntities and an entity ID and returns the associated number or blank string if no value
# @author Amy Olex
# @param list of ChronoEntities
# @param String name of number entity
# @return Integer number or None value of number entity
def getPhraseNumber(phrase_text, chrono_list, eid):
    
    #loop through entity list to identify Number entity
    if eid:
        for e in chrono_list:
            if e.get_id() == eid:
                print("RETURNING VALUE OF " + str(e.get_value()))
                return(e.get_value(), "NA")
    else:
        print("NO NUMBER")
        print(phrase_text)
        
        phrase_set = set(phrase_text.split())
        print(phrase_set)
        
        #intersect2 = list(set(APPROX2) & phrase_set)
        #print(intersect2)
        
        intersect3 = list(set(APPROX3) & phrase_set)
        print(intersect3)
        
        intersect10 = list(set(APPROX10) & phrase_set)
        print(intersect10)
        
        intersectperiodint = list(set(PERIODINT) & phrase_set)
        print(intersectperiodint)
        
        #if len(intersect2) == 1:
        #    return(2, "APPROX")
        if len(intersect3) == 1:
            return(3, "APPROX")
        elif len(intersect10) == 1:
            return(10,"APPROX")
        elif len(intersectperiodint) == 1:
            print("In PERIODINT")
            if intersectperiodint[0][-1:] == "s":
                return(2,"NA")
            else:
                return(1,"NA")
    return("","NA")


def bert_classify(start_span, end_span, sent_text, sent_idx, bert_model, bert_tokenizer):
    print("Start Span: " + str(start_span))
    print("End Span: " + str(end_span))
    print("Sentence: " + str(sent_text))
    print("Parsing into BERT")
    this_sent = SentenceObj.SentenceObj(text=sent_text, sentence_num=sent_idx, global_sent_char_start_coord=0,
                                        global_sentence_start_coord=0, phrase_idxs=[range(start_span, end_span+1)],
                                        max_length=256, bert_model=bert_model, bert_tokenizer=bert_tokenizer,
                                        context_window=3, gold_labels="", filt=False)
    print("BERT tokenized sentence: " + str(this_sent.bert_tokenized_sentence))


    ## Parse with BERT/create a Document obj with just this sentence??
    ## Extract out the embeddings according to set options.
    ## run through classifier
    ## /Users/alolex/Desktop/CCTR_Git_Repos/PycharmProjects/ChronoBERT/SVM_models_rerun/SVM_trainFull_clinbert2chrono_seq2seq_BIO_4epochs_pretrained_final.pkl
    ## return string of "DATE" or "DURATION".

    ## Once back in the getISO() method, if DURATION, continue as currently coded.  But if DATE, identify an anchor date
    ## then the quantity, and before or after the anchor date.  Calculate date based on that information.
    ## to start the anchor date can just be the document date for now, but implement as a method so it can be updated later.

    return "TMP"

    
    
    
    
    
    
    
    
    
    
       