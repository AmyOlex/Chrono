## This method reads in the Heidel Time output and returns a list of TIMEX3 entities
#
# Date: 10/10/2017
#
# Programmer Name: Nick Morton

## Searches input text for the location of an input substring
# @author Nicholas Morton
# @param a_str full text to search
# @param sub substring to find in input text
# @return A list of indexes based on the location of the substring
def find_all(a_str,sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches
        
## Takes in HeidelTime output and returns a list of TIMEX3 Entities in a list, as well as the indexes of the searched substrings
# @author Nicholas Morton
# @param output heideltime output
# @return A list of TIMEX3 entities and a list of the found substring indexes
def getList(output):
    str = output
    first = []
    second = []
    #build list of substring indexes, a "hack" of SUTime's Span method
    first = list(find_all(str,"<TIMEX3 "))
    second = list(find_all(str,"/TIMEX3>"))
    strList = []
    #loop through each index and parse out all of the TIMEX3 expressions from the output
    for i in range(len(first)):
        tempStr = str[str.find('<TIMEX3')+1 : str.find('</TIMEX3')]       
        tempStr ="<{0}</TIMEX3>".format(tempStr)
        strList.append(tempStr)
        str = str.split('</TIMEX3',1)[1]               
    
    return strList, first, second
