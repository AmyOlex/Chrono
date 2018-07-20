# Copyright (c) 2018 
# Amy L. Olex, Virginia Commonwealth University
# alolex at vcu.edu
#
# Luke Maffey, Virginia Commonwealth University
# maffeyl at vcu.edu
#
# Nicholas Morton,  Virginia Commonwealth University 
# nmorton at vcu.edu
#
# Bridget T. McInnes, Virginia Commonwealth University
# btmcinnes at vcu.edu
#
# This file is part of Chrono
#
# Chrono is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Chrono is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Chrono; if not, write to 
#
# The Free Software Foundation, Inc., 
# 59 Temple Place - Suite 330, 
# Boston, MA  02111-1307, USA.



## Converts temporal phrases into Chrono Entities


import calendar
import datetime
import re
import string


import numpy as np

from nltk.tokenize import WhitespaceTokenizer

from Chrono.TimePhraseToChrono import *
from chronoML import ChronoKeras
from Chrono import referenceToken
from Chrono import chronoEntities as chrono
from Chrono import utils
from Chrono import w2ny as w2n


#Example TimePhrase List
#Wsj_0152
#0 11/02/89 <12,20> DATE 1989-11-02
#1 Nov. 9 11/02/89 <145,160> DATE 1989-11-02
#2 5 p.m. EST Nov. 9 <393,410> TIME 2017-11-09T17:00-0500
#3 Nov. 6 <536,542> DATE 2017-11-06

