###############################
# Programmer Name: Amy Olex
# Date: 9/16/17
# Module Purpose: Provides all helper functions for task6 project.  These can be seperated into files later if needed.
#################################

import nltk
from nltk.tokenize import WhitespaceTokenizer
from task6 import t6Entities as t6
import dateutil.parser
import datetime

#### getWhitespaceTokens()
# Function Purpose: Pasrses a text file to idenitfy all tokens seperated by white space with their original file span coordinates.
# Input: String containing the location and name of the text file to be parsed.
# Outputs: 
#   text - String containing the raw text blob from reading in the file.
#   tokenized_text - a list containing each token that was seperated by white space.
#   spans - the coordinates for each token.
####
def getWhitespaceTokens(file_path):
    file = open(file_path, "r")
    text = file.read()
    span_generator = WhitespaceTokenizer().span_tokenize(text)
    spans = [span for span in span_generator]
    tokenized_text = WhitespaceTokenizer().tokenize(text)
    return text, tokenized_text, spans

def getDocTime(file_path):
    file = open(file_path, "r")
    text = file.read()
    return(dateutil.parser.parse(text))

def manualT6AddEntities():
    t6list = []
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
    
def write_xml(t6list, outfile):
    fout = open(outfile + ".completed.xml", "w")
    fout.write("<data>\n<annotations>\n")
    for t6 in t6list :
        fout.write(str(t6.print_xml()))
    
    fout.write("\n</annotations>\n</data>")
    fout.close()
    
    
    
    
    
    
    
    
    
    
    
    