## Wrapper function for SUTime.py
#
# Programmer Name: Nicholas Morton
#
# Date: 9/17/17

import os
import json
from Chrono.sutime import SUTime
from Chrono import chronoEntities as t6


## Takes in raw text file and performs SUTime's algorithm on #it and returns it in JSON format.
# @author Nicholas Morton
# @param file_path Path and file name of text file to be parsed.
# @param jar_files Path to the location of the jar files.
# @return A json strong of the parsed time information.
def callSUTimeParse(file_path, jar_files):
    file = open(file_path, "r")
    test_case = file.read()
    file.close()
    #print(jar_files)
    sutime = SUTime(jars=jar_files, mark_time_ranges=True)
    #outputText = json.dumps(sutime.parse(test_case), sort_keys=True, indent=4)
    outputText = sutime.parse(test_case)
    return outputText

####
#END_MODULE
####
#print(callSUTimeParse("/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_PracticeData/wsj_0152/wsj_0152","/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/CMSC516-SemEval2018-Task6/Chrono/jars"))

#print(callSUTimeParse("/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_PracticeData/wsj_0152/wsj_0152","/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/sutimetest/python-sutime"))


