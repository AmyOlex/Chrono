###############################
# Programmer Name: Nicholas Morton
# Date: 9/28/17
# Module Purpose: Converts SUTime Entites into T6 Entities
#################################

from task6 import t6Entities as t6
from task6 import utils
import calendar
import string
import re

#Example SUTime List
#Wsj_0152
#0 11/02/89 <12,20> DATE 1989-11-02
#1 Nov. 9 11/02/89 <145,160> DATE 1989-11-02
#2 5 p.m. EST Nov. 9 <393,410> TIME 2017-11-09T17:00-0500
#3 Nov. 6 <536,542> DATE 2017-11-06

#Need a way to handle sub-intervals, still thinking of the best way to do this...


## buildT6List(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param list of SUTime Output
# @param document creation time (optional)
# @output List of T6 entities
def buildT6List(suTimeList, t6ID , dct=None):
    t6List = []
    for s in suTimeList :   
        '''    
        if "DATE" in s.getType():  #parse out Year, Two-Digit Year, Month-of-Year, and Day-of-month
            #Parse out Year function
            t6List, t6ID  = buildT6Year(s,t6ID, t6List)
            #Parse out Two-Digit Year (if applicable) #taking out for now until I figure out what I want to do
            #t6List.append(buildT62DigitYear(s))
            #Parse out Month-of-Year
            t6List, t6ID  = buildT6MonthOfYear(s,t6ID, t6List)
            #Parse out Day-of-Month
            t6List, t6ID  = buildT6DayOfMonth(s,t6ID, t6List)           
            
            
        if "TIME" in s.getType(): #parse out all of Date data as well as Hour-of-Day, Minute-of-Hour, and Second-of-Minute  
            #Parse out Year function
            t6List, t6ID  = buildT6Year(s,t6ID, t6List)
            #Parse out Two-Digit Year (if applicable) #taking out for now until I figure out what I want to do
            #t6List.append(buildT62DigitYear(s))
            #Parse out Month-of-Year
            t6List, t6ID  = buildT6MonthOfYear(s,t6ID, t6List)
            #Parse out Day-of-Month
            t6List, t6ID  = buildT6DayOfMonth(s,t6ID, t6List) 

            #Going to rewrite this function to be a little cleaner soon, just getting my ideas out          
            #Parse out HourOfDay
            t6List, t6ID  = buildT6HourOfDay(s,t6ID, t6List)
            #Parse out MinuteOfHour
            t6List, t6ID  = buildT6MinuteOfHour(s,t6ID,t6List)   
            #Parse out SecondOfMinute
            t6List, t6ID  = buildT6SecondOfMinute(s,t6ID,t6List)

            #call non-standard formatting temporal phrases, need to decide if we are going to read in one SUTime object at a time or pass the list to each function.
        '''    
        t6List, t6ID  = buildDayOfWeek(s,t6ID,t6List)
        t6List, t6ID  = buildTextMonthAndDay(s,t6ID,t6List)            
        t6List, t6ID  = buildAMPM(s,t6ID,t6List)                
        t6List, t6ID  = buildCalendarInterval(s,t6ID,t6List)
        t6List, t6ID  = buildPartOfDay(s,t6ID,t6List)
            

    return t6List, t6ID
####
#END_MODULE
####


#################### Start buildX() Methods #######################


## buildT6Year(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime 
# @output T6Year Entity
def buildT6Year(s, t6ID, t6List):
    t6YearEntity = t6.T6YearEntity(str(t6ID )+"entity",s.start_span,s.end_span-4,s.suvalue.split("-")[0])  
    t6List.append(t6YearEntity)
    t6ID =t6ID +1
    return t6List,t6ID
####
#END_MODULE
####

## buildT62DigitYear(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime 
# @output T6Year Entity
def buildT62DigitYear(s, t6ID, t6List): #format 0203 -> February 2003?
    if len(s.suvalue) == 4:            
        t6YearEntity = t6.T6YearEntity(s.id,s.start_span+2,s.end_span,s.suvalue[-2:])  
    return t6List, t6ID
####
#END_MODULE
####

