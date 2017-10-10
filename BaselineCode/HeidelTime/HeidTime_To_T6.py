## Converts HeidTime Entites into T6 Entities
#
# Programmer Name: Nicholas Morton 
#
# Date: 10/10/2017

import t6Entities as t6
import calendar
import string
import re
import datetime

## Takes in list of Heidtime output and converts to T6Entity
# @author Nicholas Morton
# @param list of Heidtime Output
# @param document creation time (optional)
# @return List of T6 entities and the T6ID
def buildT6List(heidtimeList, t6ID , dct=None):
    t6List = []
    for s in heidtimeList :                 
        #Parse out Year function
        t6List, t6ID  = buildT6Year(s,t6ID,t6List)
        #Parse out Two-Digit Year 
        t6List, t6ID  = buildT62DigitYear(s,t6ID,t6List)
        #Parse out Month-of-Year
        t6List, t6ID  = buildT6MonthOfYear(s,t6ID,t6List)
        #Parse out Day-of-Month
        t6List, t6ID  = buildT6DayOfMonth(s,t6ID,t6List) 
        #Parse out HourOfDay
        t6List, t6ID  = buildT6HourOfDay(s,t6ID,t6List)
        #Parse out MinuteOfHour
        t6List, t6ID  = buildT6MinuteOfHour(s,t6ID,t6List)   
        #Parse out SecondOfMinute
        t6List, t6ID  = buildT6SecondOfMinute(s,t6ID,t6List)                            
        
    return t6List, t6ID    
####
#END_MODULE
####


#################### Start buildX() Methods #######################


## Takes in list of Heidtime output and converts to T6Entity
# @author Nicholas Morton
# @param s The heidtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @return t6List, t6ID Returns the expanded t6List and the incremented t6ID.
def buildT6Year(s, t6ID, t6List):

    b, text, startSpan, endSpan = hasYear(s)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        t6YearEntity = t6.T6YearEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=int(text))  
        t6List.append(t6YearEntity)
        t6ID =t6ID +1

        #Check for Month in same element
        bMonth, textMonth, startSpanMonth, endSpanMonth = hasMonthOfYear(s)
        if bMonth:
            abs_StartSpanMonth = ref_StartSpan + startSpanMonth
            abs_EndSpanMonth = abs_StartSpanMonth + abs(endSpanMonth - startSpanMonth) 
            t6MonthEntity = t6.T6MonthOfYearEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpanMonth, end_span=abs_EndSpanMonth, month_type=calendar.month_name[int(textMonth)])  
            t6List.append(t6MonthEntity)
            t6ID =t6ID +1
            t6YearEntity.set_sub_interval(t6MonthEntity.get_id())

            #Check for Day in same element
            bDay, textDay, startSpanDay, endSpanDay = hasDayOfMonth(s)
            if bDay:
                abs_StartSpanDay = ref_StartSpan + startSpanDay
                abs_EndSpanDay = abs_StartSpanDay + abs(endSpanDay-startSpanDay)
                t6DayEntity = t6.T6MinuteOfHourEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpanDay, end_span=abs_EndSpanDay, value=int(textDay))  
                t6List.append(t6DayEntity)
                t6ID =t6ID +1
                t6MonthEntity.set_sub_interval(t6DayEntity.get_id())

                #Check for Hour in same element
                bHour, textHour, startSpanHour, endSpanHour = hasHourOfDay(s)
                if bHour:
                    ref_StartSpan, ref_EndSpan = s.getSpan()
                    abs_StartSpanHour = ref_StartSpan + startSpanHour
                    abs_EndSpanHour = abs_StartSpanHour + abs(endSpanHour-startSpanHour)
                    t6HourEntity = t6.T6MinuteOfHourEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpanHour, end_span=abs_EndSpanHour, value=int(textHour))  
                    t6List.append(t6HourEntity)
                    t6ID =t6ID +1
                    t6DayEntity.set_sub_interval(t6HourEntity.get_id())

                    #Check for Minute in same element
                    bMinute, textMinute, startSpanMinute, endSpanMinute = hasMinuteOfHour(s)
                    if bMinute:
                        ref_StartSpan, ref_EndSpan = s.getSpan()
                        abs_StartSpanMinute = ref_StartSpan + startSpan
                        abs_EndSpanMinute = abs_StartSpanMinute + abs(endSpanMinute-startSpanMinute)
                        t6MinuteEntity = t6.T6MinuteOfHourEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpanMinute, end_span=abs_EndSpanMinute, value=int(textMinute))  
                        t6List.append(t6MinuteEntity)
                        t6ID =t6ID +1
                        t6HourEntity.set_sub_interval(t6MinuteEntity.get_id())
                        

                        #Check for Second in same element
                        bSecond, textSecond, startSpanSecond, endSpanSecond = hasSecondOfMinute(s)
                        if bSecond:
                            ref_StartSpan, ref_EndSpan = s.getSpan()
                            abs_StartSpanSecond = ref_StartSpan + startSpan
                            abs_EndSpanSecond = abs_StartSpanSecond + abs(endSpanSecond-startSpanSecond)
                            t6SecondEntity = t6.T6SecondOfMinuteEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpanSecond, end_span=abs_EndSpanSecond, value=int(textSecond))  
                            t6List.append(t6SecondEntity)
                            t6ID =t6ID +1
                            t6MinuteEntity.set_sub_interval(t6SecondEntity.get_id())                
    return t6List,t6ID
