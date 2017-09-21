###############################
# Programmer Name: Amy Olex
# Date: 9/16/17
# Module Purpose: To test functions and modules written.
#################################

from task6 import utils
from task6 import referenceToken

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
    
    