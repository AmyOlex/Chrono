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


from Chrono.TimePhraseToChrono import *
from Chrono import referenceToken
from Chrono import chronoEntities as chrono
from Chrono import utils


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
        chrono_tmp_list, chrono_id, chrono_time_flags = DayOfMonth.buildDayOfMonth(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        #Parse out HourOfDay
        chrono_tmp_list, chrono_id, chrono_time_flags = HourOfDay.buildHourOfDay(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        #Parse out MinuteOfHour
        chrono_tmp_list, chrono_id, chrono_time_flags = MinuteOfHour.buildMinuteOfHour(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        #Parse out SecondOfMinute
        chrono_tmp_list, chrono_id, chrono_time_flags = SecondOfMinute.buildSecondOfMinute(s, chrono_id, chrono_tmp_list, chrono_time_flags)

        
        #Parse modifier text
        chrono_tmp_list, chrono_id = Modifier.buildModifierText(s, chrono_id, chrono_tmp_list)

        #call non-standard formatting temporal phrases
        chrono_tmp_list, chrono_id, chrono_time_flags = NumericDate.buildNumericDate(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        chrono_tmp_list, chrono_id, chrono_time_flags = TwentyFourHourTime.build24HourTime(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        
        chrono_tmp_list, chrono_id = DayOfWeek.buildDayOfWeek(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id, chrono_time_flags = TextMonthAndDay.buildTextMonthAndDay(s, chrono_id, chrono_tmp_list, chrono_time_flags, dct, ref_list)
        chrono_tmp_list, chrono_id = AMPM.buildAMPM(s, chrono_id, chrono_tmp_list, chrono_time_flags)
        chrono_tmp_list, chrono_id = PartOfDay.buildPartOfDay(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id = PartOfWeek.buildPartOfWeek(s, chrono_id, chrono_tmp_list)
        chrono_tmp_list, chrono_id = Season.buildSeasonOfYear(s, chrono_id, chrono_tmp_list, ref_list)
        chrono_tmp_list, chrono_id = PeriodInterval.buildPeriodInterval(s, chrono_id, chrono_tmp_list, ref_list, PIclassifier, PIfeatures)
        chrono_tmp_list, chrono_id = TextYear.buildTextYear(s, chrono_id, chrono_tmp_list)
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


### UNUSED ###
## Parses a TimePhrase entity's text field to determine if it contains a part of the day expression, then builds the associated chronoentity list
# @author Nicholas Morton
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return TimePhrase Duration Entity
# def buildDuration(s, chrono_id, chrono_list):
#
#     #if hasExactDuration(s):  #3 days -> P3D
#
#     #if hasInExactDuration(s): #a few years -> PXY
#
#     #if hasDurationRange(s): #2 to 3 months -> P2M/P3M
#
#     return chrono_list, chrono_id
#
# ####
#END_MODULE
#### 


### UNUSED ###
## Parses a TimePhrase entity's text field to determine if it contains a part of the day expression, then builds the associated chronoentity list
# @author Nicholas Morton
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return TimePhrase Set Entity
# def buildSet(s, chrono_id, chrono_list):
#
#     return chrono_list, chrono_id



# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag
# def hasExactDuration(tpentity):
#
#     if "P#D":
#         return True
#     else:
#         return False


###  UNUSED    #############
## Takes in a single text string and identifies if it has a hh:mm:ss
# @author Nicholas Morton
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
# def hasTimeString(tpentity):
#     text_lower = tpentity.getText().lower()
#     # remove all punctuation
#     text_norm = text_lower.translate(str.maketrans("", "", ","))
#     # convert to list
#     text_list = text_norm.split(" ")
#
#     if len(text_list) > 0:
#         # loop through list looking for expression
#         for text in text_list:
#             # define regular expression to find a numeric hour
#             if (re.search('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$', text)):  # checks for HH:MM:SS String
#                 if len(text.split(":")) == 3:
#                     start_idx, end_idx = getSpan(text_norm, re.compile(":").split(text)[0])
#                     return True, text, start_idx, end_idx
#
#                 else:
#                     return False, None, None, None  # if no 2 digit hour expressions were found return false
#
#         return False, None, None, None  # if no 2 digit hour expressions were found return false
#     else:
#
#         return False, None, None, None  # if the text_list does not have any entries, return false