####
#END_MODULE
####

## Takes in list of Heidtime output and converts to T6Entity
# @author Nicholas Morton
# @param s The heidtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @return t6List, t6ID Returns the expanded t6List and the incremented t6ID.
def buildT62DigitYear(s, t6ID, t6List):           
    b, text, startSpan, endSpan = has2DigitYear(s)
    if b:
        #In most cases this will be at the end of the Span
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)          
        t62DigitYearEntity = t6.T6TwoDigitYearOperator(entityID=str(t6ID)+"entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=text, sub_interval = "None")  
        t6List.append(t62DigitYearEntity)
        t6ID =t6ID +1
        
        #Check for Month in same element
        bMonth, textMonth, startSpanMonth, endSpanMonth = hasMonthOfYear(s)
        if bMonth:
            abs_StartSpanMonth = ref_StartSpan + startSpanMonth
            abs_EndSpanMonth = abs_StartSpanMonth + abs(endSpanMonth - startSpanMonth) 
            t6MonthEntity = t6.T6MonthOfYearEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpanMonth, end_span=abs_EndSpanMonth, month_type=calendar.month_name[int(textMonth)])  
            t6List.append(t6MonthEntity)
            t6ID =t6ID +1
            t62DigitYearEntity.set_sub_interval(t6MonthEntity.get_id())

            #Check for Day in same element
            bDay, textDay, startSpanDay, endSpanDay = hasDayOfMonth(s)
            if bDay:
                abs_StartSpanDay = ref_StartSpan + startSpanDay
                abs_EndSpanDay = abs_StartSpanDay + abs(endSpanDay-startSpanDay)
                t6DayEntity = t6.T6MinuteOfHourEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpanDay, end_span=abs_EndSpanDay, value=int(textDay))  
                t6List.append(t6DayEntity)
                t6ID =t6ID +1
                t6MonthEntity.set_sub_interval(t6DayEntity.get_id())

                #Check for Hour in same element
                bHour, textHour, startSpanHour, endSpanHour = hasHourOfDay(s)
                if bHour:
                    ref_StartSpan, ref_EndSpan = s.getSpan()
                    abs_StartSpanHour = ref_StartSpan + startSpanHour
                    abs_EndSpanHour = abs_StartSpanHour + abs(endSpanHour-startSpanHour)
                    t6HourEntity = t6.T6MinuteOfHourEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpanHour, end_span=abs_EndSpanHour, value=int(textHour))  
                    t6List.append(t6HourEntity)
                    t6ID =t6ID +1
                    t6DayEntity.set_sub_interval(t6HourEntity.get_id())

                    #Check for Minute in same element
                    bMinute, textMinute, startSpanMinute, endSpanMinute = hasMinuteOfHour(s)
                    if bMinute:
                        ref_StartSpan, ref_EndSpan = s.getSpan()
                        abs_StartSpanMinute = ref_StartSpan + startSpan
                        abs_EndSpanMinute = abs_StartSpanMinute + abs(endSpanMinute-startSpanMinute)
                        t6MinuteEntity = t6.T6MinuteOfHourEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpanMinute, end_span=abs_EndSpanMinute, value=int(textMinute))  
                        t6List.append(t6MinuteEntity)
                        t6ID =t6ID +1
                        t6HourEntity.set_sub_interval(t6MinuteEntity.get_id())
                        

                        #Check for Second in same element
                        bSecond, textSecond, startSpanSecond, endSpanSecond = hasSecondOfMinute(s)
                        if bSecond:
                            ref_StartSpan, ref_EndSpan = s.getSpan()
                            abs_StartSpanSecond = ref_StartSpan + startSpan
                            abs_EndSpanSecond = abs_StartSpanSecond + abs(endSpanSecond-startSpanSecond)
                            t6SecondEntity = t6.T6SecondOfMinuteEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpanSecond, end_span=abs_EndSpanSecond, value=int(textSecond))  
                            t6List.append(t6SecondEntity)
                            t6ID =t6ID +1
                            t6MinuteEntity.set_sub_interval(t6SecondEntity.get_id())   
              
    return t6List,t6ID
