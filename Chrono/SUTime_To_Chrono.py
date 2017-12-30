## Converts SUTime Entites into Chrono Entities
#
# Programmer Name: Nicholas Morton
#
# Date: 9/28/17

import calendar
import datetime
import re
import string


import numpy as np

from nltk.tokenize import WhitespaceTokenizer
from chronoML import ChronoKeras
from Chrono import referenceToken
from Chrono import chronoEntities as chrono
from Chrono import utils


#Example SUTime List
#Wsj_0152
#0 11/02/89 <12,20> DATE 1989-11-02
#1 Nov. 9 11/02/89 <145,160> DATE 1989-11-02
#2 5 p.m. EST Nov. 9 <393,410> TIME 2017-11-09T17:00-0500
#3 Nov. 6 <536,542> DATE 2017-11-06

## Takes in list of SUTime output and converts to ChronoEntity
# @author Nicholas Morton
# @param list of SUTime Output
# @param document creation time (optional)
# @return List of Chrono entities and the ChronoID
def buildChronoList(suTimeList, chrono_id, ref_list, PIclassifier, PIfeatures, dct=None):
    chrono_list = []
    
    ## Do some further pre-processing on the ref token list
    ## Replace all punctuation with spaces
    ref_list = referenceToken.replacePunctuation(ref_list)
    ## Convert to lowercase
    ref_list = referenceToken.lowercase(ref_list)
    
    for s in suTimeList :
        #print(s)
        chrono_tmp_list = []
        chrono_minute_flag = False
        chrono_second_flag = False
        loneDigitYearFlag = False
        #Parse out Year function
        chrono_tmp_list, chrono_id, chrono_minute_flag, chrono_second_flag  = buildChronoYear(s, chrono_id, chrono_tmp_list, chrono_minute_flag, chrono_second_flag, loneDigitYearFlag)
        #Parse out Two-Digit Year 
        chrono_tmp_list, chrono_id, chrono_minute_flag, chrono_second_flag  = buildChrono2DigitYear(s, chrono_id, chrono_tmp_list, chrono_minute_flag, chrono_second_flag)
        #Parse out Month-of-Year
        chrono_tmp_list, chrono_id  = buildChronoMonthOfYear(s, chrono_id, chrono_tmp_list)
        #Parse out Day-of-Month
        chrono_tmp_list, chrono_id  = buildChronoDayOfMonth(s, chrono_id, chrono_tmp_list)
        #Parse out HourOfDay
        chrono_tmp_list, chrono_id  = buildChronoHourOfDay(s, chrono_id, chrono_tmp_list)
        #Parse out MinuteOfHour
        chrono_tmp_list, chrono_id  = buildChronoMinuteOfHour(s, chrono_id, chrono_tmp_list, chrono_minute_flag)
        #Parse out SecondOfMinute
        chrono_tmp_list, chrono_id  = buildChronoSecondOfMinute(s, chrono_id, chrono_tmp_list, chrono_second_flag)

        chrono_tmp_list, chrono_id  = build24HourTime(s, chrono_id, chrono_tmp_list, loneDigitYearFlag)

        #call non-standard formatting temporal phrases, 
        chrono_tmp_list, chrono_id  = buildDayOfWeek(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id  = buildTextMonthAndDay(s, chrono_id, chrono_tmp_list, dct)
        chrono_tmp_list, chrono_id  = buildAMPM(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id  = buildPartOfDay(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id  = buildPartOfWeek(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id  = buildSeasonOfYear(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id  = buildPeriodInterval(s, chrono_id, chrono_tmp_list, ref_list, PIclassifier, PIfeatures)
     
        
        
        chrono_list += buildChronoSubIntervals(chrono_tmp_list)
        
        #Going to incorporate in future builds
        #chrono_list, chrono_id = buildDuration(s, chrono_id, chrono_list)
        #chrono_list, chrono_id = buildSet(s, chrono_id, chrono_list)
      
    return chrono_list, chrono_id
    
####
#END_MODULE
####


## Takes in list of ChronoEntities and identifies sub-intervals within the list
# @author Amy Olex
# @param list of ChronoEntities
# @return List of ChronoEntities with sub-intervals assigned
def buildChronoSubIntervals(chrono_list):
    year = None
    month = None
    day = None
    hour = None
    minute = None
    second = None
    
    ## loop through all entities and pull out the approriate IDs
    for e in chrono_list:
        e_type = e.get_type()
        
        if e_type == "Two-Digit-Year" or e_type == "Year":
            year = e
        elif e_type == "Month-Of-Year":
            month = e
        elif e_type == "Day-Of-Month":
            day = e
        elif e_type == "Hour-Of-Day":
            hour = e
        elif e_type == "Minute-Of-Hour":
            minute = e
        elif e_type == "Second-Of-Minute":
            second = e
        
    ## Now assign all sub-intervals
    if second is not None and minute is not None:
        minute.set_sub_interval(second.get_id())
    if minute is not None and hour is not None:
        hour.set_sub_interval(minute.get_id())
    if hour is not None and day is not None:
        day.set_sub_interval(hour.get_id())
    if day is not None and month is not None:
        month.set_sub_interval(day.get_id())
    if month is not None and year is not None:
        year.set_sub_interval(month.get_id())
    
    return chrono_list

####
#END_MODULE
####

#################### Start buildX() Methods #######################


## Takes in list of SUTime output and converts to ChronoEntity
# @author Nicholas Morton
# @param s The sutime entity to parse 
# @param chrono_id The current chrono_id to increment as new chronoEntities are added to list.
# @param chrono_list The list of Chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildChronoYear(s, chrono_id, chrono_list, chrono_minute_flag, chrono_second_flag, lone_digit_year_flag):

    b, text, startSpan, endSpan, lone_digit_year_flag = hasYear(s, lone_digit_year_flag)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        chrono_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=int(text))
        chrono_id = chrono_id + 1

        #Check for Month in same element
        bMonth, textMonth, startSpanMonth, endSpanMonth = hasMonthOfYear(s)
        if bMonth:
            abs_StartSpanMonth = ref_StartSpan + startSpanMonth
            abs_EndSpanMonth = abs_StartSpanMonth + abs(endSpanMonth - startSpanMonth)
            if(int(textMonth) <= 12):
                chrono_month_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpanMonth, end_span=abs_EndSpanMonth, month_type=calendar.month_name[int(textMonth)])
                chrono_id = chrono_id + 1
                chrono_year_entity.set_sub_interval(chrono_month_entity.get_id())

            #Check for Day in same element
            bDay, textDay, startSpanDay, endSpanDay = hasDayOfMonth(s)
            if bDay:
                abs_StartSpanDay = ref_StartSpan + startSpanDay
                abs_EndSpanDay = abs_StartSpanDay + abs(endSpanDay-startSpanDay)
                if(int(textDay) <= 31):
                    chrono_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpanDay, end_span=abs_EndSpanDay, value=int(textDay))
                    chrono_id = chrono_id + 1
                    chrono_month_entity.set_sub_interval(chrono_day_entity.get_id())

                #Check for Hour in same element
                bHour, textHour, startSpanHour, endSpanHour = hasHourOfDay(s)
                if bHour:
                    ref_StartSpan, ref_EndSpan = s.getSpan()
                    abs_StartSpanHour = ref_StartSpan + startSpanHour
                    abs_EndSpanHour = abs_StartSpanHour + abs(endSpanHour-startSpanHour)
                    if(int(textHour) <= 24):
                        chrono_hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpanHour, end_span=abs_EndSpanHour, value=int(textHour))
                        chrono_id = chrono_id + 1
                        chrono_day_entity.set_sub_interval(chrono_hour_entity.get_id())

                    #Check for Minute in same element
                    bMinute, textMinute, startSpanMinute, endSpanMinute = hasMinuteOfHour(s)
                    if bMinute and not chrono_minute_flag:
                        chrono_minute_flag=True
                        ref_StartSpan, ref_EndSpan = s.getSpan()
                        abs_StartSpanMinute = ref_StartSpan + startSpanMinute
                        abs_EndSpanMinute = abs_StartSpanMinute + abs(endSpanMinute-startSpanMinute)
                        if(int(textMinute) <= 60):
                            chrono_minute_entity = chrono.ChronoMinuteOfHourEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpanMinute, end_span=abs_EndSpanMinute, value=int(textMinute))
                            chrono_id = chrono_id + 1
                            chrono_hour_entity.set_sub_interval(chrono_minute_entity.get_id())
                        

                        #Check for Second in same element
                        bSecond, textSecond, startSpanSecond, endSpanSecond = hasSecondOfMinute(s)
                        if bSecond and not chrono_second_flag:
                            chrono_second_flag=True
                            ref_StartSpan, ref_EndSpan = s.getSpan()
                            abs_StartSpanSecond = ref_StartSpan + startSpanSecond
                            abs_EndSpanSecond = abs_StartSpanSecond + abs(endSpanSecond-startSpanSecond)
                            if(int(textSecond) <= 60):
                                chrono_second_entity = chrono.ChronoSecondOfMinuteEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpanSecond, end_span=abs_EndSpanSecond, value=int(textSecond))
                                chrono_list.append(chrono_second_entity)
                                chrono_id = chrono_id + 1
                                chrono_minute_entity.set_sub_interval(chrono_second_entity.get_id())
                        
                        chrono_list.append(chrono_minute_entity)
                    
                    chrono_list.append(chrono_hour_entity)
                    
                chrono_list.append(chrono_day_entity)
               
            chrono_list.append(chrono_month_entity)
            
        chrono_list.append(chrono_year_entity)
        
        
    return chrono_list, chrono_id, chrono_minute_flag, chrono_second_flag