## buildT6MonthOfYear(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime 
# @output T6MonthOfYear Entity
def buildT6MonthOfYear(s, t6ID, t6List):
    #basing this off of the yyyy-mm-dd format of the value, might need to revisit later
    suval_split = s.suvalue.split("-")
    if len(suval_split) == 3 :
        month = calendar.month_name[int(suval_split[1])] #should be a valid month number (1-12)
        t6MonthOfYear = t6.T6MonthOfYearEntity(str(t6ID )+"entity",s.start_span + 5,s.end_span - 3,month) #might need to pull the proper spans from the reference tokens
        t6List.append(t6MonthOfYear)
        t6ID =t6ID +1
    else :
        t6MonthOfYear = None
        
    return t6List, t6ID
####
#END_MODULE
####

## buildT6MonthOfYear(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime 
# @output T6DayOfMonthEntity
def buildT6DayOfMonth(s, t6ID, t6List):
    #basing this off of the yyyy-mm-dd format of the value, might need to revisit later
    suval_split = s.suvalue.split("-")
    if len(suval_split) == 3 :
        t6DayOfMonth = t6.T6DayOfMonthEntity(str(t6ID )+"entity",s.start_span + 8,s.end_span,suval_split[2]) #might need to pull the proper spans from the reference tokens
        t6List.append(t6DayOfMonth)
        t6ID =t6ID +1
        return t6List, t6ID
    else :
        return t6List, t6ID
    
####
#END_MODULE
####

## buildT6HourOfDay(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime Entity
# @output T6HourOfDay Entity
def buildT6HourOfDay(s, t6ID, t6List):
    if 'TNI' not in s.suvalue:       #had to account for TNI for the overnight one...
        sTime = s.suvalue.split("T")[1] 
        sHour = sTime.split(":")[0]        
        sSet = "AM"
        if int(sHour) > 12: 
            sHour=int(sHour)-12
            sSet = "PM"

        t6HourOfDay = t6.T6HourOfDayEntity(str(t6ID )+"entity",s.start_span+10,s.end_span-8,sHour,sSet)  #might need to pull the proper spans from the reference tokens
        t6List.append(t6HourOfDay)
        t6ID  = t6ID +1
    return t6List, t6ID
####
#END_MODULE
####

## buildT6MinuteOfHour(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime Entity
# @output T6MinuteOfHour Entity
def buildT6MinuteOfHour(s,t6ID, t6List):
    sTime = s.suvalue.split("T")[1] #left with 17:00-0500
    sMinute = sTime.split("-")[0]
    suval_split = s.suvalue.split(":")
    if len(suval_split)==2:
        sMinute = sMinute.split(":")[1] #should be a valid number between 00-59
        t6MinuteOfHour = t6.T6MinuteOfHourEntity(str(t6ID )+"entity",s.start_span+14,s.end_span-6,sMinute)  #might need to pull the proper spans from the reference tokens
        t6List.append(t6MinuteOfHour)
        t6ID  = t6ID +1
    return t6List, t6ID
####
#END_MODULE
####

## buildT6SecondOfMinute(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime Entity
# @output T6HourOfDay Entity
def buildT6SecondOfMinute(s,t6ID, t6List):
    sTime = s.suvalue.split("T")[1] #left with 17:00-0500
    sSecond="00"

    if sTime.count(":") > 1: #Time string like 17:00:00
        sMinute = sTime.split("-")[0]
        sSecond = sMinute.split(":")[2]
    t6SecondOfMinute = t6.T6SecondOfMinuteEntity(str(t6ID )+"entity",s.start_span+14,s.end_span-6,sSecond)  #might need to pull the proper spans from the reference tokens
    t6List.append(t6SecondOfMinute)
    t6ID  = t6ID +1
    return t6List, t6ID
####
#END_MODULE
####


