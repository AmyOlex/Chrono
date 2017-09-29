###############################
# Programmer Name: Nicholas Morton
# Date: 9/28/17
# Module Purpose: Converts SUTime Entites into T6 Entities
#################################

from task6 import t6Entities as t6
import string

## buildT6List(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param list of SUTime Output
# @param document creation time (optional)
# @output List of T6 entities
def buildT6List(suTimeList, dct=None):
    t6list = []
    for s in suTimeList : 
        #Split each entity into seperate chunks for evaluation
        eid = s.split()[0]
        etext = s.split()[1]
        espan = s.split()[2]
        eBeginSpan = epsan.split(",")[0].strip("<") #not sure if this is the best way, gonna write a function soon
        eEndSpan = epspan.split(",")[1].strip(">")
        etype = s.split()[3]
        evalue = s.split()[4]
        
        if "DATE" in etype:
            if len(evalue) == 4: #Found Year Entity, I.E. 1998 // Also want to check for numbers only
                t6Entity = t6.T6YearEntity(eid,eBeginSpan,eEndSpan,evalue)
            if "A" in evalue:  #check for text, replace A with reg expression // found a Month of Year entity // need to determine if sub interval
                t6Entity = t6.T6MonthOfYearEntity(eid, eBeginSpan, eEndSpan, evalue) #need to tweak this a bit                

        t6list.append(t6Entity)         

    return t6list
####
#END_MOD

## hasDayOfWeek(): Takes in a single text string and identifies if it is a day of week
# @author Amy Olex
# @param text The text to be parsed
# @output value The normalized string value for the day of week, or None if no Day of week found.
def hasDayOfWeek(text):
    print("Before:" + text)
    #convert to all lower
    text_lower = text.lower()
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", string.punctuation))
    #print("After:" + text_norm)
    
    M = ["monday","mon","m"]
    T = ["tuesday","tue","tues","t"]
    W = ["wednesday","wed","w"]
    TR = ["thursday","thur","tr","th"]
    F = ["friday","fri","f"]
    S = ["saturday","sat","s"]
    SU = ["sunday","sun","su"]
    
    #test if the text_norm matches any of our day lists.
    if text_norm in M:
        return "Monday"
    elif text_norm in T:
        return "Tuesday"
    elif text_norm in W:
        return "Wednesday"
    elif text_norm in TR:
        return "Thursday"
    elif text_norm in F:
        return "Friday"
    elif text_norm in S:
        return "Saturday"
    elif text_norm in SU:
        return "Sunday"
    else :
        return None
    
####
#END_MOD