####
#END_MODULE
####

## Takes in list of SUTime output and converts to ChronoEntity
# @author Nicholas Morton
# @param s The sutime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildChrono2DigitYear(s, chrono_id, chrono_list, chrono_minute_flag, chrono_second_flag):
    b, text, startSpan, endSpan = has2DigitYear(s)
    if b:
        #In most cases this will be at the end of the Span
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        chrono_2_digit_year_entity = chrono.ChronoTwoDigitYearOperator(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=text)
        chrono_id = chrono_id + 1
        
        #Check for Month in same element
        bMonth, textMonth, startSpanMonth, endSpanMonth = hasMonthOfYear(s)
        if bMonth:
            abs_StartSpanMonth = ref_StartSpan + startSpanMonth
            abs_EndSpanMonth = abs_StartSpanMonth + abs(endSpanMonth - startSpanMonth)
            if(int(textMonth) <= 12):
                chrono_month_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpanMonth, end_span=abs_EndSpanMonth, month_type=calendar.month_name[int(textMonth)])
                chrono_id = chrono_id + 1
                chrono_2_digit_year_entity.set_sub_interval(chrono_month_entity.get_id())

            #Check for Day in same element
            bDay, textDay, startSpanDay, endSpanDay = hasDayOfMonth(s)
            if bDay:
                abs_StartSpanDay = ref_StartSpan + startSpanDay
                abs_EndSpanDay = abs_StartSpanDay + abs(endSpanDay-startSpanDay)
                if(int(textDay) <= 31):
                    chrono_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpanDay, end_span=abs_EndSpanDay, value=int(textDay))
                    chrono_id = chrono_id + 1
                    chrono_month_entity.set_sub_interval(chrono_day_entity.get_id())

                #Check for Hour in same element
                bHour, textHour, startSpanHour, endSpanHour = hasHourOfDay(s)
                if bHour:
                    ref_StartSpan, ref_EndSpan = s.getSpan()
                    abs_StartSpanHour = ref_StartSpan + startSpanHour
                    abs_EndSpanHour = abs_StartSpanHour + abs(endSpanHour-startSpanHour)
                    if(int(textHour) <= 24):
                        chrono_hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpanHour, end_span=abs_EndSpanHour, value=int(textHour))
                        chrono_id = chrono_id + 1
                        chrono_day_entity.set_sub_interval(chrono_hour_entity.get_id())

                    #Check for Minute in same element
                    bMinute, textMinute, startSpanMinute, endSpanMinute = hasMinuteOfHour(s)
                    if bMinute and not chrono_minute_flag:
                        chrono_minute_flag=True
                        ref_StartSpan, ref_EndSpan = s.getSpan()
                        abs_StartSpanMinute = ref_StartSpan + startSpanMinute
                        abs_EndSpanMinute = abs_StartSpanMinute + abs(endSpanMinute-startSpanMinute)
                        if(int(textMinute) <= 60):
                            chrono_minute_entity = chrono.ChronoMinuteOfHourEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpanMinute, end_span=abs_EndSpanMinute, value=int(textMinute))
                            chrono_id = chrono_id + 1
                            chrono_hour_entity.set_sub_interval(chrono_minute_entity.get_id())
                        

                        #Check for Second in same element
                        bSecond, textSecond, startSpanSecond, endSpanSecond = hasSecondOfMinute(s)
                        if bSecond and not chrono_second_flag:
                            chrono_second_flag=True
                            ref_StartSpan, ref_EndSpan = s.getSpan()
                            abs_StartSpanSecond = ref_StartSpan + startSpanSecond
                            abs_EndSpanSecond = abs_StartSpanSecond + abs(endSpanSecond-startSpanSecond)
                            if(int(textSecond) <= 60):
                                chrono_second_entity = chrono.ChronoSecondOfMinuteEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpanSecond, end_span=abs_EndSpanSecond, value=int(textSecond))
                                chrono_list.append(chrono_second_entity)
                                chrono_id = chrono_id + 1
                                chrono_minute_entity.set_sub_interval(chrono_second_entity.get_id())
    
                        chrono_list.append(chrono_minute_entity)
                    
                    chrono_list.append(chrono_hour_entity)
                    
                chrono_list.append(chrono_day_entity)
               
            chrono_list.append(            chrono_month_entity)
            
        chrono_list.append(        chrono_2_digit_year_entity)

              
    return chrono_list, chrono_id, chrono_minute_flag, chrono_second_flag