## buildDayOfWeek(): Parses a sutime entity's text field to determine if it contains a day of the week written out in text form, then builds the associated t6entity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @output t6List, t6ID Returns the expanded t6List and the incremented t6ID.
def buildDayOfWeek(s, t6ID, t6List):
    
    boo, val, idxstart, idxend = hasDayOfWeek(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = t6.T6DayOfWeekEntity(entityID=str(t6ID)+"entity", start_span=abs_Sspan, end_span=abs_Espan, day_type=val)
        t6List.append(my_entity)
        t6ID = t6ID+1
        #check here to see if it has a modifier
        hasMod, mod_type, mod_start, mod_end = hasModifier(s)
        if(hasMod):
            if mod_type == "This":
                t6List.append(t6.T6ThisOperator(entityID=t6ID, start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                t6ID = t6ID+1
                
            if mod_type == "Next":
                t6List.append(t6.T6NextOperator(entityID=t6ID, start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                t6ID = t6ID+1
                
            if mod_type == "Last":
                t6List.append(t6.T6LastOperator(entityID=t6ID, start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                t6ID = t6ID+1
            else:
                t6List.append(t6.T6LastOperator(entityID=t6ID, start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                t6ID = t6ID+1
                
        else:
            t6List.append(t6.T6LastOperator(entityID=t6ID, start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
            t6ID = t6ID+1
    
        
    return t6List, t6ID
####
#END_MODULE
####    


## buildTextMonth(): Parses a sutime entity's text field to determine if it contains a month of the year, written out in text form, followed by a day, then builds the associated t6entity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @output t6List, t6ID Returns the expanded t6List and the incremented t6ID.
# ISSUE: This method assumes the day appears after the month, but that may not always be the case as in "sixth of November"
def buildTextMonthAndDay(s, t6ID, t6List):
    
    boo, val, idxstart, idxend = hasTextMonth(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_month_entity = t6.T6MonthOfYearEntity(entityID=str(t6ID)+"entity", start_span=abs_Sspan, end_span=abs_Espan, month_type=val)
        t6ID = t6ID+1
        
        #check to see if it has a day associated with it.  We assume the day comes after the month.
        #idx_end is the last index of the month.  If there are any characters after it the lenght of the string will be greater than the endidx.
        if(idxend < len(s.getText())):
            substr = s.getText()[idxend:len(s.getText())]
            m = re.search('([0-9]{1,2})', substr)
            if m is not None :
                day_val = m.group(0)
                day_startidx, day_endidx = getSpan(s.getText(), day_val)
                abs_Sspan = ref_Sspan + day_startidx
                abs_Espan = ref_Sspan + day_endidx
                
                my_day_entity = t6.T6DayOfMonthEntity(entityID=str(t6ID)+"entity", start_span=abs_Sspan, end_span=abs_Espan, value=day_val)
                t6List.append(my_day_entity)
                t6ID = t6ID+1
                #now link the month to the day
                my_month_entity.set_sub_interval(my_day_entity.get_id())
            #else test for a ordinal day of month
            else:
                texNumVal = utils.getNumberFromText(substr)
                
                if texNumVal is not None:
                    day_startidx, day_endidx = getSpan(s.getText(), substr)
                    abs_Sspan = ref_Sspan + day_startidx
                    abs_Espan = ref_Sspan + day_endidx
                    
                    my_day_entity = t6.T6DayOfMonthEntity(entityID=str(t6ID)+"entity", start_span=abs_Sspan, end_span=abs_Espan, value=texNumVal)
                    t6List.append(my_day_entity)
                    t6ID = t6ID+1
                    #now link the month to the day
                    my_month_entity.set_sub_interval(my_day_entity.get_id())
                
                
        t6List.append(my_month_entity)
    
        
    return t6List, t6ID
####
#END_MODULE
####
 
## buildAMPM(): Parses a sutime entity's text field to determine if it contains a AM or PM time indication, then builds the associated t6entity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @output t6List, t6ID Returns the expanded t6List and the incremented t6ID.
def buildAMPM(s, t6ID, t6List):
    
    ref_Sspan, ref_Espan = s.getSpan()
    ## Identify if a time zone string exists
    tz = hasTimeZone(s)
    if tz is not None:
        my_tz_entity = t6.T6TimeZoneEntity(str(t6ID)+"entity", start_span = tz.span(0)[0]+ref_Sspan, end_span=tz.span(0)[1]+ref_Sspan)
        t6List.append(my_tz_entity)
        t6ID = t6ID+1
    else:
        my_tz_entity = None
     
    boo, val, idxstart, idxend = hasAMPM(s)
    if boo:
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_AMPM_entity = t6.T6AMPMOfDayEntity(entityID=str(t6ID)+"entity", start_span=abs_Sspan, end_span=abs_Espan, ampm_type=val)
        t6ID = t6ID+1
        t6List.append(my_AMPM_entity)
        
        #check to see if it has a time associated with it.  We assume the time comes before the AMPM string
        #We could parse out the time from the sutime normalized value.  The problem is getting the correct span.
        #idx_start is the first index of the ampm.  If there are any characters before it, it will be greater than 0.
        if idxstart > 0:
            substr = s.getText()[0:idxstart]
            m = re.search('([0-9]{1,2})', substr)
            if m is not None :
                hour_val = m.group(0)
                abs_Sspan = ref_Sspan + m.span(0)[0]
                abs_Espan = ref_Sspan + m.span(0)[1]
            
                my_hour_entity = t6.T6HourOfDayEntity(entityID=str(t6ID)+"entity", start_span=abs_Sspan, end_span=abs_Espan, value=hour_val, ampm=my_AMPM_entity.get_id())
                 
                t6ID = t6ID+1
                 
                if my_tz_entity is not None:
                    my_hour_entity.set_time_zone(my_tz_entity.get_id())
            
                #add the hour entity to the list
                t6List.append(my_hour_entity)
            
            #else search for a text number
            else:
                texNumVal = utils.getNumberFromText(substr)
                
                if texNumVal is not None:
                    #create the hour entity
                    my_hour_entity = t6.T6HourOfDayEntity(entityID=str(t6ID)+"entity", start_span=ref_Sspan, end_span=ref_Sspan+(idxstart-1), value=texNumVal, ampm=my_AMPM_entity.get_id())
                    t6ID = t6ID+1
                    if my_tz_entity is not None:
                        my_hour_entity.set_time_zone(my_tz_entity.get_id())
                    #append to list
                    t6List.append(my_hour_entity) 
                         
    return t6List, t6ID
    
####
#END_MODULE
####

## buildCalendarInterval(): Parses a sutime entity's text field to determine if it contains a calendar interval phrase, then builds the associated t6entity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @output t6List, t6ID Returns the expanded t6List and the incremented t6ID.
###### ISSUES: This method assumes the number is immediatly before the interval type. There is some concern about if the spans are going to be correct.  I do test for numbers written out as words, but this assumes the entire beginning fo the string from sutime represents the number.  If this is not the case the spans may be off.
def buildCalendarInterval(s, t6ID, t6List):
    
    ref_Sspan, ref_Espan = s.getSpan()
    boo, val, idxstart, idxend, plural = hasCalendarInterval(s)
    if boo:
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_interval_entity = t6.T6CalendarIntervalEntity(entityID=str(t6ID)+"entity", start_span=abs_Sspan, end_span=abs_Espan, calendar_type=val)
        t6ID = t6ID+1
        
        #check to see if it has a number associated with it.  We assume the number comes before the interval string
        if idxstart > 0:
            substr = s.getText()[0:idxstart]
            m = re.search('([0-9]{1,2})', substr)
            if m is not None :
                num_val = m.group(0)
                abs_Sspan = ref_Sspan + m.span(0)[0]
                abs_Espan = ref_Sspan + m.span(0)[1]
            
                my_number_entity = t6.T6Number(entityID=str(t6ID)+"entity", start_span=abs_Sspan, end_span=abs_Espan, value=num_val)
                t6ID = t6ID+1
                
                #add the number entity to the list
                t6List.append(my_number_entity)
            #else search for a text number
            else:
                texNumVal = utils.getNumberFromText(substr)
                if texNumVal is not None:
                    #create the number entity
                    my_number_entity = t6.T6Number(entityID=str(t6ID)+"entity", start_span=ref_Sspan, end_span=ref_Sspan+(idxstart-1), value=texNumVal)
                    t6ID = t6ID+1
                    #append to list
                    t6List.append(my_number_entity)
                    #link to interval entity
                    my_interval_entity.set_number(my_number_entity.get_id())
                    
        
        t6List.append(my_interval_entity)             
            
    return t6List, t6ID
####
#END_MODULE
####

## buildPartOfDay(): Parses a sutime entity's text field to determine if it contains a part of the day expression, then builds the associated t6entity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @output t6List, t6ID Returns the expanded t6List and the incremented t6ID.
def buildPartOfDay(s, t6ID, t6List):
    
    boo, val, idxstart, idxend = hasPartOfDay(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = t6.T6PartOfDayEntity(entityID=str(t6ID)+"entity", start_span=abs_Sspan, end_span=abs_Espan, part_of_day_type=val)
        t6List.append(my_entity)
        t6ID = t6ID+1
        #check here to see if it has a modifier
        
    return t6List, t6ID
####
#END_MODULE
####    



############# Start hasX() Methods ##################


## hasDayOfWeek(): Takes in a single text string and identifies if it is a day of week
# @author Amy Olex
# @param text The text to be parsed
# @output value The normalized string value for the day of week, or None if no Day of week found.
# @ISSUE If there are multiple days of week in the temporal phrase it only captures one of them.
def hasDayOfWeek(suentity):
    
    #print("Before:" + text)
    #convert to all lower
    text_lower = suentity.getText().lower()
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", string.punctuation))
    #print("After:" + text_norm)
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my day lists
    M = ["monday","mon","m"]
    T = ["tuesday","tue","tues","t"]
    W = ["wednesday","wed","w"]
    TR = ["thursday","thur","tr","th"]
    F = ["friday","fri","f"]
    S = ["saturday","sat","s"]
    SU = ["sunday","sun","su"]
    days_of_week = M+T+W+TR+F+S+SU
    
    #figure out if any of the tokens in the text_list are also in the days of week list
    intersect = list(set(text_list) & set(days_of_week))
    
    #only proceed if the intersect list has a length of 1 or more.
    if len(intersect) >= 1 :
        #test if the intersect list contains which days.
        if len(list(set(intersect) & set (M))) == 1:
            day_text = list(set(intersect) & set (M))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Monday", start_idx, end_idx
            
            
        if len(list(set(intersect) & set (T))) == 1:
            day_text = list(set(intersect) & set (T))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)  
            return True, "Tuesday", start_idx, end_idx
            
        if len(list(set(intersect) & set (W))) == 1:
            day_text = list(set(intersect) & set (W))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Wednesday", start_idx, end_idx
            
        if len(list(set(intersect) & set (TR))) == 1:
            day_text = list(set(intersect) & set (TR))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Thursday", start_idx, end_idx
            
        if len(list(set(intersect) & set (F))) == 1:
            day_text = list(set(intersect) & set (F))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Friday", start_idx, end_idx
            
        if len(list(set(intersect) & set (S))) == 1:
            day_text = list(set(intersect) & set (S))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Saturday", start_idx, end_idx
            
        if len(list(set(intersect) & set (SU))) == 1:
            day_text = list(set(intersect) & set (SU))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Sunday", start_idx, end_idx
        else :
            return False, None, None, None
    else :
        return False, None, None, None
    
####
#END_MODULE
####

## hasModifier(): Takes in a single text string and identifies if it has any modufying phrases
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @output Outputs 4 values: Boolean Flag, Value text, start index, end index 
def hasModifier(suentity):
    
    #convert to all lower
    text_lower = suentity.getText().lower()
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", string.punctuation))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my day lists
    modifiers = ["this","next","last","a","each","between","from"]
    
    #figure out if any of the tokens in the text_list are also in the modifiers list
    intersect = list(set(text_list) & set(modifiers))
    
    #only proceed if the intersect list has a length of 1 or more.
    #I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1 :
        #test if the intersect list contains which days.
        if intersect[0] == "this":
            start_idx = text_norm.index("this")
            end_idx = start_idx + len("this")
            return True, "This", start_idx, end_idx
            
        if intersect[0] == "next":
            start_idx = text_norm.index("next")
            end_idx = start_idx + len("next")
            return True, "Next", start_idx, end_idx
            
        if intersect[0] == "last":
            start_idx = text_norm.index("last")
            end_idx = start_idx + len("last")
            return True, "Last", start_idx, end_idx
            
        if intersect[0] == "a":
            start_idx = text_norm.index("a")
            end_idx = start_idx + len("a")
            return True, "Period", start_idx, end_idx
         
        if intersect[0] == "each":
            start_idx = text_norm.index("each")
            end_idx = start_idx + len("each")
            return True, "Period", start_idx, end_idx
        
        if intersect[0] == "between":
            start_idx = text_norm.index("between")
            end_idx = start_idx + len("between")
            return True, "Period", start_idx, end_idx  
            
        if intersect[0] == "from":
            start_idx = text_norm.index("from")
            end_idx = start_idx + len("from")
            return True, "Period", start_idx, end_idx  
        else :
            return False, None, None, None
    else :
        return False, None, None, None
    
####
#END_MODULE
####




## hasTextMonth(): Takes in a single text string and identifies if it is a month of the year
# @author Amy Olex
# @param suentity The entity to parse
# @output value The normalized string value for the month of the year, or None if no month of year found.
# @ISSUE If there are multiple months of the year in the temporal phrase it only captures one of them.
def hasTextMonth(suentity):
    
    #convert to all lower
    text_lower = suentity.getText().lower()
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my day lists
    M1 = ["january","jan."]
    M2 = ["february","feb."]
    M3 = ["march","mar."]
    M4 = ["april","apr."]
    M5 = ["may"]
    M6 = ["june","jun."]
    M7 = ["july","jul."]
    M8 = ["august","aug."]
    M9 = ["september","sep.", "sept."]
    M10 = ["october","oct."]
    M11 = ["november","nov."]
    M12 = ["december","dec."]
    
    full_year = M1+M2+M3+M4+M5+M6+M7+M8+M9+M10+M11+M12
    
    
    #figure out if any of the tokens in the text_list are also in the months list
    intersect = list(set(text_list) & set(full_year))
    
    
    #only proceed if the intersect list has a length of 1 or more.
    if len(intersect) >= 1 :
        #test if the intersect list contains which days.
        if len(list(set(intersect) & set (M1))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M1))[0])
            return True, "January", start_idx, end_idx
        
        if len(list(set(intersect) & set (M2))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M2))[0])
            return True, "February", start_idx, end_idx
            
        if len(list(set(intersect) & set (M3))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M3))[0])
            return True, "March", start_idx, end_idx
            
        if len(list(set(intersect) & set (M4))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M4))[0])
            return True, "April", start_idx, end_idx
            
        if len(list(set(intersect) & set (M5))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M5))[0])
            return True, "May", start_idx, end_idx
            
        if len(list(set(intersect) & set (M6))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M6))[0])
            return True, "June", start_idx, end_idx
            
        if len(list(set(intersect) & set (M7))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M7))[0])
            return True, "July", start_idx, end_idx
            
        if len(list(set(intersect) & set (M8))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M8))[0])
            return True, "August", start_idx, end_idx
            
        if len(list(set(intersect) & set (M9))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M9))[0])
            return True, "September", start_idx, end_idx
            
        if len(list(set(intersect) & set (M10))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M10))[0])
            return True, "October", start_idx, end_idx
            
        if len(list(set(intersect) & set (M11))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M11))[0])
            return True, "November", start_idx, end_idx
            
        if len(list(set(intersect) & set (M12))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (M12))[0])
            return True, "December", start_idx, end_idx

        else :
            return False, None, None, None
    else :
        return False, None, None, None
    
