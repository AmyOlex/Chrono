###############################
# Programmer Name: Amy Olex
# Date: 9/16/17
# Module Purpose: To test functions and modules written.
#################################

from task6 import utils
from sutime import SUTime
from task6 import sutime_wrapper

r, t, s = utils.getWhitespaceSpans("/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_PracticeData/wsj_0152/wsj_0152")

print("Raw text is:\n", r)

print("Parsed Tokens are:\n", t)

print("Parsed Spans are:\n", s)

su = sutime_wrapper.callSUTimeParse('SampleText.txt',os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jars'))