####
#END_MODULE
####

## Takes in list of SUTime output and converts to chronoEntity
# @author Nicholas Morton
# @param s The sutime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildChronoMonthOfYear(s, chrono_id, chrono_list):
    b, text, startSpan, endSpan = hasMonthOfYear(s)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        if(int(text) <= 12):
            chrono_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan, end_span=abs_EndSpan, month_type=calendar.month_name[int(text)])
            chrono_list.append(chrono_entity)
            chrono_id = chrono_id + 1
                         
    return chrono_list, chrono_id
####
#END_MODULE
####

## Takes in list of SUTime output and converts to chronoEntity
# @author Nicholas Morton
# @param s The sutime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildChronoDayOfMonth(s, chrono_id, chrono_list):
    b, text, startSpan, endSpan = hasDayOfMonth(s)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        if(int(text) <= 31):
            chrono_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=int(text))
            chrono_list.append(chrono_entity)
            chrono_id = chrono_id + 1
                          
    return chrono_list, chrono_id
    
####
#END_MODULE
####

## Takes in list of SUTime output and converts to chronoEntity
# @author Nicholas Morton
# @param s The sutime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildChronoHourOfDay(s, chrono_id, chrono_list):
    b, text, startSpan, endSpan = hasHourOfDay(s)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        chrono_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=int(text))
        chrono_list.append(chrono_entity)
        chrono_id = chrono_id + 1
                          
    return chrono_list, chrono_id
####
#END_MODULE
####

## Takes in list of SUTime output and converts to chronoEntity
# @author Nicholas Morton
# @param s The sutime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildChronoMinuteOfHour(s, chrono_id, chrono_list, chrono_minute_flag):
    b, text, startSpan, endSpan = hasMinuteOfHour(s)
    
    if b and not chrono_minute_flag:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        chrono_entity = chrono.ChronoMinuteOfHourEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=int(text))
        chrono_list.append(chrono_entity)
        chrono_id = chrono_id + 1
                         
    return chrono_list, chrono_id
####
#END_MODULE
####

## Takes in list of SUTime output and converts to chronoEntity
# @author Nicholas Morton
# @param s The sutime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildChronoSecondOfMinute(s, chrono_id, chrono_list, chrono_second_flag):
    b, text, startSpan, endSpan = hasSecondOfMinute(s)
    if b and not chrono_second_flag:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan-startSpan)
        chrono_entity = chrono.ChronoSecondOfMinuteEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan, end_span=abs_EndSpan, value=int(text))
        chrono_list.append(chrono_entity)
        chrono_id = chrono_id + 1
                          
    return chrono_list, chrono_id
####
#END_MODULE
####