####
#END_MODULE
####



## hasAMPM(): Takes in a single text string and identifies if it has any AM or PM phrases
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @output Outputs 4 values: Boolean Flag, Value text, start index, end index 
def hasAMPM(suentity):
    
    #convert to all lower
    #text_lower = suentity.getText().lower()
    text = suentity.getText()
    #remove all punctuation
    text_norm = text.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my day lists
    am = ["AM","am","A.M.","AM.","a.m.","am."]
    pm = ["PM","pm","P.M.","p.m.","pm.","PM."]
    
    ampm = am+pm
    
    #figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(ampm))
    
    #only proceed if the intersect list has a length of 1 or more.
    #I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1 :
        #test if the intersect list contains which days.
        if len(list(set(intersect) & set (am))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (am))[0])
            return True, "AM", start_idx, end_idx
            
        if len(list(set(intersect) & set (pm))) == 1:
            start_idx, end_idx = getSpan(text_norm, list(set(intersect) & set (pm))[0])
            return True, "PM", start_idx, end_idx
       
        else :
            return False, None, None, None
    else :
        return False, None, None, None
    
####
#END_MODULE
####

## hasTimeZone(): Takes in a single sutime entity and determines if it has a time zone specified in the text.
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @output Outputs the regex object or None 
def hasTimeZone(suentity):
    return re.search('(AST|EST|CST|MST|PST|AKST|HST|UTC-11|UTC+10)', suentity.getText())

