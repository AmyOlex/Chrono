###############################
# Programmer Name: Nicholas Morton
# Date: 9/28/17
# Module Purpose: Converts SUTime Entites into T6 Entities
#################################

from task6 import t6Entities as t6
import calendar
import string

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
def buildT6List(suTimeList, dct=None):
    t6list = []
    for s in suTimeList : 
        #Split each entity into seperate chunks for evaluation
        #eid = s.split()[0]
        #etext = s.split()[1]
        #espan = s.split()[2]
        #eBeginSpan = epsan.split(",")[0].strip("<") #not sure if this is the best way, gonna write a function soon
        #eEndSpan = epspan.split(",")[1].strip(">")
        #etype = s.split()[3]
        #evalue = s.split()[4]
        
        if "DATE" in s.getType():  #parse out Year, Two-Digit Year, Month-of-Year, and Day-of-month
            #Parse out Year function
            t6list.append(buildT6Year(s))
            #Parse out Two-Digit Year (if applicable) #taking out for now until I figure out what I want to do
            #t6list.append(buildT62DigitYear(s))
            #Parse out Month-of-Year
            t6list.append(buildT6MonthOfYear(s))
            #Parse out Day-of-Month
            t6list.append(buildT6DayOfMonth(s))
            
        if "TIME" in s.getType(): #parse out all of Date data as well as Hour-of-Day, Minute-of-Hour, and Second-of-Minute  
            #Parse out Year function
            t6list.append(buildT6Year(s))
            #Parse out Two-Digit Year (if applicable) #taking out for now until I figure out what I want to do
            #t6list.append(buildT62DigitYear(s))
            #Parse out Month-of-Year
            t6list.append(buildT6MonthOfYear(s))
            #Parse out Day-of-Month
            t6list.append(buildT6DayOfMonth(s))  

            #Going to rewrite this function to be a little cleaner soon, just getting my ideas out          
            #Parse out HourOfDay
            t6list.append(buildT6HourOfDay(s))
            #Parse out MinuteOfHour
            t6list.append(buildT6MinuteOfHour(s))    
            #Parse out SecondOfMinute
            t6list.append(buildT6SecondOfMinute(s))

    return t6list
####
#END_MODULE
####

## buildT6Year(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime 
# @output T6Year Entity
def buildT6Year(s):
    t6YearEntity = t6.T6YearEntity(s.id,s.start_span,s.end_span-6,s.suvalue.split("-")[0])  #not sure if this is the best way to do this, it had the format it yyyy-mm-dd
    return t6YearEntity
####
#END_MODULE
####

## buildT62DigitYear(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime 
# @output T6Year Entity
def buildT62DigitYear(s): #need to work on this one...
    t6YearEntity = t6.T6YearEntity(s.id,s.start_span,s.end_span-6,s.suvalue.split("-")[0])  #not sure if this is the best way to do this, it had the format it yyyy-mm-dd
    return t6YearEntity
####
#END_MODULE
####

## buildT6MonthOfYear(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime 
# @output T6MonthOfYear Entity
def buildT6MonthOfYear(s):
    #basing this off of the yyyy-mm-dd format of the value, might need to revisit later
    suval_split = s.suvalue.split("-")
    if len(suval_split) == 3 :
        month = calendar.month_name[int(suval_split[1])] #should be a valid month number (1-12)
        t6MonthOfYear = t6.T6MonthOfYearEntity(s.id,s.start_span + 5,s.end_span - 3,month) #might need to pull the proper spans from the reference tokens, this seems inadequete  
    else :
        t6MonthOfYear = None
        
    return t6MonthOfYear
####
#END_MODULE
####

## buildT6MonthOfYear(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime 
# @output T6DayOfMonthEntity
def buildT6DayOfMonth(s):
    #basing this off of the yyyy-mm-dd format of the value, might need to revisit later
    suval_split = s.suvalue.split("-")
    if len(suval_split) == 3 :
        t6DayOfMonth = t6.T6DayOfMonthEntity(s.id,s.start_span + 8,s.end_span,suval_split[2]) #might need to pull the proper spans from the reference tokens
        return t6DayOfMonth
    else :
        return None
    
####
#END_MODULE
####

## buildT6HourOfDay(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime Entity
# @output T6HourOfDay Entity
def buildT6HourOfDay(s):
    sTime = s.suvalue.split("T")[1] #left with 17:00-0500
    sHour = sTime.split(":")[0]
    sSet = "AM"
    if int(sHour) > 12: 
        sHour=int(sHour)-12
        sSet = "PM"

    t6HourOfDay = t6.T6HourOfDayEntity(s.id,s.start_span+10,s.end_span-8,sHour,sSet)  #might need to pull the proper spans from the reference tokens, also need to pull time zone from text maybe?
    return t6HourOfDay
####
#END_MODULE
####

## buildT6MinuteOfHour(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime Entity
# @output T6MinuteOfHour Entity
def buildT6MinuteOfHour(s):
    sTime = s.suvalue.split("T")[1] #left with 17:00-0500
    sMinute = sTime.split("-")[0]
    sMinute = sMinute.split(":")[1] #should be a valid number between 00-59
    t6MinuteOfHour = t6.T6MinuteOfHourEntity(s.id,s.start_span+14,s.end_span-6,sMinute)  #might need to pull the proper spans from the reference tokens
    return t6MinuteOfHour
####
#END_MODULE
####

## buildT6SecondOfMinute(): Takes in list of SUTime output and converts to T6Entity
# @author Nicholas Morton
# @param SUTime Entity
# @output T6HourOfDay Entity
def buildT6SecondOfMinute(s):
    sTime = s.suvalue.split("T")[1] #left with 17:00-0500
    sSecond="00"

    if sTime.count(":") > 1: #Time string like 17:00:00
        sMinute = sTime.split("-")[0]
        sSecond = sMinute.split(":")[2]
    t6SecondOfMinute = t6.T6SecondOfMinuteEntity(s.id,s.start_span+14,s.end_span-6,sSecond)  #might need to pull the proper spans from the reference tokens/not sure what we should do if there are no seconds defined...
    return t6SecondOfMinute
####
#END_MODULE
####

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