## Parses a sutime entity's text field to determine if it contains a day of the week written out in text form, then builds the associated chronoentity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildDayOfWeek(s, chrono_id, chrono_list):
    
    boo, val, idxstart, idxend = hasDayOfWeek(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoDayOfWeekEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, day_type=val)
        chrono_list.append(my_entity)
        chrono_id = chrono_id + 1
        #check here to see if it has a modifier
        hasMod, mod_type, mod_start, mod_end = hasModifier(s)
        if(hasMod):
            if mod_type == "This":
                chrono_list.append(chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1
                
            if mod_type == "Next":
                chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1
                
            if mod_type == "Last":
                chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1
            else:
                chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1
                
        else:
            chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
            chrono_id = chrono_id + 1
    
        
    return chrono_list, chrono_id
####
#END_MODULE
#### 

## Parses a sutime entity's text field to determine if it contains a season of the year written out in text form, then builds the associated chronoentity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildSeasonOfYear(s, chrono_id, chrono_list):
    
    boo, val, idxstart, idxend = hasSeasonOfYear(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoSeasonOfYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, season_type=val)
        
        #check here to see if it has a modifier
        hasMod, mod_type, mod_start, mod_end = hasModifier(s)
        if(hasMod):
            if mod_type == "This":
                chrono_list.append(chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1
                
            if mod_type == "Next":
                chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1
                
            if mod_type == "Last":
                chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1
            else:
                chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1
                
       # else:
    #        chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
     #       chrono_id = chrono_id+1
    
        #check to see if it has a number associated with it.  We assume the number comes before the interval string
        if idxstart > 0:
            substr = s.getText()[0:idxstart]
            m = re.search('([0-9]{1,2})', substr)
            if m is not None :
                num_val = m.group(0)
                abs_Sspan = ref_Sspan + m.span(0)[0]
                abs_Espan = ref_Sspan + m.span(0)[1]
        
                my_number_entity = chrono.ChronoNumber(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num_val)
                chrono_id = chrono_id + 1
            
                #add the number entity to the list
                chrono_list.append(my_number_entity)
                my_entity.set_number(my_number_entity.get_id())
                #else search for a text number
            else:
                texNumVal = utils.getNumberFromText(substr)
                if texNumVal is not None:
                    #create the number entity
                    my_number_entity = chrono.ChronoNumber(entityID=str(chrono_id) + "entity", start_span=ref_Sspan, end_span=ref_Sspan + (idxstart - 1), value=texNumVal)
                    chrono_id = chrono_id + 1
                    #append to list
                    chrono_list.append(my_number_entity)
                    #link to interval entity
                    my_entity.set_number(my_number_entity.get_id())
    
            chrono_list.append(my_entity)
            chrono_id = chrono_id + 1
            
    return chrono_list, chrono_id
####
#END_MODULE
####    

## Parses a sutime entity's text field to determine if it contains a month of the year, written out in text form, followed by a day, then builds the associated chronoentity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
# ISSUE: This method assumes the day appears after the month, but that may not always be the case as in "sixth of November"
def buildTextMonthAndDay(s, chrono_id, chrono_list, dct=None):
    boo, val, idxstart, idxend = hasTextMonth(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_month_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, month_type=val)
        chrono_id = chrono_id + 1
        
        ## assume all numbers 1-31 are days
        ## assume all numbers >1000 are years
        ## parse all text before month
            ## test to see if all text is a number or text year
            ## if no:
              ## remove all punctuation
              ## seperate by spaces
              ## parse each token, if find a number then assign to day or year as appropriate
            ## if yes:
              ## assign to day or year as appropriate
              
        ## parse all text after month
          ## test to see if all text is a number or text year
          ## if no:
            ## remove all punctuation
            ## seperate by spaces
            ## parse each token, if find a number then assign to day or year as appropriate
          ## if yes:
            ## assign to day or year as appropriate

        #idx_end is the last index of the month.  If there are any characters after it the length of the string will be greater than the endidx.
        if(idxend < len(s.getText())):
            substr = s.getText()[idxend:len(s.getText())]

            num = utils.getNumberFromText(substr)
            if num is not None:
                if num <= 31:
                    day_startidx, day_endidx = getSpan(s.getText(), substr)
                    abs_Sspan = ref_Sspan + day_startidx
                    abs_Espan = ref_Sspan + day_endidx
                    my_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num)
                    chrono_list.append(my_day_entity)
                    chrono_id = chrono_id + 1
                    
                    #now figure out if it is a NEXT or LAST
                    #create doctime
                    if dct is not None:
                        mStart = my_month_entity.get_start_span()
                        mEnd = my_month_entity.get_end_span()
                        this_dct = datetime.datetime(int(dct.year),int(utils.getMonthNumber(my_month_entity.get_month_type())), int(my_day_entity.get_value()), 0, 0)
                        if this_dct > dct:
                            chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                            chrono_id = chrono_id + 1
                        elif this_dct < dct:
                            chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                            chrono_id = chrono_id + 1
                #elif num >=1000:
                    ##add as year
            else:
                ##parse and process each token
                ##replace punctuation 
                substr = substr.translate(str.maketrans("", "", string.punctuation))
                ##split on spaces
                tokenized_text = WhitespaceTokenizer().tokenize(substr)
                for i in range(0,len(tokenized_text)):
                    num = utils.getNumberFromText(tokenized_text[i])
                    if num is not None:
                        if num <= 31:
                            day_startidx, day_endidx = getSpan(s.getText(), tokenized_text[i])
                            abs_Sspan = ref_Sspan + day_startidx
                            abs_Espan = ref_Sspan + day_endidx
                            my_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num)
                            chrono_list.append(my_day_entity)
                            chrono_id = chrono_id + 1
                            
                            #now figure out if it is a NEXT or LAST
                            #create doctime
                            if dct is not None:
                                mStart = my_month_entity.get_start_span()
                                mEnd = my_month_entity.get_end_span()
                                this_dct = datetime.datetime(int(dct.year),int(utils.getMonthNumber(my_month_entity.get_month_type())), int(my_day_entity.get_value()), 0, 0)
                                if this_dct > dct:
                                    chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                                    chrono_id = chrono_id + 1
                                elif this_dct < dct:
                                    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                                    chrono_id = chrono_id + 1
                        #elif num >=1000:
                            ##add as year
                    
                
        
                
                
                      
        chrono_list.append(my_month_entity)
    
        
    return chrono_list, chrono_id
####
#END_MODULE
####
 
## Parses a sutime entity's text field to determine if it contains a AM or PM time indication, then builds the associated chronoentity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildAMPM(s, chrono_id, chrono_list):
    
    ref_Sspan, ref_Espan = s.getSpan()
    ## Identify if a time zone string exists
    tz = hasTimeZone(s)
    if tz is not None:
        my_tz_entity = chrono.ChronoTimeZoneEntity(str(chrono_id) + "entity", start_span =tz.span(0)[0] + ref_Sspan, end_span=tz.span(0)[1] + ref_Sspan)
        chrono_list.append(my_tz_entity)
        chrono_id = chrono_id + 1
    else:
        my_tz_entity = None
     
    boo, val, idxstart, idxend = hasAMPM(s)
    if boo:
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_AMPM_entity = chrono.ChronoAMPMOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, ampm_type=val)
        chrono_id = chrono_id + 1
        chrono_list.append(my_AMPM_entity)
        
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
            
                my_hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=hour_val, ampm=my_AMPM_entity.get_id())
                 
                chrono_id = chrono_id + 1
                 
                if my_tz_entity is not None:
                    my_hour_entity.set_time_zone(my_tz_entity.get_id())
            
                #add the hour entity to the list
                chrono_list.append(my_hour_entity)
            
            #else search for a text number
            else:
                texNumVal = utils.getNumberFromText(substr)
                
                if texNumVal is not None:
                    #create the hour entity
                    my_hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan, end_span=ref_Sspan + (idxstart - 1), value=texNumVal, ampm=my_AMPM_entity.get_id())
                    chrono_id = chrono_id + 1
                    if my_tz_entity is not None:
                        my_hour_entity.set_time_zone(my_tz_entity.get_id())
                    #append to list
                    chrono_list.append(my_hour_entity)
                         
    return chrono_list, chrono_id
    
####
#END_MODULE
####