####
#END_MODULE
####

## hasCalendarInterval(): Takes in a SUTime entity and identifies if it has any calendar interval phrases like "week" or "days"
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @output Outputs 5 values: Boolean Flag, Value text, start index, end index, pluralBoolean 
def hasCalendarInterval(suentity):
    
    #convert to all lower
    #text_lower = suentity.getText().lower()
    text = suentity.getText()
    #remove all punctuation
    text_norm = text.translate(str.maketrans("", "", string.punctuation))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my period lists
    singular = ["day","week","month","year","daily","weekly","monthly","yearly"]
    plural = ["days","weeks","months","years"]
    
    #figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(singular+plural))
    
    #only proceed if the intersect list has a length of 1 or more.
    #For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1 :
        #test if the intersect list contains plural or singular period.
        
        if len(list(set(intersect) & set (singular))) == 1:
            singTerm = list(set(intersect) & set (singular))[0]
            start_idx, end_idx = getSpan(text_norm, singTerm)
            if singTerm == "day" or singTerm == "daily":
                return True, "Day", start_idx, end_idx, False
            elif singTerm == "week" or singTerm == "weekly":
                return True, "Week", start_idx, end_idx, False
            elif singTerm == "month" or singTerm == "monthly":
                return True, "Month", start_idx, end_idx, False
            elif singTerm == "year" or singTerm == "yearly":
                return True, "Year", start_idx, end_idx, False
            
            
        if len(list(set(intersect) & set (plural))) == 1:
            plurTerm = list(set(intersect) & set (plural))[0]
            start_idx, end_idx = getSpan(text_norm, plurTerm)
            if plurTerm == "days":
                return True, "Days", start_idx, end_idx, True
            elif plurTerm == "weeks":
                return True, "Weeks", start_idx, end_idx, True
            elif plurTerm == "months":
                return True, "Months", start_idx, end_idx, True
            elif plurTerm == "years":
                return True, "Years", start_idx, end_idx, True
              
        else :
            return False, None, None, None, None
    else :
        return False, None, None, None, None
    
