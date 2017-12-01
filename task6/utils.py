## Provides all helper functions for task6 project.  These can be seperated into files later if needed.
#
# Programmer Name: Amy Olex
#
# Date: 9/16/17

import nltk
from nltk.tokenize import WhitespaceTokenizer
from nltk.stem.snowball import SnowballStemmer
from task6 import t6Entities as t6
import dateutil.parser
import datetime
from task6 import SUTime_To_T6
import re
import csv
from collections import OrderedDict
import numpy as np
from word2number import w2n

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
    return text, tokenized_text, spans

## Reads in the dct file and converts it to a datetime object.
# @author Amy Olex
# @param file_path The path and file name of the dct file.
# @return A datetime object
def getDocTime(file_path):
    file = open(file_path, "r")
    text = file.read()
    return(dateutil.parser.parse(text))

## Manually creates the wsj_0152 t6Entity data
# @author Amy Olex
# @return A list of t6 entity objects
def manualT6AddEntities(t6list):
    t6list.append(t6.T6HourOfDayEntity(entityID=32, start_span=393, end_span=394, value=5, ampm=40, time_zone=35,sub_interval=None, number=None, modifier=None))
    t6list.append(t6.T6MonthOfYearEntity(entityID=33, start_span=12, end_span=14, month_type="November",sub_interval=41, number=None, modifier=None))
    t6list.append(t6.T6MonthOfYearEntity(entityID=34, start_span=536, end_span=540, month_type="November",sub_interval=42, number=None, modifier=None))
    t6list.append(t6.T6TimeZoneEntity(entityID=35, start_span=400, end_span=403))
    t6list.append(t6.T6MonthOfYearEntity(entityID=36, start_span=145, end_span=149, month_type="November",sub_interval=37, number=None, modifier=None))
    t6list.append(t6.T6DayOfMonthEntity(entityID=37, start_span=150, end_span=151, value=6,sub_interval=None, number=None, modifier=None))
    t6list.append(t6.T6MonthOfYearEntity(entityID=38, start_span=152, end_span=154, month_type="November",sub_interval=39, number=None, modifier=None))
    t6list.append(t6.T6DayOfMonthEntity(entityID=39, start_span=155, end_span=157, value=2,sub_interval=None, number=None, modifier=None))
    t6list.append(t6.T6AMPMOfDayEntity(entityID=40, start_span=395, end_span=399, ampm_type="PM", number=None, modifier=None))
    t6list.append(t6.T6DayOfMonthEntity(entityID=41, start_span=15, end_span=17, value=2,sub_interval=None, number=None, modifier=None))
    t6list.append(t6.T6DayOfMonthEntity(entityID=42, start_span=541, end_span=542, value=6,sub_interval=None, number=None, modifier=None))
    t6list.append(t6.T6TwoDigitYearOperator(entityID=43, start_span=158, end_span=160, value=89, sub_interval=38))
    t6list.append(t6.T6MonthOfYearEntity(entityID=44, start_span=404, end_span=408, month_type="November",sub_interval=45, number=None, modifier=None))
    t6list.append(t6.T6DayOfMonthEntity(entityID=45, start_span=409, end_span=410, value=9,sub_interval=32, number=None, modifier=None))
    t6list.append(t6.T6TwoDigitYearOperator(entityID=46, start_span=18, end_span=20, value=89, sub_interval=33))
    t6list.append(t6.T6NextOperator(entityID=47, start_span=145, end_span=149, period=None, repeating_interval=36))
    t6list.append(t6.T6NextOperator(entityID=48, start_span=404, end_span=408, period=None, repeating_interval=44))
    t6list.append(t6.T6NextOperator(entityID=49, start_span=536, end_span=540, period=None, repeating_interval=34))
    t6list.append(t6.T6BetweenOperator(entityID=50, start_span=139, end_span=144, start_interval_type="DocTime", end_interval_type="Link", end_interval=47))
    t6list.append(t6.T6BetweenOperator(entityID=51, start_span=387, end_span=392, start_interval_type="DocTime", end_interval_type="Link", end_interval=48))
    
    return(t6list)