## Parses a sutime entity's text field to determine if it contains a calendar interval or period phrase, then builds the associated chronoentity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
###### ISSUES: This method assumes the number is immediatly before the interval type. There is some concern about if the spans are going to be correct.  I do test for numbers written out as words, but this assumes the entire beginning of the string from sutime represents the number.  If this is not the case the spans may be off.
###### More Issues: I created the training data incorrectly to remove the SUTime entity from consideration.  In order to classify from scratch we would need multiple classes: period, interval, everything else.  I only have a binary classifier here, so I need to narrow it down before trying to classify.
def buildPeriodInterval(s, chrono_id, chrono_list, ref_list, classifier, feats):
    
    features = feats.copy()
    ref_Sspan, ref_Espan = s.getSpan()
    #print("SUTime Text: " + s.getText())
    boo, val, idxstart, idxend, plural = hasCalendarInterval(s)
    if boo:
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        
        # get index of overlapping reference token
        ref_idx = -1
        for i in range(0,len(ref_list)):
            if(utils.overlap(ref_list[i].getSpan(),(abs_Sspan,abs_Espan))):
                ref_idx = i
                break
        
        # extract ML features
        my_features = utils.extract_prediction_features(ref_list, ref_idx, feats.copy())
        # classify into period or interval
        if(classifier[1] == "NN"):
            my_class = ChronoKeras.keras_classify(classifier[0], np.array(list(my_features.values())))
            #print("Class: " + str(my_class) + " : Start: " + str(abs_Sspan) + " : End: "+ str(abs_Espan))
        else:
            my_class = classifier[0].classify(my_features)
            #print("Class: " + str(my_class) + " : Start: " + str(abs_Sspan) + " : End: "+ str(abs_Espan))
            
            
            
        # if 1 then it is a period, if 0 then it is an interval  
        if(my_class == 1):
            my_entity = chrono.ChronoPeriodEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, period_type=getPeriodValue(val), number=None)
            chrono_id = chrono_id + 1
        else:
            my_entity = chrono.ChronoCalendarIntervalEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, calendar_type=val, number=None)
            chrono_id = chrono_id + 1
        
        #check to see if it has a number associated with it.  We assume the number comes before the interval string
        if idxstart > 0:
            substr = s.getText()[0:idxstart]
            m = re.search('([0-9]{1,2})', substr)
            if m is not None :
                num_val = m.group(0)
                abs_Sspan = ref_Sspan + m.span(0)[0]
                abs_Espan = ref_Sspan + m.span(0)[1]
            
                my_number_entity = chrono.ChronoNumber(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num_val)
                chrono_id = chrono_id + 1
                
                #add the number entity to the list
                chrono_list.append(my_number_entity)
                my_entity.set_number(my_number_entity.get_id())
            #else search for a text number
            else:
                texNumVal = utils.getNumberFromText(substr)
                if texNumVal is not None:
                    #create the number entity
                    my_number_entity = chrono.ChronoNumber(entityID=str(chrono_id) + "entity", start_span=ref_Sspan, end_span=ref_Sspan + (idxstart - 1), value=texNumVal)
                    chrono_id = chrono_id + 1
                    #append to list
                    chrono_list.append(my_number_entity)
                    #link to interval entity
                    my_entity.set_number(my_number_entity.get_id())
                    
        chrono_list.append(my_entity)
    
    else:
        boo2, val, idxstart, idxend, numstr = hasEmbeddedPeriodInterval(s)
        if(boo2):
            abs_Sspan = ref_Sspan + idxstart
            abs_Espan = ref_Sspan + idxend
        
            # get index of overlapping reference token
            ref_idx = -1
            for i in range(0,len(ref_list)):
                if(utils.overlap(ref_list[i].getSpan(),(abs_Sspan,abs_Espan))):
                    ref_idx = i
                    break
        
            # extract ML features
            my_features = utils.extract_prediction_features(ref_list, ref_idx, features)
        
            # classify into period or interval
            if(classifier[1] == "NN"):
                my_class = ChronoKeras.keras_classify(classifier[0], np.array(list(my_features.values())))
                #print("Class: " + str(my_class) + " : Start: " + str(abs_Sspan) + " : End: "+ str(abs_Espan))
            else:
                my_class = classifier[0].classify(my_features)
                #print("Class: " + str(my_class) + " : Start: " + str(abs_Sspan) + " : End: "+ str(abs_Espan))
            
             # if 1 then it is a period, if 0 then it is an interval  
            if(my_class == 1):
                my_entity = chrono.ChronoPeriodEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, period_type=getPeriodValue(val), number=None)
                chrono_id = chrono_id + 1
            else:
                my_entity = chrono.ChronoCalendarIntervalEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, calendar_type=val)
                chrono_id = chrono_id + 1
        
            #Extract the number and idetify the span of numstr
            
            substr = s.getText()[:idxstart] ## extract entire first part of SUTime phrase
            m = re.search('([0-9]{1,2})', substr) #search for an integer in the subphrase and extract it's coordinates
            if m is not None :
                num_val = m.group(0)
                abs_Sspan = ref_Sspan + m.span(0)[0]
                abs_Espan = ref_Sspan + m.span(0)[1]
            
                my_number_entity = chrono.ChronoNumber(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num_val)
                chrono_id = chrono_id + 1
                
                #add the number entity to the list
                chrono_list.append(my_number_entity)
                #link to interval entity
                my_entity.set_number(my_number_entity.get_id())
            #else search for a text number
            else:
                texNumVal = utils.getNumberFromText(numstr)
                if texNumVal is not None:
                    m = re.search(numstr, substr) #search for the number string in the subphrase
                    if m is not None :
                        abs_Sspan = ref_Sspan + m.span(0)[0]
                        abs_Espan = ref_Sspan + m.span(0)[1]
                        #create the number entity
                        my_number_entity = chrono.ChronoNumber(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=texNumVal)
                        chrono_id = chrono_id + 1
                        #append to list
                        chrono_list.append(my_number_entity)
                        #link to interval entity
                        my_entity.set_number(my_number_entity.get_id())
                    
            chrono_list.append(my_entity)
    
            
    return chrono_list, chrono_id
####
#END_MODULE
####

## Parses a sutime entity's text field to determine if it contains a part of the day expression, then builds the associated chronoentity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildPartOfDay(s, chrono_id, chrono_list):
    
    boo, val, idxstart, idxend = hasPartOfDay(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoPartOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, part_of_day_type=val)
        chrono_list.append(my_entity)
        chrono_id = chrono_id + 1
        #check here to see if it has a modifier
        
    return chrono_list, chrono_id
####
#END_MODULE
####    