## Takes in list of TimePhrase output and converts to ChronoEntity
# @author Nicholas Morton
# @param list of TimePhrase Output
# @param document creation time (optional)
# @return List of Chrono entities and the ChronoID
def buildChronoList(TimePhraseList, chrono_id, ref_list, PIclassifier, PIfeatures, dct=None):
    chrono_list = []
    
    ## Do some further pre-processing on the ref token list
    ## Replace all punctuation with spaces
    ref_list = referenceToken.replacePunctuation(ref_list)
    ## Convert to lowercase
    ref_list = referenceToken.lowercase(ref_list)
    
    for s in TimePhraseList:
        print(s)
        chrono_tmp_list = []
        
        # this is the new chrono time flags so we don't duplicate effort.  Will ned to eventually re-write this flow.
        # The flags are in the order: [loneDigitYear, month, day, hour, minute, second]
        chrono_time_flags = {"loneDigitYear":False, "month":False, "day":False, "hour":False, "minute":False, "second":False, "fourdigityear":False}

        #Parse out Year function
        chrono_tmp_list, chrono_id, chrono_time_flags = MonthYear.buildYear(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        #Parse out Two-Digit Year 
        chrono_tmp_list, chrono_id, chrono_time_flags = MonthYear.build2DigitYear(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        #Parse out Month-of-Year
        chrono_tmp_list, chrono_id, chrono_time_flags = MonthYear.buildMonthOfYear(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        #Parse out Day-of-Month
        chrono_tmp_list, chrono_id, chrono_time_flags = buildDayOfMonth(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        #Parse out HourOfDay
        chrono_tmp_list, chrono_id, chrono_time_flags = buildHourOfDay(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        #Parse out MinuteOfHour
        chrono_tmp_list, chrono_id, chrono_time_flags = buildMinuteOfHour(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        #Parse out SecondOfMinute
        chrono_tmp_list, chrono_id, chrono_time_flags = buildSecondOfMinute(s, chrono_id, chrono_tmp_list, chrono_time_flags)

        
        #Parse modifier text
        chrono_tmp_list, chrono_id = buildModifierText(s, chrono_id, chrono_tmp_list)

        #call non-standard formatting temporal phrases
        chrono_tmp_list, chrono_id, chrono_time_flags = NumericDate.buildNumericDate(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        chrono_tmp_list, chrono_id, chrono_time_flags = build24HourTime(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        
        chrono_tmp_list, chrono_id = buildDayOfWeek(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id, chrono_time_flags = buildTextMonthAndDay(s, chrono_id, chrono_tmp_list, chrono_time_flags, dct, ref_list)
        chrono_tmp_list, chrono_id = buildAMPM(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        chrono_tmp_list, chrono_id = buildPartOfDay(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id = buildPartOfWeek(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id = buildSeasonOfYear(s, chrono_id, chrono_tmp_list, ref_list)
        chrono_tmp_list, chrono_id = buildPeriodInterval(s, chrono_id, chrono_tmp_list, ref_list, PIclassifier, PIfeatures)
        chrono_tmp_list, chrono_id = buildTextYear(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id = This.buildThis(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id = BeforeAfter.buildBeforeAfter(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id = NthFromStart.buildNthFromStart(s, chrono_id, chrono_tmp_list, ref_list)
        chrono_tmp_list, chrono_id = TimeZone.buildTimeZone(s, chrono_id, chrono_tmp_list)
        
    #    print("XXXXXXXXX")
    #    print(s)
    #    for e in chrono_tmp_list:
    #        print(e)
        
        
        tmplist, chrono_id = buildSubIntervals(chrono_tmp_list, chrono_id, dct, ref_list)
        chrono_list = chrono_list+tmplist
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
def buildSubIntervals(chrono_list, chrono_id, dct, ref_list):
    year = None
    month = None
    day = None
    hour = None
    minute = None
    second = None
    daypart = None
    dayweek = None
    interval = None
    period = None
    nth = None
    mod = None
    tz = None
    ampm = None
    modifier = None
   
    #print("in Build Subintervals") 
    ## loop through all entities and pull out the approriate IDs
    for e in range(0,len(chrono_list)):
        #print(chrono_list[e].get_id())
        e_type = chrono_list[e].get_type()
        #print("E-type: " + e_type)
        
        if e_type == "Two-Digit-Year" or e_type == "Year":
            year = e
            # print("YEAR VALUE: " + str(chrono_list[e].get_value()))
        elif e_type == "Month-Of-Year":
            # print("FOUND Month")
            month = e
        elif e_type == "Day-Of-Month":
            day = e
        elif e_type == "Hour-Of-Day":
            hour = e
        elif e_type == "Minute-Of-Hour":
            minute = e
        elif e_type == "Second-Of-Minute":
            second = e
        elif e_type == "Part-Of-Day":
            daypart = e
        elif e_type == "Day-Of-Week":
            dayweek = e
        elif e_type == "Calendar-Interval":
            interval = e
        elif e_type == "Period":
            period = e
        elif e_type == "NthFromStart":
            nth = e
        elif e_type == "This" or e_type == "Next" or e_type == "Last":
            # print("FOUND Mod")
            mod = e
        elif e_type == "Time-Zone":
            #print("Time Zone Value: " + str(chrono_list[e]))
            tz = e
        elif e_type == "AMPM-Of-Day":
            #print("AMPM Value: " + str(chrono_list[e]))
            ampm = e
        elif e_type == "Modifier":
            #print("Modifier Value: " + str(chrono_list[e]))
            modifier = e
        
    ## Now identify all NEXT and LAST entities
    ## Need to edit to figure out if a modifier word exists first, then test for year, etc.
    ## need to look specifically for modifier words in the other methods.  This method catches full dates that are next or last with no modifier words.
    if year is None:
        if dct is not None:
            if month is not None and mod is None:                
                mStart = chrono_list[month].get_start_span()
                mEnd = chrono_list[month].get_end_span()
                
                my_month = utils.getMonthNumber(chrono_list[month].get_month_type())
                
                if day is not None and my_month == dct.month:
                    # add a Last
                    if chrono_list[day].get_value() <= dct.day:
                        chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=chrono_list[month].get_id()))
                        chrono_id = chrono_id + 1
                    elif chrono_list[day].get_value() > dct.day:
                        chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=chrono_list[month].get_id()))
                        chrono_id = chrono_id + 1
                
                elif my_month < dct.month:
                    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=chrono_list[month].get_id()))
                    chrono_id = chrono_id + 1
                    
                elif my_month > dct.month:
                    chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=chrono_list[month].get_id()))
                    chrono_id = chrono_id + 1      
            
            ##having a problem where a past day is being referenced without it being explicit.  
            ##need to look at the closest preceding verb tense to see if it is past or present I think.
            ##will need the reference list to do this.
            if dayweek is not None and mod is None:                
                mStart = chrono_list[dayweek].get_start_span()
                mEnd = chrono_list[dayweek].get_end_span()
                
                #Get ref idx for this token
                ref = utils.getRefIdx(ref_list, mStart, mEnd)
                vb = None
                
                while vb is None and ref != 0:
                    if "VB" in ref_list[ref].getPos():
                        if ref_list[ref].getPos() in ["VBD","VBN"]:
                            #past tense so put as a last
                            chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=chrono_list[dayweek].get_id()))
                            chrono_id = chrono_id + 1
                            # print("FOUND DAYWEEK LAST")
                        elif ref_list[ref].getPos() in ["VB","VBG","VBP","VBZ"]:
                            #present tense so put as a next
                            chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=chrono_list[dayweek].get_id()))
                            chrono_id = chrono_id + 1  
                            # print("FOUND DAYWEEK NEXT")
                        vb = True
                    # print("Ref Tok: " + str(ref))
                    ref-=1
                
                '''
                weekdays = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}
                ##Monday is 0 and Sunday is 6
                dct_day = dct.weekday()
                ##need convert the doctime to a day of week
                my_dayweek = weekdays[chrono_list[dayweek].get_day_type()]
                
                if my_dayweek < dct_day:
                    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=chrono_list[dayweek].get_id()))
                    chrono_id = chrono_id + 1
                    print("FOUND DAYWEEK LAST")
                    
                elif my_dayweek > dct_day:
                    chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=chrono_list[dayweek].get_id()))
                    chrono_id = chrono_id + 1  
                    print("FOUND DAYWEEK NEXT")        
                '''
    
    ## Now assign all sub-intervals
    if second is not None and minute is not None:
        chrono_list[minute].set_sub_interval(chrono_list[second].get_id())
    if minute is not None and hour is not None:
        #print("Linking entities " + str(minute) + " and " + str(hour))
        chrono_list[hour].set_sub_interval(chrono_list[minute].get_id())
    if hour is not None and day is not None:
        chrono_list[day].set_sub_interval(chrono_list[hour].get_id())
    if day is not None and month is not None:
        chrono_list[month].set_sub_interval(chrono_list[day].get_id())
    if month is not None and year is not None:
        chrono_list[year].set_sub_interval(chrono_list[month].get_id())
    if dayweek is not None and hour is not None:
        chrono_list[dayweek].set_sub_interval(chrono_list[hour].get_id())
    if dayweek is not None and daypart is not None and hour is None:
        chrono_list[dayweek].set_sub_interval(chrono_list[daypart].get_id())
    if day is not None and daypart is not None and hour is None:
        chrono_list[day].set_sub_interval(chrono_list[daypart].get_id())
    if nth is not None and period is not None:
        # print("Adding period sub-interval")
        chrono_list[nth].set_period(chrono_list[period].get_id())
    elif nth is not None and interval is not None:
        # print("Adding interval sub-interval")
        chrono_list[nth].set_repeating_interval(chrono_list[interval].get_id())
    
    reindex = False
    if ampm is not None and hour is not None:
        chrono_list[hour].set_ampm(chrono_list[ampm].get_id())
    elif ampm is not None and hour is None:
        # Delete the AMPM entity if not hour associated with it.
        #print("Deleting AMPM")
        del chrono_list[ampm]
        reindex = True
    
    if reindex:
        for e in range(0,len(chrono_list)):
            #print(chrono_list[e].get_id())
            e_type = chrono_list[e].get_type()
            if e_type == "Time-Zone":
                #print("Reindexing Time Zone Value: " + str(chrono_list[e]))
                tz = e
        
    if tz is not None and hour is not None:
        chrono_list[hour].set_time_zone(chrono_list[tz].get_id())
    elif tz is not None and hour is None:
        # Delete the tz entity if there is no hour to link it to.  Not sure if this will work for all cases.
        #print("Deleting TimeZone")
        del chrono_list[tz]

    # Link modifiers
    if modifier is not None and period is not None:
        chrono_list[period].set_modifier(chrono_list[modifier].get_id())
    elif modifier is not None and interval is not None:
        chrono_list[interval].set_modifier(chrono_list[modifier].get_id())
    elif modifier is not None and period is None and interval is None:
        # Delete the modifier entity if there is no period or interval to link it to.  Not sure if this will work for all cases.
        #print("Deleting Modifier")
        del chrono_list[modifier]
    
    
    ##### Notes: This next bit is complicated.  If I include it I remove some False Positives, but I also create some False Negatives.
    ##### I think more complex parsing is needed here to figure out if the ordinal is an NthFromStart or not.  
    ##### I think implementing a machine learning method here may help.
    #elif nth is not None:
        # if the nthFromStart does not have a corresponding interval we should remove it from the list.
        #print("REMOVING NthFromStart: " + str(chrono_list[nth]))
        #del chrono_list[nth]
    
    return chrono_list, chrono_id

####
#END_MODULE
####



## Takes in a single text string and identifies if it has a hh:mm:ss
# @author Nicholas Morton
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasTimeString(tpentity):
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    # convert to list
    text_list = text_norm.split(" ")

    if len(text_list) > 0:
        # loop through list looking for expression
        for text in text_list:
            # define regular expression to find a numeric hour
            if (re.search('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$', text)):  # checks for HH:MM:SS String
                if len(text.split(":")) == 3:
                    start_idx, end_idx = getSpan(text_norm, re.compile(":").split(text)[0])
                    return True, text, start_idx, end_idx

                else:
                    return False, None, None, None  # if no 2 digit hour expressions were found return false

        return False, None, None, None  # if no 2 digit hour expressions were found return false
    else:

        return False, None, None, None  # if the text_list does not have any entries, return false


####
# END_MODULE
####

## Parses a TimePhrase entity's text field to determine if it contains a day of the week written out in text form, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse 
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
                chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id(), semantics="Interval-Included"))
                chrono_id = chrono_id + 1
            #else:
            #    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id(), semantics="Interval-Included"))
            #    chrono_id = chrono_id + 1
                
        #else:
            # TODO all last operators are getting added here except yesterday...
        #    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, semantics="Interval-Included", repeating_interval=my_entity.get_id()))
        #    chrono_id = chrono_id + 1
    
        
    return chrono_list, chrono_id
####
#END_MODULE
#### 

## Takes in a single text string and identifies if it is a day of week
# @author Amy Olex
# @param text The text to be parsed
# @return value The normalized string value for the day of week, or None if no Day of week found.
# @ISSUE If there are multiple days of week in the temporal phrase it only captures one of them.
def hasDayOfWeek(tpentity):
    # print("Before:" + text)
    # convert to all lower
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", string.punctuation))
    # print("After:" + text_norm)
    # convert to list
    text_list = text_norm.split(" ")

    # define my day lists
    M = ["monday", "mon", "m"]
    T = ["tuesday", "tue", "tues", "t"]
    W = ["wednesday", "wed", "w"]
    TR = ["thursday", "thur", "tr", "th"]
    F = ["friday", "fri", "f"]
    S = ["saturday", "sat", "s"]
    SU = ["sunday", "sun", "su"]
    days_of_week = M + T + W + TR + F + S + SU

    # figure out if any of the tokens in the text_list are also in the days of week list
    intersect = list(set(text_list) & set(days_of_week))

    # only proceed if the intersect list has a length of 1 or more.
    if len(intersect) >= 1:
        # test if the intersect list contains which days.
        if len(list(set(intersect) & set(M))) == 1:
            day_text = list(set(intersect) & set(M))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Monday", start_idx, end_idx

        if len(list(set(intersect) & set(T))) == 1:
            day_text = list(set(intersect) & set(T))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Tuesday", start_idx, end_idx

        if len(list(set(intersect) & set(W))) == 1:
            day_text = list(set(intersect) & set(W))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Wednesday", start_idx, end_idx

        if len(list(set(intersect) & set(TR))) == 1:
            day_text = list(set(intersect) & set(TR))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Thursday", start_idx, end_idx

        if len(list(set(intersect) & set(F))) == 1:
            day_text = list(set(intersect) & set(F))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Friday", start_idx, end_idx

        if len(list(set(intersect) & set(S))) == 1:
            day_text = list(set(intersect) & set(S))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Saturday", start_idx, end_idx

        if len(list(set(intersect) & set(SU))) == 1:
            day_text = list(set(intersect) & set(SU))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Sunday", start_idx, end_idx
        else:
            return False, None, None, None
    else:
        return False, None, None, None


####
# END_MODULE
####

## Parses a TimePhrase entity's text field to determine if it contains a season of the year written out in text form, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildSeasonOfYear(s, chrono_id, chrono_list, ref_list):
    
    boo, val, idxstart, idxend = hasSeasonOfYear(s, ref_list)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoSeasonOfYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, season_type=val)
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
            #else:
            #    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
            #    chrono_id = chrono_id + 1
                
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
            
    return chrono_list, chrono_id