####
#END_MODULE
####

## Takes in list of Heidtime output and converts to T6Entity
# @author Nicholas Morton
# @param s The heidtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @return t6List, t6ID Returns the expanded t6List and the incremented t6ID.
def buildT6MonthOfYear(s, t6ID, t6List):    
    b, text, startSpan, endSpan = hasMonthOfYear(s)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        t6Entity = t6.T6MonthOfYearEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpan, end_span=abs_EndSpan, month_type=calendar.month_name[int(text)])  
        t6List.append(t6Entity)
        t6ID =t6ID +1
                         
    return t6List, t6ID
####
#END_MODULE
####

## Takes in list of Heidtime output and converts to T6Entity
# @author Nicholas Morton
# @param s The heidtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @return t6List, t6ID Returns the expanded t6List and the incremented t6ID.
def buildT6DayOfMonth(s, t6ID, t6List):
    b, text, startSpan, endSpan = hasDayOfMonth(s)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        t6Entity = t6.T6DayOfMonthEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=int(text))  
        t6List.append(t6Entity)
        t6ID =t6ID +1
                          
    return t6List, t6ID
    
####
#END_MODULE
####

## Takes in list of Heidtime output and converts to T6Entity
# @author Nicholas Morton
# @param s The heidtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @return t6List, t6ID Returns the expanded t6List and the incremented t6ID.
def buildT6HourOfDay(s, t6ID, t6List):
    b, text, startSpan, endSpan = hasHourOfDay(s)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        t6Entity = t6.T6HourOfDayEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=int(text))  
        t6List.append(t6Entity)
        t6ID =t6ID +1
                          
    return t6List, t6ID
####
#END_MODULE
####

## Takes in list of Heidtime output and converts to T6Entity
# @author Nicholas Morton
# @param s The heidtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @return t6List, t6ID Returns the expanded t6List and the incremented t6ID.
def buildT6MinuteOfHour(s,t6ID, t6List):
    b, text, startSpan, endSpan = hasMinuteOfHour(s)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        t6Entity = t6.T6MinuteOfHourEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=int(text))  
        t6List.append(t6Entity)
        t6ID =t6ID +1
                         
    return t6List, t6ID
####
#END_MODULE
####