####
#END_MODULE
####


## hasPartOfDay(): Takes in a SUTime entity and identifies if it has any part of day terms, like "overnight" or "morning"
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @output Outputs 4 values: Boolean Flag, Value text, start index, end index
#############ISSUE: I've coded this to return the sub-span of the "value".  For example, the span returned for "overnight" is just for the "night" portion.  This seems to be how the gold standard xml does it, which I think is silly, but that is what it does.
def hasPartOfDay(suentity):
    
    #convert to all lower
    #text_lower = suentity.getText().lower()
    text = suentity.getText()
    #remove all punctuation
    text_norm = text.translate(str.maketrans("", "", string.punctuation))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my period lists
    partofday = ["morning","evening","afternoon","night","dawn","dusk","tonight","overnight","today","nights","mornings","evening","afternoons"]
    
    #figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(partofday))
    
    #only proceed if the intersect list has a length of 1 or more.
    #For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1 :
        
        term = intersect[0]
        start_idx, end_idx = getSpan(text_norm, term)
        if term == "morning" or term == "dawn" or term == "mornings":
            return True, "Morning", start_idx, end_idx
        elif term == "evening" or term == "dusk" or term == "evenings":
            return True, "Evening", start_idx, end_idx
        elif term == "afternoon" or term == "afternoons":
            return True, "Afternoon", start_idx, end_idx 
        elif term == "nights":
            return True, "Night", start_idx, end_idx  
        elif term == "night" or term == "overnight" or term == "tonight":
            m = re.search("night", text_norm)
            sidx = m.span(0)[0]
            eidx = m.span(0)[1]
            return True, "Night", sidx, eidx  
        elif term == "today":
            return True, "Day", start_idx, end_idx
        else :
            return False, None, None, None
    else :
        return False, None, None, None
    
####
#END_MODULE
####




## getSpan(): identifies the local span of the serach_text in the input "text"
# @author Amy Olex
# @param text The text to be searched
# @param search_text The text to search for.
# @output The start index and end index of the search_text string.
######## ISSUE: This needs to be re-named here and in all the above usages.  Probably should also move this to the utils class.  Dont delete the s.getSpan() as those are from the sutime entity class.
def getSpan(text, search_text):
    try:
        start_idx = text.index(search_text)
        end_idx = start_idx + len(search_text)
    except ValueError:
        return None, None
        
    return start_idx, end_idx