####
#END_MODULE
####

## Takes in a TimePhrase entity and identifies if it has any season terms, like "summer" or "fall"
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasSeasonOfYear(tpentity, ref_list):
    refStart_span, refEnd_span = tpentity.getSpan()

    # convert to all lower
    # text_lower = tpentity.getText().lower()
    text = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).strip()

    # convert to list
    text_list = text_norm.split(" ")

    # define my period lists
    seasonofyear = ["summer", "winter", "fall", "spring", "summers", "falls", "winters", "springs"]

    # figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(seasonofyear))

    # only proceed if the intersect list has a length of 1 or more.
    # For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1:

        term = intersect[0]
        start_idx, end_idx = getSpan(text_norm, term)
        if term == "summer" or term == "summers":
            start_idx, end_idx = getSpan(text_norm, "summer")
            absStart = refStart_span + start_idx
            absEnd = refStart_span + end_idx
            postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

            if postag == "NN":
                return True, "Summer", start_idx, end_idx

        elif term == "winter" or term == "winters":
            start_idx, end_idx = getSpan(text_norm, "winter")
            absStart = refStart_span + start_idx
            absEnd = refStart_span + end_idx
            postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

            if postag == "NN":
                return True, "Winter", start_idx, end_idx

        elif term == "fall" or term == "falls":
            start_idx, end_idx = getSpan(text_norm, "fall")
            absStart = refStart_span + start_idx
            absEnd = refStart_span + end_idx
            postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

            if postag == "NN":
                return True, "Fall", start_idx, end_idx

        elif term == "spring" or term == "springs":
            start_idx, end_idx = getSpan(text_norm, "spring")
            absStart = refStart_span + start_idx
            absEnd = refStart_span + end_idx
            postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

            if postag == "NN":
                return True, "Spring", start_idx, end_idx

        else:
            return False, None, None, None

    return False, None, None, None

####
# END_MODULE
####

## Parses a TimePhraseEntity's text field to determine if it contains a month of the year, written out in text form, followed by a day, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhraseEntity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildTextYear(s, chrono_id, chrono_list):
    
    boo, val, idxstart, idxend = isTextYear(s)
    
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=val)
        chrono_id = chrono_id + 1
        chrono_list.append(my_year_entity)

    return chrono_list, chrono_id

def isTextYear(tpentity):
    #remove ending punctuation
    text1 = tpentity.getText().strip(",.")
    #replace all other punctuation and replace with spaces
    text = text1.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    #make sure it is all letters
    m = re.search('[a-z,A-Z,-,\s]*', text)
    if m.group(0) is not '':
        ##split on spaces
        tokenized_text = WhitespaceTokenizer().tokenize(text)
        for t in tokenized_text:
            if utils.getNumberFromText(t) is None:
                return False, None, None, None
        val = utils.getNumberFromText(text)
        
        if val is not None:
            if val >= 1500 and val <= 2050:
                r = re.search(text1, tpentity.getText())
                start, end = r.span(0)
                return True, val, start, end
            else:
                return False, None, None, None
        else:
            return False, None, None, None
    return False, None, None, None