## Parses a sutime entity's text field to determine if it contains a part of the week expression, then builds the associated chronoentity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildPartOfWeek(s, chrono_id, chrono_list):
    
    boo, val, idxstart, idxend = hasPartOfWeek(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoPartOfWeekEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, part_of_week_type=val)
        chrono_list.append(my_entity)
        chrono_id = chrono_id + 1
        #check here to see if it has a modifier
        
    return chrono_list, chrono_id
####
#END_MODULE
#### 

## Parses a sutime entity's text field to determine if it contains a 24-hour time expression, then builds the associated chronoentity list
# @author Amy Olex
# @param s The SUtime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def build24HourTime(s, chrono_id, chrono_list, lone_digit_year_flag):
    
    boo, val, idxstart, idxend = has24HourTime(s, lone_digit_year_flag)
    ref_Sspan, ref_Espan = s.getSpan()
    if boo and not lone_digit_year_flag:
        ## assume format of hhmm or hhmmzzz
        #print("24HourTime Text: " + val)
        hour = int(val[:2])
        minute = int(val[2:])
        #print("24HourTime Minute:" + str(minute))
        
        #search for time zone
        ## Identify if a time zone string exists
        tz = hasTimeZone(s)
        if tz is not None:
            my_tz_entity = chrono.ChronoTimeZoneEntity(str(chrono_id) + "entity", start_span =tz.span(0)[0] + ref_Sspan, end_span=tz.span(0)[1] + ref_Sspan)
            chrono_list.append(my_tz_entity)
            chrono_id = chrono_id + 1
        else:
            my_tz_entity = None
        
        ## build minute entity
        min_entity = chrono.ChronoMinuteOfHourEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan + idxstart + 3, end_span=ref_Sspan + idxend, value=minute)
        #print("Minute Value Added: " + str(min_entity.get_value()))
        chrono_list.append(min_entity)
        chrono_id = chrono_id + 1
        
        if my_tz_entity is not None:
            hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan + idxstart + 3, end_span=ref_Sspan + idxstart + 2, value=hour, time_zone=my_tz_entity.get_id())
        else:
            hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan + idxstart + 3, end_span=ref_Sspan + idxstart + 2, value=hour)
            
        hour_entity.set_sub_interval(min_entity.get_id())
        chrono_list.append(hour_entity)
        chrono_id = chrono_id + 1

 
    return chrono_list, chrono_id
####
#END_MODULE
#### 


## Parses a sutime entity's text field to determine if it contains a part of the day expression, then builds the associated chronoentity list
# @author Nicholas Morton
# @param s The SUtime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return SUTime Duration Entity
def buildDuration(s, chrono_id, chrono_list): 

    #if hasExactDuration(s):  #3 days -> P3D

    #if hasInExactDuration(s): #a few years -> PXY

    #if hasDurationRange(s): #2 to 3 months -> P2M/P3M

    return chrono_list, chrono_id
 
####
#END_MODULE
#### 

## Parses a sutime entity's text field to determine if it contains a part of the day expression, then builds the associated chronoentity list
# @author Nicholas Morton
# @param s The SUtime entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return SUTime Set Entity
def buildSet(s, chrono_id, chrono_list):

    return chrono_list, chrono_id


####
#END_MODULE
#### 


############# Start hasX() Methods ##################


## Takes in a single text string and identifies if it is a day of week
# @author Amy Olex
# @param text The text to be parsed
# @return value The normalized string value for the day of week, or None if no Day of week found.
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

## Takes in a single text string and identifies if it has any modufying phrases
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
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




## Takes in a single text string and identifies if it is a month of the year
# @author Amy Olex
# @param suentity The entity to parse
# @return value The normalized string value for the month of the year, or None if no month of year found.
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



## Takes in a single text string and identifies if it has any AM or PM phrases
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
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

## Takes in a single sutime entity and determines if it has a time zone specified in the text.
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @return Outputs the regex object or None
def hasTimeZone(suentity):
    return re.search('(AST|EST|EDT|CST|MST|PST|AKST|HST|UTC-11|UTC+10)', suentity.getText())

####
#END_MODULE
####

## Takes in a SUTime entity and identifies if it has any calendar interval phrases like "week" or "days"
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @return Outputs 5 values: Boolean Flag, Value text, start index, end index, pluralBoolean
def hasCalendarInterval(suentity):
    
    #convert to all lower
    #text_lower = suentity.getText().lower()
    text = suentity.getText()
    #remove all punctuation
    text_norm = text.translate(str.maketrans("", "", string.punctuation))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my period lists
    terms = ["decades","decade","yesterday","day","week","month","year","daily","weekly","monthly","yearly","century","minute","second","hour","hourly","days","weeks","months","years","centuries", "minutes","seconds","hours"]
    
    #figure out if any of the tokens in the text_list are also in the interval list
    intersect = list(set(text_list) & set(terms))
    
    #only proceed if the intersect list has a length of 1 or more.
    #For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1 :
        #test if the intersect list contains plural or singular period.
        
        if len(list(set(intersect) & set (terms))) == 1:
            this_term = list(set(intersect) & set (terms))[0]
            start_idx, end_idx = getSpan(text_norm, this_term)
            if this_term == "day" or this_term == "daily" or this_term == "days" or this_term == "yesterday":
                return True, "Day", start_idx, end_idx, False
            elif this_term == "week" or this_term == "weekly" or this_term == "weeks":
                return True, "Week", start_idx, end_idx, False
            elif this_term == "month" or this_term == "monthly" or this_term == "months":
                return True, "Month", start_idx, end_idx, False
            elif this_term == "year" or this_term == "yearly" or this_term == "years":
                return True, "Year", start_idx, end_idx, False
            elif this_term == "century" or this_term == "centuries":
                return True, "Century", start_idx, end_idx, False
            elif this_term == "decade" or this_term == "decades":
                return True, "Decade", start_idx, end_idx, False
            elif this_term == "minute" or this_term == "minutes":
                return True, "Minute", start_idx, end_idx, False
            elif this_term == "second" or this_term == "seconds":
                return True, "Second", start_idx, end_idx, False
            elif this_term == "hour" or this_term == "hourly" or this_term == "hours":
                return True, "Hour", start_idx, end_idx, False
              
        else :
            return False, None, None, None, None
    else :          
        return False, None, None, None, None
    
####
#END_MODULE
####

