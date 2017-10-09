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

def find_all(a_str,sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def runHeidTime(file_path): 

    with tempfile.TemporaryFile() as tempf:
       command = "java -jar de.unihd.dbs.heideltime.standalone.jar " + file_path
       args=shlex.split(command)
       proc = subprocess.Popen(args, stdout=tempf)
       proc.wait()
       tempf.seek(0)
       outputText=tempf.read()       
       heidList = []
       spanB = []
       spanE = []
       docTime=''
       file = open(file_path + ".dct", "r")
       docTime = file.read()
       id_counter = 0
       strList, spanB, spanE = BuildTimex3List.getList(str(outputText))
       file = open(file_path, "r")
       text = file.read()
       span_generator = WhitespaceTokenizer().span_tokenize(text)
       spans = [span for span in span_generator]
       tokenized_text = WhitespaceTokenizer().tokenize(text)
    
       for i in range(len(strList)):
        hText = strList[i][strList[i].find('">')+2 : strList[i].find('</T')]
        hType = strList[i][strList[i].find('type="')+6 : strList[i].find('" value')]
        hValue = strList[i][strList[i].find('value="')+7 : strList[i].find('">')]
        
        hStartSpan = 0
        hEndSpan = 0

        for j in range(len(tokenized_text)):
            if hText in tokenized_text[j]:
                hStartSpan, hEndSpan = spans[j]
                tokenized_text = tokenized_text[i:]
                spans = spans[i:]
                break                               
                
        heidList.append(HeidEntity.HeidEntity(id=id_counter, text=hText, start_span=hStartSpan, end_span=hEndSpan, sutype=hType, suvalue=hValue,doctime=docTime))
        id_counter = id_counter +1

       return heidList