## Parses a TimePhraseEntity's text field to determine if it contains a month of the year, written out in text form, followed by a day, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhraseEntity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
# ISSUE: This method assumes the day appears after the month, but that may not always be the case as in "sixth of November"
# ISSUE: This method has much to be desired. It will not catch all formats, and will not be able to make the correct connections for sub-intervals.
#        It also will not be able to identify formats like "January 6, 1996" or "January third, nineteen ninety-six".  
def buildTextMonthAndDay(s, chrono_id, chrono_list, flags, dct=None, ref_list=None):
    boo, val, idxstart, idxend = hasTextMonth(s, ref_list)
    if boo and not flags["month"]:
        flags["month"] = True
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
            substr = s.getText()[idxend:].strip(",.").strip()

            num = utils.getNumberFromText(substr)
            if num is not None:
                if num <= 31 and not flags["day"]:
                    flags["day"] = True
                    day_startidx, day_endidx = getSpan(s.getText(), str(num))#substr)
                    abs_Sspan = ref_Sspan + day_startidx
                    abs_Espan = ref_Sspan + day_endidx
                    my_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num)
                    chrono_list.append(my_day_entity)
                    chrono_id = chrono_id + 1
                    
                    #now figure out if it is a NEXT or LAST
                    #create doctime
                    if False: #dct is not None:
                        mStart = my_month_entity.get_start_span()
                        mEnd = my_month_entity.get_end_span()
                        this_dct = datetime.datetime(int(dct.year),int(utils.getMonthNumber(my_month_entity.get_month_type())), int(my_day_entity.get_value()), 0, 0)
                        if this_dct > dct:
                            chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                            chrono_id = chrono_id + 1
                        elif this_dct < dct:
                            chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                            chrono_id = chrono_id + 1
                elif num >=1500 and num <=2050 and not flags["fourdigityear"] and not flags["loneDigitYear"]:
                    flags["fourdigityear"] = True
                    year_startidx, year_endidx = getSpan(s.getText(), substr)
                    abs_Sspan = ref_Sspan + year_startidx
                    abs_Espan = ref_Sspan + year_endidx
                    
                    my_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num)
                    chrono_list.append(my_year_entity)
                    my_year_entity.set_sub_interval(my_month_entity.get_id())
                    chrono_id = chrono_id + 1
            else:
                ##parse and process each token
                ##replace punctuation 
                substr = substr.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
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
                            if False: #dct is not None:
                                mStart = my_month_entity.get_start_span()
                                mEnd = my_month_entity.get_end_span()
                                this_dct = datetime.datetime(int(dct.year),int(utils.getMonthNumber(my_month_entity.get_month_type())), int(my_day_entity.get_value()), 0, 0)
                                if this_dct > dct:
                                    chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                                    chrono_id = chrono_id + 1
                                elif this_dct < dct:
                                    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                                    chrono_id = chrono_id + 1
                        elif num >=1500 and num <=2050 and not flags["fourdigityear"] and not flags["loneDigitYear"]:
                            flags["fourdigityear"] = True
                            year_startidx, year_endidx = getSpan(s.getText(), tokenized_text[i])
                            abs_Sspan = ref_Sspan + year_startidx
                            abs_Espan = ref_Sspan + year_endidx
                            
                            my_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num)
                            chrono_list.append(my_year_entity)
                            my_year_entity.set_sub_interval(my_month_entity.get_id())
                            chrono_id = chrono_id + 1
     
        ## if the start of the month is not 0 then we have leading text to parse
        if(idxstart > 0):
            #substr = s.getText()[:idxstart].strip(",.").strip()
            hasMod, mod_type, mod_start, mod_end = hasModifier(s)
            if(hasMod):
                if mod_type == "This":
                    chrono_list.append(chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity", start_span=ref_Sspan+mod_start, end_span=ref_Sspan+mod_end, repeating_interval=my_month_entity.get_id()))
                    chrono_id = chrono_id + 1
                
                if mod_type == "Next":
                    chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=ref_Sspan+mod_start, end_span=ref_Sspan+mod_end, repeating_interval=my_month_entity.get_id()))
                    chrono_id = chrono_id + 1
                
                if mod_type == "Last":
                    # print("FOUND LAST")
                    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=ref_Sspan+mod_start, end_span=ref_Sspan+mod_end, repeating_interval=my_month_entity.get_id(), semantics="Interval-Not-Included"))
                    chrono_id = chrono_id + 1
        
        chrono_list.append(my_month_entity)
        
    return chrono_list, chrono_id, flags

####
#END_MODULE
####

## Takes in a single text string and identifies if it is a month of the year
# @author Amy Olex
# @param tpentity The entity to parse
# @return value The normalized string value for the month of the year, or None if no month of year found.
# @ISSUE If there are multiple months of the year in the temporal phrase it only captures one of them.
def hasTextMonth(tpentity, ref_list):
    refStart_span, refEnd_span = tpentity.getSpan()

    # convert to all lower
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    # text_norm = text_lower.translate(str.maketrans(",", ' ')).strip()
    text_norm = text_lower.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).strip()
    # convert to list
    text_list = text_norm.split(" ")

    # define my month lists
    full_month = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
                  "november", "december"]

    # run for full month
    t_flag = False
    for tok in text_list:
        answer = next((m for m in full_month if tok in m), None)
        if answer is not None and not t_flag:
            answer2 = next((m for m in full_month if m in tok), None)
            if answer2 is not None and not t_flag:
                t_flag = True
                # answer2 should contain the element that matches.  We need to find the span in the original phrase and return the correct value
                start_idx, end_idx = getSpan(text_lower, answer2)
                absStart = refStart_span + start_idx
                absEnd = refStart_span + end_idx
                postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

                if postag == "NNP":
                    if answer2 in ["january"]:
                        return True, "January", start_idx, end_idx
                    elif answer2 in ["february"]:
                        return True, "February", start_idx, end_idx
                    elif answer2 in ["march"]:
                        return True, "March", start_idx, end_idx
                    elif answer2 in ["april"]:
                        return True, "April", start_idx, end_idx
                    elif answer2 in ["may"]:
                        return True, "May", start_idx, end_idx
                    elif answer2 in ["june"]:
                        return True, "June", start_idx, end_idx
                    elif answer2 in ["july"]:
                        return True, "July", start_idx, end_idx
                    elif answer2 in ["august"]:
                        return True, "August", start_idx, end_idx
                    elif answer2 in ["september"]:
                        return True, "September", start_idx, end_idx
                    elif answer2 in ["october"]:
                        return True, "October", start_idx, end_idx
                    elif answer2 in ["november"]:
                        return True, "November", start_idx, end_idx
                    elif answer2 in ["december"]:
                        return True, "December", start_idx, end_idx

    # run for abbr month
    abbr_month = ["jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug.", "sept.", "sep.", "oct.", "nov.", "dec."]
    adj_punc = '!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~'
    text_norm2 = text_lower.translate(str.maketrans(adj_punc, ' ' * len(adj_punc))).strip()
    # convert to list
    text_list2 = text_norm2.split(" ")

    t_flag = False
    for tok in text_list2:
        answer = next((m for m in abbr_month if tok in m), None)
        if answer is not None and not t_flag:
            answer2 = next((m for m in abbr_month if m in tok), None)
            if answer2 is not None and not t_flag:
                t_flag = True
                # answer2 should contain the element that matches.  We need to find the span in the original phrase and return the correct value
                start_idx, end_idx = getSpan(text_lower, answer2)
                absStart = refStart_span + start_idx
                absEnd = refStart_span + end_idx
                postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

                if postag == "NNP":
                    if answer2 in ["jan."]:
                        return True, "January", start_idx, end_idx
                    elif answer2 in ["feb."]:
                        return True, "February", start_idx, end_idx
                    elif answer2 in ["mar."]:
                        return True, "March", start_idx, end_idx
                    elif answer2 in ["apr."]:
                        return True, "April", start_idx, end_idx
                    elif answer2 in ["jun."]:
                        return True, "June", start_idx, end_idx
                    elif answer2 in ["jul."]:
                        return True, "July", start_idx, end_idx
                    elif answer2 in ["aug."]:
                        return True, "August", start_idx, end_idx
                    elif answer2 in ["sept.", "sep."]:
                        return True, "September", start_idx, end_idx
                    elif answer2 in ["oct."]:
                        return True, "October", start_idx, end_idx
                    elif answer2 in ["nov."]:
                        return True, "November", start_idx, end_idx
                    elif answer2 in ["dec."]:
                        return True, "December", start_idx, end_idx

    # run for abbr month without punctuation
    abbr_month = ["jan", "feb", "mar", "apr", "jun", "jul", "aug", "sept", "sep", "oct", "nov", "dec"]
    adj_punc = '!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~'
    text_norm2 = text_lower.translate(str.maketrans(adj_punc, ' ' * len(adj_punc))).strip()
    # convert to list
    text_list2 = text_norm2.split(" ")

    t_flag = False
    for tok in text_list2:
        answer = next((m for m in abbr_month if tok in m), None)
        if answer is not None and not t_flag:
            answer2 = next((m for m in abbr_month if m in tok), None)
            if answer2 is not None and not t_flag:
                t_flag = True
                # answer2 should contain the element that matches.  We need to find the span in the original phrase and return the correct value
                start_idx, end_idx = getSpan(text_lower, answer2)
                absStart = refStart_span + start_idx
                absEnd = refStart_span + end_idx
                postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

                if postag == "NNP":
                    if answer2 in ["jan"]:
                        return True, "January", start_idx, end_idx
                    elif answer2 in ["feb"]:
                        return True, "February", start_idx, end_idx
                    elif answer2 in ["mar"]:
                        return True, "March", start_idx, end_idx
                    elif answer2 in ["apr"]:
                        return True, "April", start_idx, end_idx
                    elif answer2 in ["jun"]:
                        return True, "June", start_idx, end_idx
                    elif answer2 in ["jul"]:
                        return True, "July", start_idx, end_idx
                    elif answer2 in ["aug"]:
                        return True, "August", start_idx, end_idx
                    elif answer2 in ["sept", "sep"]:
                        return True, "September", start_idx, end_idx
                    elif answer2 in ["oct"]:
                        return True, "October", start_idx, end_idx
                    elif answer2 in ["nov"]:
                        return True, "November", start_idx, end_idx
                    elif answer2 in ["dec"]:
                        return True, "December", start_idx, end_idx

    return False, None, None, None