## Takes in a SUTime entity and identifies if it has any calendar interval phrases like "week" or "days"
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @return Outputs 5 values: Boolean Flag, Value text, start index, end index, numeric string
# Note: this should be called after everything else is checked.  The numeric string will need to have it's span and value identified by the calling method.
def hasEmbeddedPeriodInterval(suentity):
    
    #convert to all lower
    #text_lower = suentity.getText().lower()
    text = suentity.getText()
    #remove all punctuation
    text_norm = text.translate(str.maketrans("", "", string.punctuation))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my period/interval term lists
    terms = ["decades","decade","today","yesterday","day","week","month","year","daily","weekly","monthly","yearly","century","minute","second","hour","hourly","days","weeks","months","years","centuries", "minutes","seconds","hours"]
    
    ## if the term does not exist by itself it may be a substring. Go through each word in the SUTime string and see if a substring matches.
    for t in text_list:
        for r in terms:
            ## see if r is a substring of t
            ## if yes and the substring is at the end, extract the first substring and test to see if it is a number.
            idx = t.find(r)
            if(idx > 0):
                # then the r term is not the first substring.  Extract and test.
                sub1 = t[:idx]
                sub2 = t[idx:]
                # sub1 should be a number
                if(isinstance(utils.getNumberFromText(sub1), (int))):
                    # if it is a number then test to figure out what sub2 is.
                    this_term = sub2
                    start_idx, end_idx = getSpan(text_norm, this_term)
                    if this_term == "day" or this_term == "daily" or this_term == "days" or this_term == "yesterday":
                        return True, "Day", start_idx, end_idx, sub1
                    elif this_term == "week" or this_term == "weekly" or this_term == "weeks":
                        return True, "Week", start_idx, end_idx, sub1
                    elif this_term == "month" or this_term == "monthly" or this_term == "months":
                        return True, "Month", start_idx, end_idx, sub1
                    elif this_term == "year" or this_term == "yearly" or this_term == "years":
                        return True, "Year", start_idx, end_idx, sub1
                    elif this_term == "century" or this_term == "centuries":
                        return True, "Century", start_idx, end_idx, sub1
                    elif this_term == "decade" or this_term == "decades":
                        return True, "Decade", start_idx, end_idx, sub1
                    elif this_term == "minute" or this_term == "minutes":
                        return True, "Minute", start_idx, end_idx, sub1
                    elif this_term == "second" or this_term == "seconds":
                        return True, "Second", start_idx, end_idx, sub1
                    elif this_term == "hour" or this_term == "hourly" or this_term == "hours":
                        return True, "Hour", start_idx, end_idx, sub1
                else :
                    return False, None, None, None, None
    return False, None, None, None, None
####
#END_MODULE
####

## Takes in a string that is a Calendar-Interval value and returns the associated Period value
# @author Amy Olex
# @param val The Calendar-Interval string
# @return The Period value string
def getPeriodValue(val):
    if val == "Day":
        return("Days")
    elif val == "Week":
        return("Weeks")
    elif val == "Month":
        return("Months")
    elif val == "Year":
        return("Years")
    elif val == "Century":
        return("Centuries")
    elif val == "Decade":
        return("Decades")
    elif val == "Hour":
        return("Hours")
    elif val == "Minute":
        return("Minutes")
    elif val == "Second":
        return("Seconds")
    else:
        return(val)


## Takes in a SUTime entity and identifies if it has any part of day terms, like "overnight" or "morning"
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
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
    partofday = ["morning","evening","afternoon","night","dawn","dusk","tonight","overnight","nights","mornings","evening","afternoons","noon"]
    
    #figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(partofday))
    
    #only proceed if the intersect list has a length of 1 or more.
    #For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1 :
        
        term = intersect[0]
        start_idx, end_idx = getSpan(text_norm, term)
        if term == "morning" or term == "mornings":
            return True, "Morning", start_idx, end_idx
        if term == "dawn":
            return True, "Dawn", start_idx, end_idx
        elif term == "evening" or term == "dusk" or term == "evenings":
            return True, "Evening", start_idx, end_idx
        elif term == "afternoon" or term == "afternoons":
            return True, "Afternoon", start_idx, end_idx 
        elif term == "nights":
            return True, "Night", start_idx, end_idx
        elif term == "noon":
            return True, "Noon", start_idx, end_idx  
        elif term == "night" or term == "overnight" or term == "tonight":
            m = re.search("night", text_norm)
            sidx = m.span(0)[0]
            eidx = m.span(0)[1]
            return True, "Night", sidx, eidx  
        else :
            return False, None, None, None
    else :
        return False, None, None, None
    
####
#END_MODULE
####

## Takes in a SUTime entity and identifies if it has any season terms, like "summer" or "fall"
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasSeasonOfYear(suentity):
    
    #convert to all lower
    #text_lower = suentity.getText().lower()
    text = suentity.getText()
    #remove all punctuation
    text_norm = text.translate(str.maketrans("", "", string.punctuation))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my period lists
    seasonofyear = ["summer", "winter", "fall", "spring"]
    
    #figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(seasonofyear))
    
    #only proceed if the intersect list has a length of 1 or more.
    #For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1 :
        
        term = intersect[0]
        start_idx, end_idx = getSpan(text_norm, term)
        if term == "summer":
            return True, "Summer", start_idx, end_idx
        if term == "winter":
            return True, "Winter", start_idx, end_idx
        elif term == "fall":
            return True, "Fall", start_idx, end_idx
        elif term == "spring":
            return True, "Spring", start_idx, end_idx   
        else :
            return False, None, None, None
    else :
        return False, None, None, None
    
####
#END_MODULE
####

## Takes in a SUTime entity and identifies if it has any part of week terms, like "weekend"
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
#############ISSUE: I've coded this to return the sub-span of the "value".  For example, the span returned for "overnight" is just for the "night" portion.  This seems to be how the gold standard xml does it, which I think is silly, but that is what it does.
def hasPartOfWeek(suentity):
    
    #convert to all lower
    #text_lower = suentity.getText().lower()
    text = suentity.getText()
    #remove all punctuation
    text_norm = text.translate(str.maketrans("", "", string.punctuation))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my period lists
    partofday = ["weekend", "weekends"]
    
    #figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(partofday))
    
    #only proceed if the intersect list has a length of 1 or more.
    #For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1 :
        
        term = intersect[0]
        start_idx, end_idx = getSpan(text_norm, term)
        if term == "weekend" or term == "weekends":
            return True, "Weekend", start_idx, end_idx
        else :
            return False, None, None, None
    else :
        return False, None, None, None
    
