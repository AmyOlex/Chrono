###############################
# Programmer Name: Amy Olex
# Date: 9/16/17
# Module Purpose: Provides all helper functions for task6 project.  These can be seperated into files later if needed.
#################################

import nltk
from nltk.tokenize import WhitespaceTokenizer
from task6 import t6Entities as t6
import dateutil.parser
import datetime
from task6 import SUTime_To_T6
import re

## getWhitespaceTokens(): Pasrses a text file to idenitfy all tokens seperated by white space with their original file span coordinates.
# @author Amy Olex
# @param file_path The path and file name of the text file to be parsed.
# @output text String containing the raw text blob from reading in the file.
# @output tokenized_text A list containing each token that was seperated by white space.
# @output spans The coordinates for each token.
def getWhitespaceTokens(file_path):
    file = open(file_path, "r")
    text = file.read()
    span_generator = WhitespaceTokenizer().span_tokenize(text)
    spans = [span for span in span_generator]
    tokenized_text = WhitespaceTokenizer().tokenize(text)
    return text, tokenized_text, spans

## getDocTime(): Reads in the dct file and converts it to a datetime object.
# @author Amy Olex
# @param file_path The path and file name of the dct file.
# @output A datetime object
def getDocTime(file_path):
    file = open(file_path, "r")
    text = file.read()
    return(dateutil.parser.parse(text))

## manualT6AddEntities(): Manually creates the wsj_0152 t6Entity data
# @author Amy Olex
# @output A list of t6 entity objects
def manualT6AddEntities(t6list):
    t6list.append(t6.T6HourOfDayEntity(entityID=32, start_span=393, end_span=394, value=5, ampm=40, time_zone=35,sub_interval=None, number=None, modifier=None))
    t6list.append(t6.T6MonthOfYearEntity(entityID=33, start_span=12, end_span=14, month_type="November",sub_interval=41, number=None, modifier=None))
    t6list.append(t6.T6MonthOfYearEntity(entityID=34, start_span=536, end_span=540, month_type="November",sub_interval=42, number=None, modifier=None))
    t6list.append(t6.T6TimeZoneEntity(entityID=35, start_span=400, end_span=403))
    t6list.append(t6.T6MonthOfYearEntity(entityID=36, start_span=145, end_span=149, month_type="November",sub_interval=37, number=None, modifier=None))
    t6list.append(t6.T6DayOfMonthEntity(entityID=37, start_span=150, end_span=151, value=6,sub_interval=None, number=None, modifier=None))
    t6list.append(t6.T6MonthOfYearEntity(entityID=38, start_span=152, end_span=154, month_type="November",sub_interval=39, number=None, modifier=None))
    t6list.append(t6.T6DayOfMonthEntity(entityID=39, start_span=155, end_span=157, value=2,sub_interval=None, number=None, modifier=None))
    t6list.append(t6.T6AMPMOfDayEntity(entityID=40, start_span=395, end_span=399, ampm_type="PM", number=None, modifier=None))
    t6list.append(t6.T6DayOfMonthEntity(entityID=41, start_span=15, end_span=17, value=2,sub_interval=None, number=None, modifier=None))
    t6list.append(t6.T6DayOfMonthEntity(entityID=42, start_span=541, end_span=542, value=6,sub_interval=None, number=None, modifier=None))
    t6list.append(t6.T6TwoDigitYearOperator(entityID=43, start_span=158, end_span=160, value=89, sub_interval=38))
    t6list.append(t6.T6MonthOfYearEntity(entityID=44, start_span=404, end_span=408, month_type="November",sub_interval=45, number=None, modifier=None))
    t6list.append(t6.T6DayOfMonthEntity(entityID=45, start_span=409, end_span=410, value=9,sub_interval=32, number=None, modifier=None))
    t6list.append(t6.T6TwoDigitYearOperator(entityID=46, start_span=18, end_span=20, value=89, sub_interval=33))
    t6list.append(t6.T6NextOperator(entityID=47, start_span=145, end_span=149, period=None, repeating_interval=36))
    t6list.append(t6.T6NextOperator(entityID=48, start_span=404, end_span=408, period=None, repeating_interval=44))
    t6list.append(t6.T6NextOperator(entityID=49, start_span=536, end_span=540, period=None, repeating_interval=34))
    t6list.append(t6.T6BetweenOperator(entityID=50, start_span=139, end_span=144, start_interval_type="DocTime", end_interval_type="Link", end_interval=47))
    t6list.append(t6.T6BetweenOperator(entityID=51, start_span=387, end_span=392, start_interval_type="DocTime", end_interval_type="Link", end_interval=48))
    
    return(t6list)
    