####
# END_MODULE
####
 
## Parses a TimePhrase entity's text field to determine if it contains a AM or PM time indication, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildAMPM(s, chrono_id, chrono_list, flags):
    am_flag = True
    ref_Sspan, ref_Espan = s.getSpan()
    ## Identify if a time zone string exists
    # tz = hasTimeZone(s)
    # if tz is not None:
    #     my_tz_entity = chrono.ChronoTimeZoneEntity(str(chrono_id) + "entity", start_span =tz.span(0)[0] + ref_Sspan, end_span=tz.span(0)[1] + ref_Sspan)
    #     chrono_list.append(my_tz_entity)
    #     chrono_id = chrono_id + 1
    # else:
    #     my_tz_entity = None
     
    boo, val, idxstart, idxend = hasAMPM(s)
    if boo:
        if val == "PM":
            am_flag = False

        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_AMPM_entity = chrono.ChronoAMPMOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, ampm_type=val)
        chrono_id = chrono_id + 1
        chrono_list.append(my_AMPM_entity)

        #check to see if it has a time associated with it.  We assume the time comes before the AMPM string
        #We could parse out the time from the TimePhrase normalized value.  The problem is getting the correct span.
        #idx_start is the first index of the ampm.  If there are any characters before it, it will be greater than 0.
        if idxstart > 0 and not flags['hour']:
            substr = s.getText()[0:idxstart]
            m = re.search('([0-9]{1,2})', substr)
            if m is not None :
                hour_val = m.group(0)
                abs_Sspan = ref_Sspan + m.span(0)[0]
                abs_Espan = ref_Sspan + m.span(0)[1]
                #print("Adding Hour in AMPM")
                my_hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=hour_val, ampm=my_AMPM_entity.get_id())
                chrono_id = chrono_id + 1
                chrono_list.append(my_hour_entity)
            
            #else search for a text number
            else:
                texNumVal = utils.getNumberFromText(substr)
                
                if texNumVal is not None:
                    #create the hour entity
                    if not flags['hour']:
                        my_hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan, end_span=ref_Sspan + (idxstart - 1), value=texNumVal, ampm=my_AMPM_entity.get_id())
                        chrono_id = chrono_id + 1
                        chrono_list.append(my_hour_entity)


    return chrono_list, chrono_id
    
####
#END_MODULE
####

## Takes in a single text string and identifies if it has any AM or PM phrases
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasAMPM(tpentity):
    # convert to all lower
    # text_lower = tpentity.getText().lower()
    text = tpentity.getText()
    # remove all punctuation
    text_norm = text.translate(str.maketrans("", "", ","))
    # convert to list
    text_list = text_norm.split(" ")

    if len(text_list) > 0:
        for text in text_list:
            if (re.search('AM|A\.M\.|am|a\.m\.', text)):
                match = re.search('AM|A\.M\.|am|a\.m\.', text).group(0)
                start_idx, end_idx = getSpan(text_norm, match)
                return True, "AM", start_idx, end_idx
            elif (re.search('PM|P\.M\.|pm|p\.m\.', text)):
                match = re.search('PM|P\.M\.|pm|p\.m\.', text).group(0)
                start_idx, end_idx = getSpan(text_norm, match)
                return True, "PM", start_idx, end_idx
    return False, None, None, None

####
# END_MODULE
####