## Takes in list of Heidtime output and converts to T6Entity
# @author Nicholas Morton
# @param s The heidtime entity to parse 
# @param t6ID The current t6ID to increment as new t6entities are added to list.
# @param t6List The list of T6 objects we currently have.  Will add to these.
# @return t6List, t6ID Returns the expanded t6List and the incremented t6ID.
def buildT6SecondOfMinute(s,t6ID, t6List):
    b, text, startSpan, endSpan = hasSecondOfMinute(s)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        t6Entity = t6.T6SecondOfMinuteEntity(entityID=str(t6ID)+"entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=int(text))  
        t6List.append(t6Entity)
        t6ID =t6ID +1
                          
    return t6List, t6ID
####
#END_MODULE
####

############# Start hasX() Methods ##################

## Takes in a single text string and identifies if it has any 4 digit year phrases
# @author Nicholas Morton
# @param heidentity The heidtime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasYear(heidentity):
    
    text_lower = heidentity.getText().lower() 
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            #define regular expression to find a 4-digit year
            if(re.search('([0-9]{1,2})[-/:]([0-9]{1,2})[-/:]([0-9]{4})',text)):
                if  len(text.split("/")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile("/").split(text)[2])    
                    return True, re.compile("/").split(text)[2], start_idx, end_idx
                elif len(text.split("-")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile("-").split(text)[2])    
                    return True, re.compile("-").split(text)[2], start_idx, end_idx
                else:
                   return False, None, None, None

        return False, None, None, None #if no 4 digit year expressions were found return false            
    else:

        return False, None, None, None #if the text_list does not have any entries, return false

####
#END_MODULE
####

## Takes in a single text string and identifies if it has any 2 digit year phrases
# @author Nicholas Morton
# @param heidentity The heidtime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def has2DigitYear(heidentity):

    text_lower = heidentity.getText().lower() 
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            #define regular expression to find a 2-digit year
            if(re.search('([0-9]{1,2})[-/:]([0-9]{1,2})[-/:]([0-9]{2})',text)) and len(text)==8:
                #print(text)
                if  len(text.split("/")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile("/").split(text)[2])    
                    return True, re.compile("/").split(text)[2], start_idx, end_idx
                elif len(text.split("-")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile("-").split(text)[2])    
                    return True, re.compile("-").split(text)[2], start_idx, end_idx
                else:
                   return False, None, None, None

        return False, None, None, None #if no 2 digit year expressions were found return false            
    else:

        return False, None, None, None #if the text_list does not have any entries, return false

####
#END_MODULE
####

## Takes in a single text string and identifies if it has a month of year
# @author Nicholas Morton and Amy Olex
# @param heidentity The heidtime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasMonthOfYear(heidentity):

    text_lower = heidentity.getText().lower() 
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            #define regular expression to find a 2-digit month
            twodigitstart = re.search('(^[0-9]{1,2})[-/:]([0-9]{1,2})[-/:]([0-9]{2})',text)
            fourdigitstart = re.search('(^[0-9]{4})[-/:]([0-9]{1,2})[-/:]([0-9]{2})',text)
            splitText = "/"
            if "-" in text:
                splitText = "-"            
            if(fourdigitstart):
                #If start with 4 digits then assum the format yyyy/mm/dd                
                start_idx, end_idx = getSpan(text_norm,fourdigitstart.group(0).split(splitText)[1])
                return True, fourdigitstart.group(0).split(splitText)[1], start_idx, end_idx
            elif(twodigitstart):
                #If only starts with 2 digits assume the format mm/dd/yy or mm/dd/yyyy
                #Note for dates like 12/03/2012, the text 12/11/03 and 11/03/12 can't be disambiguated, so will return 12 as the month for the first and 11 as the month for the second.
                #check to see if the first two digits are less than or equal to 12.  If greater then we have the format yy/mm/dd
                #print(twodigitstart.group(0))
                if int(twodigitstart.group(0).split(splitText)[0]) <= 12:
                    # assume mm/dd/yy
                    start_idx, end_idx = getSpan(text_norm,twodigitstart.group(0).split(splitText)[0])
                    return True, twodigitstart.group(0).split(splitText)[0], start_idx, end_idx
                elif int(twodigitstart.group(0).split(splitText)[0]) > 12:
                    # assume yy/mm/dd
                    #print(twodigitstart.group(0)).split("/")[0]
                    start_idx, end_idx = getSpan(text_norm,twodigitstart.group(0).split(splitText)[1])
                    return True, twodigitstart.group(0).split(splitText)[1], start_idx, end_idx
                else:
                    return False, None, None, None

        return False, None, None, None #if no 2 digit month expressions were found return false            
    else:

        return False, None, None, None #if the text_list does not have any entries, return false

####
#END_MODULE
####

## Takes in a single text string and identifies if it has a day of the month in numeric format
# @author Nicholas Morton
# @param heidentity The heidtime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasDayOfMonth(heidentity):

    text_lower = heidentity.getText().lower() 
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            #define regular expression to find a 2-digit day
            if(re.search('([0-9]{1,2})[-/:]([0-9]{1,2})[-/:]([0-9]{2})',text)):
                #print(text)
                if  len(text.split("/")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile("/").split(text)[1])    
                    return True, re.compile("/").split(text)[1], start_idx, end_idx
                elif len(text.split("-")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile("-").split(text)[1])    
                    return True, re.compile("-").split(text)[1], start_idx, end_idx
                else:
                   return False, None, None, None

        return False, None, None, None #if no 2 digit day expressions were found return false            
    else:

        return False, None, None, None #if the text_list does not have any entries, return false

####
#END_MODULE
####

## Takes in a single text string and identifies if it has a hh:mm:ss
# @author Nicholas Morton
# @param heidentity The heidtime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasTimeString(heidentity):

    text_lower = heidentity.getText().lower() 
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            #define regular expression to find a numeric hour
            if(re.search('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$',text)):  #checks for HH:MM:SS String
                if len(text.split(":")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile(":").split(text)[0]) 
                    return True, text, start_idx, end_idx
                    
                else:
                    return False, None, None, None #if no 2 digit hour expressions were found return false            
                

        return False, None, None, None #if no 2 digit hour expressions were found return false            
    else:

        return False, None, None, None #if the text_list does not have any entries, return false

####
#END_MODULE
####

## Takes in a single text string and identifies if it has a hour of a day
# @author Nicholas Morton
# @param heidentity The heidtime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasHourOfDay(heidentity):

    text_lower = heidentity.getText().lower() 
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            #define regular expression to find a numeric hour
            if(re.search('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$',text)):  #checks for HH:MM:SS String
                if len(text.split(":")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile(":").split(text)[0]) 
                    return True, re.compile(":").split(text)[0], start_idx, end_idx                    
                else:
                    return False, None, None, None #if no 2 digit hour expressions were found return false  

        return False, None, None, None #if no 2 digit hour expressions were found return false            
    else:

        return False, None, None, None #if the text_list does not have any entries, return false

####
#END_MODULE
####

## Takes in a single text string and identifies if it has a minute of an hour
# @author Nicholas Morton
# @param heidentity The heidtime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasMinuteOfHour(heidentity):

    text_lower = heidentity.getText().lower() 
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            #define regular expression to find a 2-digit minute
            if(re.search('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$',text)):  #checks for HH:MM:SS String
                if len(text.split(":")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile(":").split(text)[1]) 
                    return True, re.compile(":").split(text)[1], start_idx, end_idx                    
                else:
                    return False, None, None, None #if no 2 digit hour expressions were found return false

        return False, None, None, None #if no 2 digit day expressions were found return false            
    else:

        return False, None, None, None #if the text_list does not have any entries, return false

####
#END_MODULE
####

## Takes in a single text string and identifies if it has a second of an minute
# @author Nicholas Morton
# @param heidentity The heidtime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasSecondOfMinute(heidentity):

    text_lower = heidentity.getText().lower() 
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            #define regular expression to find a 2-digit minute
            if(re.search('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$',text)):  #checks for HH:MM:SS String
                if len(text.split(":")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile(":").split(text)[2]) 
                    return True, re.compile(":").split(text)[2], start_idx, end_idx                    
                else:
                    return False, None, None, None #if no 2 digit hour expressions were found return false

        return False, None, None, None #if no 2 digit day expressions were found return false            
    else:

        return False, None, None, None #if the text_list does not have any entries, return false

####
#END_MODULE
####

## Identifies the local span of the serach_text in the input "text"
# @author Amy Olex
# @param text The text to be searched
# @param search_text The text to search for.
# @return The start index and end index of the search_text string.
######## ISSUE: This needs to be re-named here and in all the above usages.  Probably should also move this to the utils class.  Dont delete the s.getSpan() as those are from the heidtime entity class.
def getSpan(text, search_text):
    try:
        start_idx = text.index(search_text)
        end_idx = start_idx + len(search_text)
    except ValueError:
        return None, None
        
    return start_idx, end_idx