## write_xml(): Writes out the full XML file for all T6entities in list.
# @author Amy Olex
# @param t6list The list of T6 objects needed to be written in the file.
# @param outfile A string containing the output file location and name.
def write_xml(t6list, outfile):
    fout = open(outfile + ".completed.xml", "w")
    fout.write("<data>\n<annotations>\n")
    for t6 in t6list :
        fout.write(str(t6.print_xml()))
    
    fout.write("\n</annotations>\n</data>")
    fout.close()
    


## buildDayOfWeek(): Parses out all sutime entities that contain a day of the week written out in text form
# @author Amy Olex
# @param t6list The list of T6 objects we currently have.  Will add to these.
# @param suList The list of SUtime entities to parse
def buildDayOfWeek(t6list, t6idCounter, suList):
    
    ## Test out the identification of days
    for s in suList :
        boo, val, idxstart, idxend = SUTime_To_T6.hasDayOfWeek(s)
        if boo:
            ref_Sspan, ref_Espan = s.getSpan()
            abs_Sspan = ref_Sspan + idxstart
            abs_Espan = ref_Sspan + idxend
            my_entity = t6.T6DayOfWeekEntity(entityID=str(t6idCounter)+"entity", start_span=abs_Sspan, end_span=abs_Espan, day_type=val)
            t6list.append(my_entity)
            t6idCounter = t6idCounter+1
            #check here to see if it has a modifier
            hasMod, mod_type, mod_start, mod_end = SUTime_To_T6.hasModifier(s)
            if(hasMod):
                if mod_type == "This":
                    t6list.append(t6.T6ThisOperator(entityID=t6idCounter, start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                    t6idCounter = t6idCounter+1
                    
                if mod_type == "Next":
                    t6list.append(t6.T6NextOperator(entityID=t6idCounter, start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                    t6idCounter = t6idCounter+1
                    
                if mod_type == "Last":
                    t6list.append(t6.T6LastOperator(entityID=t6idCounter, start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                    t6idCounter = t6idCounter+1
                else:
                    t6list.append(t6.T6LastOperator(entityID=t6idCounter, start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                    t6idCounter = t6idCounter+1
                    
            else:
                t6list.append(t6.T6LastOperator(entityID=t6idCounter, start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                t6idCounter = t6idCounter+1
        
            
    return t6list, t6idCounter
    


## buildTextMonth(): Parses out all sutime entities that contain a month of the year written out in text form
# @author Amy Olex
# @param t6list The list of T6 objects we currently have.  Will add to these.
# @param suList The list of SUtime entities to parse
def buildTextMonthAndDay(t6list, t6idCounter, suList):
    
    ## Test out the identification of days
    for s in suList :
        boo, val, idxstart, idxend = SUTime_To_T6.hasTextMonth(s)
        if boo:
            ref_Sspan, ref_Espan = s.getSpan()
            abs_Sspan = ref_Sspan + idxstart
            abs_Espan = ref_Sspan + idxend
            my_month_entity = t6.T6MonthOfYearEntity(entityID=str(t6idCounter)+"entity", start_span=abs_Sspan, end_span=abs_Espan, month_type=val)
            t6idCounter = t6idCounter+1
            
            #check to see if it has a day associated with it.  We assume the day comes after the month.
            #idx_end is the last index of the month.  If there are any characters after it the lenght of the string will be greater than the endidx.
            if(idxend < len(s.getText())):
                m = re.search('([0-9]{1,2})', s.getText()[idxend:len(s.getText())])
                day_val = m.group(0)
                print("DAY VALUE: " + day_val + "\nFULL TEXT: " + s.getText())
                day_startidx, day_endidx = SUTime_To_T6.getSpan(s.getText(), day_val)
                abs_Sspan = ref_Sspan + day_startidx
                abs_Espan = ref_Sspan + day_endidx
                
                my_day_entity = t6.T6DayOfMonthEntity(entityID=str(t6idCounter)+"entity", start_span=abs_Sspan, end_span=abs_Espan, value=day_val)
                t6list.append(my_day_entity)
                t6idCounter = t6idCounter+1
                #now link the month to the day
                my_month_entity.set_sub_interval(my_day_entity.get_id())
            
            t6list.append(my_month_entity)
        
            
    return t6list, t6idCounter
 
 
## buildAMPM(): Parses out all sutime entities that contain a AM or PM time indication
# @author Amy Olex
# @param t6list The list of T6 objects we currently have.  Will add to these.
# @param suList The list of SUtime entities to parse
def buildAMPM(t6list, t6idCounter, suList):
    
    ## Test out the identification of days
    for s in suList :
        ref_Sspan, ref_Espan = s.getSpan()
        ## Identify if a time zone string exists
        tz = SUTime_To_T6.hasTimeZone(s)
        if tz is not None:
            my_tz_entity = t6.T6TimeZoneEntity(str(t6idCounter)+"entity", start_span = tz.span(0)[0]+ref_Sspan, end_span=tz.span(0)[1]+ref_Sspan)
            t6list.append(my_tz_entity)
            t6idCounter = t6idCounter+1
        else:
            my_tz_entity = None
         
        boo, val, idxstart, idxend = SUTime_To_T6.hasAMPM(s)
        if boo:
            abs_Sspan = ref_Sspan + idxstart
            abs_Espan = ref_Sspan + idxend
            my_AMPM_entity = t6.T6AMPMOfDayEntity(entityID=str(t6idCounter)+"entity", start_span=abs_Sspan, end_span=abs_Espan, ampm_type=val)
            t6idCounter = t6idCounter+1
            t6list.append(my_AMPM_entity)
            
            #check to see if it has a time associated with it.  We assume the time comes before the AMPM string
            #We could parse out the time from the sutime normalized value.  The problem is getting the correct span.
            #idx_start is the first index of the ampm.  If there are any characters before it, it will be greater than 0.
            if idxstart > 0:
                m = re.search('([0-9]{1,2})', s.getText()[0:idxstart])
                if m is not None :
                    hour_val = m.group(0)
                    abs_Sspan = ref_Sspan + m.span(0)[0]
                    abs_Espan = ref_Sspan + m.span(0)[1]
                
                    my_hour_entity = t6.T6HourOfDayEntity(entityID=str(t6idCounter)+"entity", start_span=abs_Sspan, end_span=abs_Espan, value=hour_val, ampm=my_AMPM_entity.get_id())
                     
                    t6idCounter = t6idCounter+1
                     
                    if my_tz_entity is not None:
                        my_hour_entity.set_time_zone(my_tz_entity.get_id())
                    
                    #add the hour entity to the list
                    t6list.append(my_hour_entity)
                         

            
    return t6list, t6idCounter
    

## markTemporalRefToks(): Marks all the reference tokens that show up in the SUTime entity list.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @param suList The list of SUtime entities to compare against
def markTemporalRefToks(refToks, suList):
    for ref in refToks:
        for su in suList:
            suStart, suEnd = su.getSpan()
            if ref.spanOverlap(suStart, suEnd):
                ref.setTemporal(True)
        if ref.isTemporal() is None:
            ref.setTemporal(False)
    return refToks

    
    
    
    
    
    
    
    
    
    