## Parses a TimePhrase entity's text field to determine if it contains a calendar interval or period phrase, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
###### ISSUES: This method assumes the number is immediatly before the interval type. There is some concern about if the spans are going to be correct.  I do test for numbers written out as words, but this assumes the entire beginning of the string from TimePhrase represents the number.  If this is not the case the spans may be off.
###### More Issues: I created the training data incorrectly to remove the TimePhrase entity from consideration.  In order to classify from scratch we would need multiple classes: period, interval, everything else.  I only have a binary classifier here, so I need to narrow it down before trying to classify.
def buildPeriodInterval(s, chrono_id, chrono_list, ref_list, classifier, feats):
    
    features = feats.copy()
    ref_Sspan, ref_Espan = s.getSpan()
    #print("In buildPeriodInterval(), TimePhrase Text: " + s.getText())
    boo, val, idxstart, idxend, plural = hasPeriodInterval(s)

    # FIND terms that are always marked as calendar intervals!
    if boo and re.search("yesterday|yesterdays|tomorrow|tomorrows|today|todays|daily|/min|/week", s.getText()):
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoCalendarIntervalEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan,
                                                        end_span=abs_Espan, calendar_type=val, number=None)
        chrono_id = chrono_id + 1
        
        if re.search("yesterday|yesterdays", s.getText()):
            
            my_last_entity = chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan,
                                                   end_span=abs_Espan, repeating_interval=str(chrono_id - 1) + "entity")
            chrono_id = chrono_id + 1
            chrono_list.append(my_last_entity)
        
        chrono_list.append(my_entity)

    # FIND terms that are always marked as periods!
    elif boo and val == "Unknown" :
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoPeriodEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan,
                                                        end_span=abs_Espan, period_type=val, number=None)
        chrono_id = chrono_id + 1
        chrono_list.append(my_entity)

    elif boo:
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        
        # get index of overlapping reference token
        #ref_idx = -1
        #for i in range(0,len(ref_list)):
        #    if(utils.overlap(ref_list[i].getSpan(),(abs_Sspan,abs_Espan))):
        #        ref_idx = i
        #        break
        
        ref_idx = utils.getRefIdx(ref_list, abs_Sspan, abs_Espan)
        
        # extract ML features
        my_features = utils.extract_prediction_features(ref_list, ref_idx, feats.copy())
        
        # classify into period or interval
        if classifier[1] == "NN":
            my_class = ChronoKeras.keras_classify(classifier[0], np.array(list(my_features.values())))
            #print("Class: " + str(my_class) + " : Start: " + str(abs_Sspan) + " : End: "+ str(abs_Espan))
        elif classifier[1] in ("SVM", "RF"):
            feat_array = [int(i) for i in my_features.values()]
            my_class = classifier[0].predict([feat_array])[0]
        else:
            my_class = classifier[0].classify(my_features)
            #print("Class: " + str(my_class) + " : Start: " + str(abs_Sspan) + " : End: "+ str(abs_Espan))

        # if 1 then it is a period, if 0 then it is an interval  
        if my_class == 1:
            my_entity = chrono.ChronoPeriodEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, period_type=getPeriodValue(val), number=None)
            chrono_id = chrono_id + 1
            ### Check to see if this calendar interval has a "this" in front of it
            prior_tok = ref_list[ref_idx-1].getText().lower()
            if prior_tok.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))) == "this":
                # add a This entitiy and link it to the interval.
                start_span, end_span = re.search(prior_tok, "this").span(0)
                prior_start, prior_end = ref_list[ref_idx-1].getSpan()
                
                chrono_this_entity = chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity", start_span=prior_start + start_span, end_span = prior_start + end_span)
                chrono_id = chrono_id + 1
                chrono_this_entity.set_period(my_entity.get_id())
                chrono_list.append(chrono_this_entity)
                
            else:    
                # check for a Last Word
                hasMod, mod_type, mod_start, mod_end = hasModifier(s)
                
                if(hasMod):
                    if mod_type == "Next":
                        chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=ref_Sspan+mod_start, end_span=ref_Sspan+mod_end, period=my_entity.get_id()))
                        chrono_id = chrono_id + 1
                
                    if mod_type == "Last":
                        chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=ref_Sspan+mod_start, end_span=ref_Sspan+mod_end, period=my_entity.get_id(), semantics="Interval-Not-Included"))
                        chrono_id = chrono_id + 1
                       
                

        else:
            my_entity = chrono.ChronoCalendarIntervalEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, calendar_type=val, number=None)
            chrono_id = chrono_id + 1
            ### Check to see if this calendar interval has a "this" in front of it
            prior_tok = ref_list[ref_idx-1].getText().lower()
            if prior_tok.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))) == "this":
                # add a This entitiy and link it to the interval.
                start_span, end_span = re.search(prior_tok, "this").span(0)
                prior_start, prior_end = ref_list[ref_idx-1].getSpan()
                
                chrono_this_entity = chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity", start_span=prior_start + start_span, end_span = prior_start + end_span)
                chrono_id = chrono_id + 1
                chrono_this_entity.set_repeating_interval(my_entity.get_id())
                chrono_list.append(chrono_this_entity)
            else:
                # check for a Last Word
                hasMod, mod_type, mod_start, mod_end = hasModifier(s)
                if(hasMod):
                    if mod_type == "Next":
                        chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=ref_Sspan+mod_start, end_span=ref_Sspan+mod_end, repeating_interval=my_entity.get_id()))
                        chrono_id = chrono_id + 1
                
                    if mod_type == "Last":
                        chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=ref_Sspan+mod_start, end_span=ref_Sspan+mod_end, repeating_interval=my_entity.get_id(), semantics="Interval-Not-Included"))
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
        
            #Extract the number and identify the span of numstr
            
            substr = s.getText()[:idxstart] ## extract entire first part of TimePhrase phrase
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

## Takes in a TimePhrase entity and identifies if it has any period or calendar interval phrases like "week" or "days"
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 5 values: Boolean Flag, Value text, start index, end index, pluralBoolean
def hasPeriodInterval(tpentity):
    # convert to all lower
    # text_lower = tpentity.getText().lower()
    text = tpentity.getText().lower()
    #print("In hasPeriodInterval text: ", text)

    reg = re.search("date/time", text)  ##we don't want to annotate these specific types of mentions
    if reg:
        #print("Found date/time, returning FALSE")
        return False, None, None, None, None

    # remove all punctuation
    text_norm = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).strip()
    # convert to list
    text_list = text_norm.split(" ")
    #print("text list: " + str(text_list))

    # define my period lists
    terms = ["decades", "decade", "yesterday", "yesterdays", "today", "todays", "tomorrow", "tomorrows", "day", "week",
             "month", "year", "daily", "weekly", "monthly", "yearly", "century", "minute", "second", "hour", "hourly", 
             "days", "weeks", "months", "years", "centuries", "century", "minutes", "seconds", "hours", "time", "shortly", 
             "soon", "briefly", "awhile", "future", "lately", "annual", "hr", "hrs", "min", "mins", "quarter"]  #, "date"]

    # figure out if any of the tokens in the text_list are also in the interval list
    intersect = list(set(text_list) & set(terms))

    #print("My intersection: " + str(intersect))

    # only proceed if the intersect list has a length of 1 or more.
    # For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1:
        # test if the intersect list contains plural or singular period.

        this_term = list(set(intersect) & set(terms))[0]
        start_idx, end_idx = getSpan(text_norm, this_term)
        if this_term in ["day", "daily", "days", "yesterday", "tomorrow", "yesterdays", "tomorrows", "today", "todays"]:
            return True, "Day", start_idx, end_idx, False
        elif this_term in ["week", "weekly", "weeks"]:
            return True, "Week", start_idx, end_idx, False
        elif this_term in ["month", "monthly", "months"]:
            return True, "Month", start_idx, end_idx, False
        elif this_term in ["year", "yearly", "years", "annual"]:
            return True, "Year", start_idx, end_idx, False
        elif this_term in ["century", "centuries"]:
            return True, "Century", start_idx, end_idx, False
        elif this_term in ["decade", "decades"]:
            return True, "Decade", start_idx, end_idx, False
        elif this_term in ["minute", "minutes", "min", "mins"]:
            return True, "Minute", start_idx, end_idx, False
        elif this_term in ["second", "seconds"]:
            return True, "Second", start_idx, end_idx, False
        elif this_term in ["hour", "hourly", "hours", "hr", "hrs"]:
            return True, "Hour", start_idx, end_idx, False
        elif this_term in ["time", "shortly", "soon", "briefly", "awhile", "future", "lately", "quarter"]:
            return True, "Unknown", start_idx, end_idx, False
        else:
            return False, None, None, None, None

    elif len(intersect) > 1:
        this_term = list(
            set(intersect) & set(["daily", "weekly", "monthly", "yearly", "weeks", "days", "months", "years"]))

        if (this_term):
            if (len(this_term) == 1):
                this_term = this_term[0]
                start_idx, end_idx = getSpan(text_norm, this_term)

                if this_term in ["daily", "days"]:
                    #print("Returning a Daily")
                    return True, "Day", start_idx, end_idx, False
                elif this_term in ["weekly", "weeks"]:
                    return True, "Week", start_idx, end_idx, False
                elif this_term in ["monthly", "months"]:
                    return True, "Month", start_idx, end_idx, False
                elif this_term in ["yearly", "years"]:
                    return True, "Year", start_idx, end_idx, False
                else:
                    return False, None, None, None, None
            else:
                return False, None, None, None, None
        else:
            return False, None, None, None, None

    else:
        return False, None, None, None, None


