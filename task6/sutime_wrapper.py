###############################
# Programmer Name: Nicholas Morton
# Date: 9/17/17
# Module Purpose: Wrapper function for SUTime.py
#################################

import os
import json
from task6.sutime import SUTime

#### callSUTIMEParse()
# Function Purpose: Takes in raw text file and performs SUTime's algorithm on #it and returns it in JSON format.
# Input: String containing the location and name of the text file to be parsed.
# Output: JSON string output of raw input file
####
def callSUTimeParse(file_path, jar_files):
    file = open(file_path, "r")
    test_case = file.read()
    file.close()
    #change the file path to your local directory...
    #jar_files = os.path.join(os.path.dirname(__file__), 'jars') ->going to try and get this to work soon
    #jar_files = '/home/nick/enviroments/python-sutime/sutime/jars'
    #jar_files = '/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/CMSC516-SemEval2018-Task6/task6/jars' #make sire you change this to your proper directory!
    print(jar_files)
    sutime = SUTime(jars=jar_files, mark_time_ranges=True)
    outputText = json.dumps(sutime.parse(test_case), sort_keys=True, indent=4)
    return outputText

####
#END_MODULE
####


print(callSUTimeParse("/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_PracticeData/wsj_0152/wsj_0152","/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/CMSC516-SemEval2018-Task6/task6/jars"))