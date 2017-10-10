## Wrapper function for HeidelTime
#
# Programmer Name: Nicholas Morton
#
# Date: 10/10/2017

import os
import sys
import HeidEntity
import BuildTimex3List
import subprocess
import tempfile
import shlex
import json
import nltk
from nltk.tokenize import WhitespaceTokenizer

## Takes in file path and returns a HeidTimeList
# @author Nicholas Morton
# @param file_path Path and file name of text file to be parsed.
# @return A list of heidTime objects to be returned to the main program
def runHeidTime(file_path): 

    with tempfile.TemporaryFile() as tempf:
       command = "java -jar de.unihd.dbs.heideltime.standalone.jar " + file_path #Run HeidelTime command
       args=shlex.split(command)
       proc = subprocess.Popen(args, stdout=tempf)
       proc.wait()
       tempf.seek(0)
       outputText=tempf.read()  #Read in HeidelTime output     
       heidList = []
       spanB = []
       spanE = []
       docTime=''
       file = open(file_path + ".dct", "r")
       docTime = file.read()
       id_counter = 0
       strList, spanB, spanE = BuildTimex3List.getList(str(outputText)) #get list of TIMEX3 Entites
       file = open(file_path, "r")
       text = file.read()
       span_generator = WhitespaceTokenizer().span_tokenize(text)
       spans = [span for span in span_generator]
       tokenized_text = WhitespaceTokenizer().tokenize(text)  #create Span and token list to help discover proper spans for Heidlist
    
       for i in range(len(strList)):                            #Build HeidTime list to be passed to the main entity
        hText = strList[i][strList[i].find('">')+2 : strList[i].find('</T')]
        hType = strList[i][strList[i].find('type="')+6 : strList[i].find('" value')]
        hValue = strList[i][strList[i].find('value="')+7 : strList[i].find('">')]
        
        hStartSpan = 0
        hEndSpan = 0

        for j in range(len(tokenized_text)):    #try to determine start and end span, needs improvement
            if hText in tokenized_text[j]:
                hStartSpan, hEndSpan = spans[j]
                tokenized_text = tokenized_text[i:]
                spans = spans[i:]
                break                               
                
        heidList.append(HeidEntity.HeidEntity(id=id_counter, text=hText, start_span=hStartSpan, end_span=hEndSpan, sutype=hType, suvalue=hValue,doctime=docTime))
        id_counter = id_counter +1

       return heidList