####
# END_MODULE
####

## Takes in a TimePhrase entity and identifies if it has any calendar interval phrases like "week" or "days"
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 5 values: Boolean Flag, Value text, start index, end index, numeric string
# Note: this should be called after everything else is checked.  The numeric string will need to have it's span and value identified by the calling method.
def hasEmbeddedPeriodInterval(tpentity):
    # convert to all lower
    # text_lower = tpentity.getText().lower()
    text = tpentity.getText()
    # remove all punctuation
    text_norm = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    # convert to list
    text_list = text_norm.split(" ")

    # define my period/interval term lists
    terms = ["decades", "decade", "yesterday", "yesterdays", "today", "todays", "tomorrow", "tomorrows", "day", "week",
             "month", "year", "daily", "weekly", "monthly", "yearly", "century", "minute", "second", "hour", "hourly", 
             "days", "weeks", "months", "years", "centuries", "century", "minutes", "seconds", "hours", "time", "shortly", 
             "soon", "briefly", "awhile", "future", "lately", "annual", "hr", "hrs", "min", "mins", "quarter"] #, "date"]

    ## if the term does not exist by itself it may be a substring. Go through each word in the TimePhrase string and see if a substring matches.
    for t in text_list:
        for r in terms:
            ## see if r is a substring of t
            ## if yes and the substring is at the end, extract the first substring and test to see if it is a number.
            idx = t.find(r)
            if (idx > 0):
                # then the r term is not the first substring.  Extract and test.
                sub1 = t[:idx]
                sub2 = t[idx:]
                # sub1 should be a number
                if (isinstance(utils.getNumberFromText(sub1), (int))):
                    # if it is a number then test to figure out what sub2 is.
                    this_term = sub2
                    start_idx, end_idx = getSpan(text_norm, this_term)
                    if this_term in ["day", "daily", "days", "yesterday", "tomorrow", "yesterdays", "tomorrows",
                                     "today", "todays"]:
                        #print("ACK! Found an Embedded Day")
                        return True, "Day", start_idx, end_idx, sub1
                    elif this_term in ["week", "weekly", "weeks"]:
                        return True, "Week", start_idx, end_idx, sub1
                    elif this_term in ["month", "monthly", "months"]:
                        return True, "Month", start_idx, end_idx, sub1
                    elif this_term in ["year", "yearly", "years"]:
                        return True, "Year", start_idx, end_idx, sub1
                    elif this_term in ["century", "centuries"]:
                        return True, "Century", start_idx, end_idx, sub1
                    elif this_term in ["decade", "decades"]:
                        return True, "Decade", start_idx, end_idx, sub1
                    elif this_term in ["minute", "minutes"]:
                        return True, "Minute", start_idx, end_idx, sub1
                    elif this_term in ["second", "seconds"]:
                        return True, "Second", start_idx, end_idx, sub1
                    elif this_term in ["hour", "hourly", "hours"]:
                        return True, "Hour", start_idx, end_idx, sub1
                    elif this_term in ["time", "shortly", "soon", "briefly", "awhile", "future", "lately"]:
                        return True, "Unknown", start_idx, end_idx, sub1

                else:
                    return False, None, None, None, None
    return False, None, None, None, None


####
# END_MODULE
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

####
# END_MODULE
####

## Parses a TimePhrase entity's text field to determine if it contains a part of the day expression, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse 
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

## Takes in a TimePhrase entity and identifies if it has any part of day terms, like "overnight" or "morning"
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
#############ISSUE: I've coded this to return the sub-span of the "value".  For example, the span returned for "overnight" is just for the "night" portion.  This seems to be how the gold standard xml does it, which I think is silly, but that is what it does.
def hasPartOfDay(tpentity):
    # convert to all lower
    text = tpentity.getText().lower()
    # text = tpentity.getText()
    # remove all punctuation
    text_norm = text.translate(str.maketrans("", "", string.punctuation))
    # convert to list
    text_list = text_norm.split(" ")

    # define my period lists
    partofday = ["morning", "evening", "afternoon", "night", "dawn", "dusk", "tonight", "overnight", "nights",
                 "mornings", "evening", "afternoons", "noon", "bedtime", "midnight", "eve"]

    # figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(partofday))

    # only proceed if the intersect list has a length of 1 or more.
    # For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1:

        term = intersect[0]
        start_idx, end_idx = getSpan(text_norm, term)
        if term == "morning" or term == "mornings":
            return True, "Morning", start_idx, end_idx
        if term == "dawn":
            return True, "Dawn", start_idx, end_idx
        elif term == "evening" or term == "dusk" or term == "evenings" or term == "eve":
            return True, "Evening", start_idx, end_idx
        elif term == "afternoon" or term == "afternoons":
            return True, "Afternoon", start_idx, end_idx
        elif term == "nights":
            return True, "Night", start_idx, end_idx
        elif term == "noon":
            return True, "Noon", start_idx, end_idx
        elif term == "bedtime":
            return True, "Unknown", start_idx, end_idx
        elif term == "midnight":
            return True, "Midnight", start_idx, end_idx
        elif term == "night" or term == "overnight" or term == "tonight":
            m = re.search("night", text_norm)
            sidx = m.span(0)[0]
            eidx = m.span(0)[1]
            return True, "Night", sidx, eidx
        else:
            return False, None, None, None
    else:
        return False, None, None, None

####
# END_MODULE
####

## Parses a TimePhrase entity's text field to determine if it contains a part of the week expression, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse 
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

## Takes in a TimePhrase entity and identifies if it has any part of week terms, like "weekend"
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
#############ISSUE: I've coded this to return the sub-span of the "value".  For example, the span returned for "overnight" is just for the "night" portion.  This seems to be how the gold standard xml does it, which I think is silly, but that is what it does.
def hasPartOfWeek(tpentity):
    # convert to all lower
    # text_lower = tpentity.getText().lower()
    text = tpentity.getText()
    # remove all punctuation
    text_norm = text.translate(str.maketrans("", "", string.punctuation))
    # convert to list
    text_list = text_norm.split(" ")

    # define my period lists
    partofday = ["weekend", "weekends"]

    # figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(partofday))

    # only proceed if the intersect list has a length of 1 or more.
    # For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1:

        term = intersect[0]
        start_idx, end_idx = getSpan(text_norm, term)
        if term == "weekend" or term == "weekends":
            return True, "Weekend", start_idx, end_idx
        else:
            return False, None, None, None
    else:
        return False, None, None, None

####
# END_MODULE
####

