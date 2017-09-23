###############################
# Programmer Name: Amy Olex
# Date: 9/16/17
# Module Purpose: To test functions and modules written.
#################################

from task6 import utils
from task6 import referenceToken
from task6 import sutimeEntity
from task6 import sutime_wrapper

r, t, s = utils.getWhitespaceSpans("/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_PracticeData/wsj_0152/wsj_0152")

print("Raw text is:\n", r)

print("Parsed Tokens are:\n", t)

print("Parsed Spans are:\n", s)

## Converting to a reference Token list

my_list = referenceToken.convertToRefTokens(t, span=s)
my_list[1].setTemporal(1)
print(str(len(my_list)))
for tok in my_list:
    print(tok)
    
## Parsing with SUTime and converting to a list of sutimeEntity objects.
path = "/Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_PracticeData/"
#name = "wsj_0152/wsj_0152"
name = "APW19980820.1428/APW19980820.1428"
jars = "../task6/jars"
json_str = sutime_wrapper.callSUTimeParse(path+name, jars)
suList = sutimeEntity.getSutimeEntityList(sut_json=json_str)
for s in suList:
    print(s)
    