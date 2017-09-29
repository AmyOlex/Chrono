###############################
# Programmer Name: Nicholas Morton
# Date: 9/28/17
# Module Purpose: Converts SUTime Entites into T6 Entities
#################################

from task6 import t6Entities as t6

## buildT6List(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param list of SUTime Output
# @param document creation time (optional)
# @output List of T6 entities
def buildT6List(suTimeList, dct=None):
    t6list = []
    for s in suTimeList : 
        #Split each entity into seperate chunks for evaluation
        eid = s.id
        etext = s.text
        eBeginSpan = s.start_span
        eEndSpan = s.end_span
        etype = s.sutype
        evalue = s.suvalue
        
        if "DATE" in etype:
            if len(evalue) == 4: #Found Year Entity, I.E. 1998 // Also want to check for numbers only
                t6Entity = t6.T6YearEntity(eid,eBeginSpan,eEndSpan,evalue)
            if "A" in evalue:  #check for text, replace A with reg expression // found a Month of Year entity // need to determine if sub interval
                t6Entity = t6.T6MonthOfYearEntity(eid, eBeginSpan, eEndSpan, evalue) #need to tweak this a bit                

        t6list.append(t6Entity)         

    return t6list
####
#END_MOD