## Parses a TimePhrase entity's text field to determine if it contains a 24-hour time expression, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def build24HourTime(s, chrono_id, chrono_list, flags):
    
    boo, val, idxstart, idxend = has24HourTime(s, flags)
    ref_Sspan, ref_Espan = s.getSpan()
    if boo and not flags["loneDigitYear"]:
        ## assume format of hhmm or hhmmzzz
        try:
            hour = int(val[0:2])
            minute = int(val[2:4])
        except ValueError:
            # print("Skipping, not a 24hour time")
            return chrono_list, chrono_id, flags
            # hour = w2n.number_formation(val[0:2])
            # minute = w2n.word_to_num(val[2:4])
        #     print("TIME ZONE: {}".format(val))
        #     tz = hasTimeZone(s)
        #     my_tz_entity = chrono.ChronoTimeZoneEntity(str(chrono_id) + "entity", start_span=tz.span(0)[0] + ref_Sspan,
        #                                                end_span=tz.span(0)[1] + ref_Sspan)
        #     chrono_list.append(my_tz_entity)
        #     chrono_id = chrono_id + 1
        #     return chrono_list, chrono_id
        # #search for time zone
        # ## Identify if a time zone string exists
        # tz = hasTimeZone(s)
        # if tz is not None:
        #     my_tz_entity = chrono.ChronoTimeZoneEntity(str(chrono_id) + "entity", start_span =tz.span(0)[0] + ref_Sspan, end_span=tz.span(0)[1] + ref_Sspan)
        #     chrono_list.append(my_tz_entity)
        #     chrono_id = chrono_id + 1
        # else:
        #     my_tz_entity = None
        
        ## build minute entity
        min_entity = chrono.ChronoMinuteOfHourEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan + idxstart + 2, end_span=ref_Sspan + idxstart + 4, value=minute)
        # print("24Minute Value Added: " + str(min_entity.get_value()))
        chrono_list.append(min_entity)
        chrono_id = chrono_id + 1
        
        # if my_tz_entity is not None:
        #     hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan + idxstart, end_span=ref_Sspan + idxstart + 2, value=hour, time_zone=my_tz_entity.get_id())
        # else:
        hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan + idxstart, end_span=ref_Sspan + idxstart + 2, value=hour)
        # print("24Hour Value Added: " + str(hour_entity.get_value()))
        hour_entity.set_sub_interval(min_entity.get_id())
        chrono_list.append(hour_entity)
        chrono_id = chrono_id + 1

 
    return chrono_list, chrono_id, flags

####
#END_MODULE
####

## Takes in a single text string and identifies if it has any 4 digit 24-hour time phrases
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
# Note: This need to be called after it has checked for years
def has24HourTime(tpentity, flags):
    # text_lower = tpentity.getText().lower()
    # remove all punctuation
    # text_norm = text_lower.translate(str.maketrans("", "", ","))
    # convert to list
    stext = tpentity.getText()
    text_list = stext.split(" ")

    if not flags["loneDigitYear"]:
        # loop through list looking for expression
        for text in text_list:
            tz_format = re.search(
                '\d{0,4}(AST|EST|EDT|CST|CDT|MST|MDT|PST|PDT|AKST|HST|HAST|HADT|SST|SDT|GMT|CHST|UTC)', text)
            if len(text) == 4:
                num = utils.getNumberFromText(text)
                if num is not None:
                    hour = utils.getNumberFromText(text[:2])
                    minute = utils.getNumberFromText(text[2:])
                    if (hour is not None) and (minute is not None):
                        if (minute > 60) or (hour > 24):
                            return False, None, None, None
                        else:
                            start_idx, end_idx = getSpan(stext, text)
                            return True, text, start_idx, end_idx
            elif tz_format is not None:
                time = tz_format[0]
                # print("THIS TIME: {}".format(time))
                hour = utils.getNumberFromText(time[0:2])
                minute = utils.getNumberFromText(time[2:4])
                # if (minute > 60) or (hour > 24):
                #     return False, None, None, None
                # else:
                start_idx, end_idx = getSpan(stext, time)
                return True, time, start_idx, end_idx

        return False, None, None, None  # if no 4 digit year expressions were found return false
    else:
        return False, None, None, None  # if loneDigitYearFlag has already been set

####
#END_MODULE
####

## Parses a TimePhrase entity's text field to determine if it contains a part of the day expression, then builds the associated chronoentity list
# @author Nicholas Morton
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return TimePhrase Duration Entity
def buildDuration(s, chrono_id, chrono_list): 

    #if hasExactDuration(s):  #3 days -> P3D

    #if hasInExactDuration(s): #a few years -> PXY

    #if hasDurationRange(s): #2 to 3 months -> P2M/P3M

    return chrono_list, chrono_id
 
####
#END_MODULE
#### 

## Parses a TimePhrase entity's text field to determine if it contains a part of the day expression, then builds the associated chronoentity list
# @author Nicholas Morton
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return TimePhrase Set Entity
def buildSet(s, chrono_id, chrono_list):

    return chrono_list, chrono_id


####
#END_MODULE
####

## Parses a TimePhrase entity's text field to determine if it contains a modifier text expression, then builds the associated chronoentity list
# @author Luke Maffey
# @param s The TimePhrase entity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildModifierText(s, chrono_id, chrono_list):
    boo, val, idxstart, idxend = hasModifierText(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        if val is not None:
            if val in ("nearly", "almost", "<"):
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, modifier="Less-Than")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val in ("about", "approximately"):
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="Approx")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val == "late":
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="End")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val == "mid":
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="Mid")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val == "fiscal" or val == "fy":
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="Fiscal")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val == "over":
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="More-Than")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val in ("early", "beginning"):
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="Start")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            else:
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="Approx")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
        else:
            my_modifier_entity = None

    return chrono_list, chrono_id

####
# END_MODULE
####

## Takes in a single text string and identifies if it has a modifier text
# @author Luke Maffey
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasModifierText(tpentity):

    text_lower = tpentity.getText().lower()
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        temp_text = ["nearly", "almost", "<", "late", "mid", "fiscal", "fy", "over", "early", "approximately", "beginning"]

        for t in text_list:
            answer = next((m for m in temp_text if m in t), None)
            if answer is not None:
                answer2 = next((m for m in temp_text if t in m), None)
                if answer2 is not None:
                    return True, t, getSpan(text_norm,t)[0], getSpan(text_norm,t)[1]
                else:
                    return False, None, None, None  # if no 2 digit hour expressions were found return false
            else:
                return False, None, None, None  # if no 2 digit day expressions were found return false
    else:

        return False, None, None, None  # if the text_list does not have any entries, return false
####
#END_MODULE
####

## Takes in a single text string and identifies if it has any modufying phrases
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasModifier(tpentity):
    # convert to all lower
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text_lower.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    # convert to list
    text_list = text_norm.split(" ")

    # define my day lists
    modifiers = ["this", "next", "last", "a", "each", "between", "from"]

    # figure out if any of the tokens in the text_list are also in the modifiers list
    intersect = list(set(text_list) & set(modifiers))

    # only proceed if the intersect list has a length of 1 or more.
    # I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1:
        # test if the intersect list contains which days.
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
        else:
            return False, None, None, None
    else:
        return False, None, None, None

####
# END_MODULE
####

## Identifies the local span of the serach_text in the input "text"
# @author Amy Olex
# @param text The text to be searched
# @param search_text The text to search for.
# @return The start index and end index of the search_text string.
######## ISSUE: This needs to be re-named here and in all the above usages.  Probably should also move this to the utils class.  Dont delete the s.getSpan() as those are from the TimePhrase entity class.
def getSpan(text, search_text):
    try:
        start_idx = text.index(search_text)
        end_idx = start_idx + len(search_text)
    except ValueError:
        return None, None

    return start_idx, end_idx

# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag
# def hasExactDuration(tpentity):
#
#     if "P#D":
#         return True
#     else:
#         return False

####
#END_MODULE
####