####
#END_MODULE
####

  
## Writes out the full XML file for all T6entities in list.
# @author Amy Olex
# @param t6list The list of T6 objects needed to be written in the file.
# @param outfile A string containing the output file location and name.
def write_xml(t6list, outfile):
    fout = open(outfile + ".completed.xml", "w")
    fout.write("<data>\n<annotations>\n")
    for t6 in t6list :
        fout.write(str(t6.print_xml()))
    
    fout.write("\n</annotations>\n</data>")
    fout.close()
 ####
 #END_MODULE
 ####   


## Marks all the reference tokens that show up in the SUTime entity list.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @param suList The list of SUtime entities to compare against
def markTemporalRefToks(refToks, suList):
    for ref in refToks:
        for su in suList:
            suStart, suEnd = su.getSpan()
            if ref.spanOverlap(suStart, suEnd):
                ref.setTemporal(True)
        if ref.isTemporal() is None:
            ref.setTemporal(False)
    return refToks
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
        text_lower = text.lower()
        if(re.search('1st|first', text_lower) is not None):
            number = 1
        elif(re.search('2nd|second', text_lower) is not None):
            number = 2
        elif(re.search('3rd|third', text_lower) is not None):
            number = 3
        elif(re.search('4th|fourth', text_lower) is not None):
            number = 4
        elif(re.search('5th|fifth', text_lower) is not None):
            number = 5
        elif(re.search('6th|sixth', text_lower) is not None):
            number = 6
        elif(re.search('7th|seventh', text_lower) is not None):
            number = 7
        elif(re.search('8th|eighth', text_lower) is not None):
            number = 8
        elif(re.search('9th|ninth', text_lower) is not None):
            number = 9
        elif(re.search('10th|tenth', text_lower) is not None):
            number = 10
        elif(re.search('11th|eleventh', text_lower) is not None):
            number = 11
        elif(re.search('12th|twelfth', text_lower) is not None):
            number = 12
        elif(re.search('13th|thirteenth', text_lower) is not None):
            number = 13
        elif(re.search('14th|fourteenth', text_lower) is not None):
            number = 14
        elif(re.search('15th|fifteenth', text_lower) is not None):
            number = 15
        elif(re.search('16th|sixteenth', text_lower) is not None):
            number = 16
        elif(re.search('17th|seventeenth', text_lower) is not None):
            number = 17
        elif(re.search('18th|eighteenth', text_lower) is not None):
            number = 18
        elif(re.search('19th|nineteenth', text_lower) is not None):
            number = 19
        elif(re.search('20th|twentieth', text_lower) is not None):
            number = 20
        elif(re.search('21st|twenty-first', text_lower) is not None):
            number = 21
        elif(re.search('22nd|twenty-second', text_lower) is not None):
            number = 22
        elif(re.search('23rd|twenty-third', text_lower) is not None):
            number = 23
        elif(re.search('24th|twenty-fourth', text_lower) is not None):
            number = 24
        elif(re.search('25th|twenty-fifth', text_lower) is not None):
            number = 25
        elif(re.search('26th|twenty-sixth', text_lower) is not None):
            number = 26
        elif(re.search('27th|twenty-seventh', text_lower) is not None):
            number = 27
        elif(re.search('28th|twenty-eighth', text_lower) is not None):
            number = 28
        elif(re.search('29th|twenty-ninth', text_lower) is not None):
            number = 29
        elif(re.search('30th|thirtieth', text_lower) is not None):
            number = 30
        elif(re.search('31st|thirty-first', text_lower) is not None):
            number = 31
        else:
            number = None                                                                                                                    

    return number
####
#END_MODULE
####      
  
  
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


## Function to extract prediction features
# @author Amy Olex
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
        
    
    