####
#END_MODULE
####

## Takes in a single text string and identifies if it has any 4 digit 24-hour time phrases
# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
# Note: This need to be called after it has checked for years
def has24HourTime(suentity, loneDigitYearFlag):
    
    text_lower = suentity.getText().lower() 
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0 and not loneDigitYearFlag:
        #loop through list looking for expression
        for text in text_list:
            if len(text) == 4:
                num = utils.getNumberFromText(text)
                if num is not None:
                    hour = utils.getNumberFromText(text[:2])
                    minute = utils.getNumberFromText(text[2:])
                    if (hour is not None) and (minute is not None):
                        if (minute > 60) or (hour > 24):
                            return False, None, None, None
                        else:
                            start_idx, end_idx = getSpan(text_norm, text)    
                            return True, text, start_idx, end_idx


        return False, None, None, None #if no 4 digit year expressions were found return false            
    else:
        return False, None, None, None #if the text_list does not have any entries, return false


## Takes in a single text string and identifies if it has any 4 digit year phrases
# @author Nicholas Morton
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasYear(suentity, loneDigitYearFlag):
    
    text_lower = suentity.getText().lower() 
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            #print(text + " " + str(len(text)))
            #define regular expression to find a 4-digit year from the date format
            if(re.search('([0-9]{1,2})[-/:]([0-9]{1,2})[-/:]([0-9]{4})',text)):
                if  len(text.split("/")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile("/").split(text)[2])    
                    return True, re.compile("/").split(text)[2], start_idx, end_idx, loneDigitYearFlag
                elif len(text.split("-")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile("-").split(text)[2])    
                    return True, re.compile("-").split(text)[2], start_idx, end_idx, loneDigitYearFlag
                else:
                   return False, None, None, None, loneDigitYearFlag
            ## look for year at start of date
            ## added by Amy Olex
            elif(re.search('([0-9]{4})[-/:]([0-9]{1,2})[-/:]([0-9]{1,2})',text)):
                if  len(text.split("/")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile("/").split(text)[0])    
                    return True, re.compile("/").split(text)[0], start_idx, end_idx, loneDigitYearFlag
                elif len(text.split("-")) == 3:
                    start_idx, end_idx = getSpan(text_norm,re.compile("-").split(text)[0])    
                    return True, re.compile("-").split(text)[0], start_idx, end_idx, loneDigitYearFlag
                else:
                   return False, None, None, None, loneDigitYearFlag
            ## if no date format, see if there is a 4 digit number and assume it is a year if between 1800 and 2050
            ## Added by Amy Olex
            elif len(text) == 4:
                num = utils.getNumberFromText(text)
                if num is not None:
                    if  (num >= 1800) and (num <= 2050):
                        start_idx, end_idx = getSpan(text_norm, text)
                        loneDigitYearFlag = True    
                        return True, num, start_idx, end_idx, loneDigitYearFlag
                    else:
                       return False, None, None, None, loneDigitYearFlag
            ## parse out the condesnsed date format like 19980303.  Assumes the format yyyymmdd.  SUTime currently doesn't recognize this format.
            elif len(text) == 8:
                num = utils.getNumberFromText(text[0:4])
                if num is not None:
                    if  (num >= 1800) and (num <= 2050):
                        start_idx, end_idx = getSpan(text_norm, text)    
                        return True, num, start_idx, end_idx, loneDigitYearFlag
                    else:
                       return False, None, None, None, loneDigitYearFlag

        return False, None, None, None, loneDigitYearFlag #if no 4 digit year expressions were found return false            
    else:

        return False, None, None, None, loneDigitYearFlag #if the text_list does not have any entries, return false

####
#END_MODULE
####

## Takes in a single text string and identifies if it has any 2 digit year phrases
# @author Nicholas Morton
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def has2DigitYear(suentity):

    text_lower = suentity.getText().lower() 
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
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasMonthOfYear(suentity):

    text_lower = suentity.getText().lower() 
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
            
            if(fourdigitstart):
                #If start with 4 digits then assum the format yyyy/mm/dd
                start_idx, end_idx = getSpan(text_norm,fourdigitstart[2])
                return True, fourdigitstart[2], start_idx, end_idx
            elif(twodigitstart):
                #If only starts with 2 digits assume the format mm/dd/yy or mm/dd/yyyy
                #Note for dates like 12/03/2012, the text 12/11/03 and 11/03/12 can't be disambiguated, so will return 12 as the month for the first and 11 as the month for the second.
                #check to see if the first two digits are less than or equal to 12.  If greater then we have the format yy/mm/dd
                if int(twodigitstart[1]) <= 12:
                    # assume mm/dd/yy
                    start_idx, end_idx = getSpan(text_norm,twodigitstart[1])
                    return True, twodigitstart[1], start_idx, end_idx
                elif int(twodigitstart[1]) > 12:
                    # assume yy/mm/dd
                    start_idx, end_idx = getSpan(text_norm,twodigitstart[2])
                    return True, twodigitstart[2], start_idx, end_idx
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
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasDayOfMonth(suentity):

    text_lower = suentity.getText().lower() 
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
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasTimeString(suentity):

    text_lower = suentity.getText().lower() 
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
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasHourOfDay(suentity):

    text_lower = suentity.getText().lower() 
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
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasMinuteOfHour(suentity):

    text_lower = suentity.getText().lower() 
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
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasSecondOfMinute(suentity):

    text_lower = suentity.getText().lower() 
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

# @author Amy Olex
# @param suentity The SUTime entity object being parsed
# @return Outputs 4 values: Boolean Flag
def hasExactDuration(suentity):
    
    if "P#D":
        return True    
    else:
        return False

####
#END_MODULE
####


## Identifies the local span of the serach_text in the input "text"
# @author Amy Olex
# @param text The text to be searched
# @param search_text The text to search for.
# @return The start index and end index of the search_text string.
######## ISSUE: This needs to be re-named here and in all the above usages.  Probably should also move this to the utils class.  Dont delete the s.getSpan() as those are from the sutime entity class.
def getSpan(text, search_text):
    try:
        start_idx = text.index(search_text)
        end_idx = start_idx + len(search_text)
    except ValueError:
        return None, None
        
    return start_idx, end_idx
