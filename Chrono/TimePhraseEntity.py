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


## Class definitions to represent a temporal phrase

import json
import dateutil.parser as dp
from datetime import timedelta as td
import datetime
from Chrono import utils

## Class to define a TimePhrase entity parsed from the json output of TimePhrase
# @author Amy Olex
# @param id Unique numerical ID
# @param text The text parsed out by TimePhrase
# @param start_span The location of the first character
# @param end_span The location of the last character
# @param type The type of temporal entity parsed by TimePhrase.  Can be one of DATE, TIME, SET, DURATION, RANGE...I think!
# @param value The normalized date/time value from TimePhrase.
class TimePhraseEntity :
    
    ## The constructor
    def __init__(self, id, text, start_span, end_span, type, mod, value, doctime) :
        self.id = id
        self.text = text
        self.start_span = start_span
        self.end_span = end_span
        self.type = type
        self.mod = mod
        self.value = value
        self.doctime = doctime
      
    ## String representation    
    def __str__(self) :
        span_str = "" if self.start_span is None else (" <" + str(self.start_span) + "," + str(self.end_span) + "> ")
        return(str(self.id) + " " + str(self.text) + span_str + " Type: " +str(self.type) + " Mod: " +str(self.mod) + " Value: " + str(self.value) + " DocTime: " + str(self.doctime))
    

    #### Methods to SET properties ###
    
    ## Sets the entity's ID
    #  @param id The ID to set it to
    def setID(self, id) :
        self.id = id

    ## Sets the entity's text
    #  @param text The text to set it to
    def setText(self, text) :
        self.text = text
        
    ## Sets the entity's span
    #  @param start The start index
    #  @param end The ending index
    def setSpan(self, start, end) :
        self.start_span = start
        self.end_span = end
        
    ## Sets the entity's type
    #  @param type The type of TimePhrase temporal expression
    def setType(self, type) :
        self.type = type
        
    ## Sets the entity's modifier
    #  @param mod The modifier of TimePhrase temporal expression
    def setMod(self, mod) :
        self.mod = mod
        
    ## Sets the entity's TimePhrase normalized value (this is in ISO format)
    #  @param value The entities normalized TimePhrase value
    def setValue(self, value) :
        self.value = value
    
    def setDoctime(self, doctime) :
        self.doctime = doctime
        
    #### Methods to GET properties ####
    
    ## Gets the entity's ID
    def getID(self) :
        return(self.id)
        
    ## Gets the entity's text
    def getText(self) :
        return(self.text)
        
    ## Gets the entity's span
    def getSpan(self) :
        return(self.start_span, self.end_span)
        
    ## Gets the entity's type
    def getType(self) :
        return(self.type)
        
    ## Gets the entity's modifier
    def getMod(self) :
        return(self.mod)
        
    ## Gets the entity's value
    def getValue(self) :
        return(self.value)
    
    ## Gets the entity's doctime
    def getDoctime(self):
        return(self.doctime)
    
    ## Print i2b2 format
    def i2b2format(self):
        #<TIMEX3 id="T0" start="18" end="26" text="10/17/95" type="DATE" val="1995-10-17" mod="NA" />
    
        return("<TIMEX3 id=\"T" + str(self.id) + "\" start=\"" + str(self.start_span) + "\" end=\"" + str(self.end_span) + "\" text=\"" + str(self.text) + "\" type=\"" + str(self.type) + "\" val=\"" + str(self.value) + "\" mod=\"" + str(self.mod) + "\" />")
        
        
    
    ## Uses the parsed Chrono entities to create the ISO value   
    def getISO(self, chronolist):
        
        mytype = "TIME"
        mymod = "NA"
        
        for e in chronolist:
            print("ENTITY: " + str(e))
        
        #determine which types are in the phrase
        #year,month,day,hour,minute,second,daypart,dayweek,interval,period,nth,nxt,this,tz,ampm,modifier,last = utils.getEntityValues(chronolist)
        year,month,day,hour,minute,second,daypart,dayweek,interval,period,nth,nxt,thisx,tz,ampm,modifier,lastx = utils.getPhraseEntities(chronolist)
        
        
        
        yearV = year.get_value() if year else ""
        monthV = month.get_value() if month else ""
        dayV = day.get_value() if day else ""
        hourV = hour.get_value() if hour else ""
        minuteV = minute.get_value() if minute else ""
        secondV = second.get_value() if second else ""

        print("Year Value: " + str(yearV))
        print("Month Value: " + str(monthV))
        print("Day Value: " + str(dayV))


        daypartV = daypart.get_value() if daypart else ""
        dayweekV = dayweek.get_value() if dayweek else ""
        intervalV = interval.get_value() if interval else ""
        periodV = period.get_value() if period else ""
        nthV = nth.get_value() if nth else ""
        nxtV = nxt.get_value() if nxt else ""
        thisV = thisx.get_value() if thisx else ""
        tzV = tz.get_value() if tz else ""
        ampmV = ampm.get_value() if ampm else ""
        modifierV = modifier.get_value() if modifier else ""
        lastV = lastx.get_value() if lastx else ""
        
        ## convert hour to 24 hour time if needed.
        ## If flag is zero then no addition will be made, but if 1 then 12 hours will be added anytime the hour entitiy is used.
        hour_flag = 0
        if hour and ampm:
            if ampmV == "PM" and int(hour.get_value()) < 12:
                print("Converting hour to 24-hour time.")
                hourV = int(hour.get_value()) + 12
                
            

        iso = ""
        
        ## Convert dates and times
        try:
            #if month or day or year or hour or minute or second:
            tmpdate = dp.parse(self.text, fuzzy = True, default=self.doctime)
            #    print("First date parse attempt: " + str(tmpdate))
            #else:
            #    tmpdate = ""
            print("TMPDATE IS: " + str(tmpdate.isoformat()))
           
        except:
            if month or day or year or hour or minute or second:
                mytext = str(monthV) + " " + str(dayV) + ", " + str(yearV) + " " + str(hourV) + ":" + str(minuteV) + ":" + str(secondV)
                print("My Full Date Text is: " + mytext)
                tmpdate = dp.parse(mytext, fuzzy = True, default=self.doctime)

            else:
                tmpdate = ""
        else:
            ### This code does not work.  It gets overwritten by the interval or period control below.  I need to figure this out.
            if lastx and period:
                print("HELLO LASTX")
                if periodV in "Weeks" or dayweek:
                    print("try parsing Weeks: " + self.text)
                    tmpdate = dp.parse(self.text, fuzzy = True, default=self.doctime - td(days=7))
                elif periodV in "Months":
                    print("try parsing Months: " + self.text)
                    tmpdate = dp.parse(self.text, fuzzy = True, default=self.doctime - td(days=30))
                elif periodV in "Years":
                    print("try parsing Years: " + self.text)
                    tmpdate = dp.parse(self.text, fuzzy = True, default=self.doctime - td(days=365))
                else:
                    print("assume 7 days: " + self.text)
                    tmpdate = dp.parse(self.text, fuzzy = True, default=self.doctime - td(days=7))
        finally:
            
            if month and day and year and not (hour or minute or second):
                print("hello1")
                m = tmpdate.month
                y = tmpdate.year
                d = tmpdate.day
                if m < 10:
                    m = "0" + str(m)
                if d < 10:
                    d = "0" + str(d)
                iso = str(y) + "-" + str(m) + "-" + str(d)
                mytype = "DATE"
                
            elif month and year and not day:
                print("hello2")
                m = tmpdate.month
                y = tmpdate.year
                if m < 10:
                    m = "0" + str(m)
                iso = str(y) + "-" + str(m)
                mytype = "DATE"
                
            elif year and not (day or month):
                print("hello3")
                iso = str(tmpdate.year)
                mytype = "DATE"
            elif dayweek:
                print("hello4")
                iso = str(dp.parse(self.text, fuzzy = True, default=self.doctime).isoformat())
                mytype = "DATE"
            elif tmpdate:
                print("hello5")
                print(str(tmpdate))
                iso = tmpdate.isoformat()
                mytype = "DATE"
                print("GOOD: " + str(iso))
            else:
                print("hello6")
                print("tmpdate should be blank: " + tmpdate)
                iso = tmpdate
            
            
            ## Convert periods and intervals that do not have dates and times.
            ## year,month,day,hour,minute,second,daypart,dayweek,interval,period,nth,nxt,this,tz,ampm,modifier,last
            
            ## low hanging fruit, periods and intervals
            ## I will have to pull out Frequency from this as the term "daily" is a frequency, but will work on that later.
            
            if interval or period:
                print("HELLO DURATION")
                mytype = "DURATION"
                
                if interval:
                    duration = interval.get_value()
                    dtime,mymod = utils.getPhraseNumber(self.text, chronolist, interval.get_number())
                    print("INTERVAL HERE: " + str(duration) + " Num: " + str(dtime))

                else:
                    duration = period.get_value()
                    dtime,mymod = utils.getPhraseNumber(self.text, chronolist, period.get_number())
                    print("PERIOD HERE: " + str(duration) + " Num: " + str(dtime))

                if duration in "Days" and dtime:
                    iso = "P" + str(dtime) + "D"
                if duration in "Weeks" and dtime:
                    iso = "P" + str(dtime) + "W"
                if duration in "Months" and dtime:
                    iso = "P" + str(dtime) + "M"
                if duration in "Years" and dtime:
                    iso = "P" + str(dtime) + "Y"
                if duration in "Hours" and dtime:
                    iso = "PT" + str(dtime) + "H"
                if duration in "Minutes" and dtime:
                    iso = "PT" + str(dtime) + "M"
                if duration in "Seconds" and dtime:
                    iso = "PT" + str(dtime) + "S"
                if duration in "Decades" and dtime:
                    iso = "P" + str(int(dtime) * 10) + "Y"
                if duration in "Century" and dtime:
                    iso = "P100Y"
                if duration in "Centuries" and dtime:
                    iso = "P" + str(int(dtime) * 100) + "Y"
                if duration in "Day" and dtime:
                    iso = "P" + str(dtime) + "D"
                if duration in "Week" and dtime:
                    iso = "P" + str(dtime) + "W"
                if duration in "Month" and dtime:
                    iso = "P" + str(dtime) + "M"
                if duration in "Year" and dtime:
                    iso = "P" + str(dtime) + "Y"
                if duration in "Hour" and dtime:
                    iso = "PT" + str(dtime) + "H"
                if duration in "Minute" and dtime:
                    iso = "PT" + str(dtime) + "M"
                if duration in "Second" and dtime:
                    iso = "PT" + str(dtime) + "S"
                if duration in "Decade" and dtime:
                    iso = "P" + str(int(dtime) * 10) + "Y"
                    
            if daypart:
                print("hello8")
                #look for last, this, or next
                print("Found Daypart: " + str(daypart) + " " + str(daypartV) + " " + self.text.lower())
                if "night" in self.text.lower() and "over" in self.text.lower():
                    mytype = "DURATION"
                    iso = "PT12H"
                #elif lastx:
                #    print("Found LAST: " + str(lastx) + str(lastV))
                #    mytype = "DATE"
                #    iso = (self.doctime - td(days=1)).isoformat()
                #elif nxt:
                #    print("Found NEXT: " + str(nxt) + str(nxtV))
                #    mytype = "DATE"
                #    iso = (self.doctime + td(days=1)).isoformat()
                else:
                    #assume it is this or doesn't have a modifier.
                    mytype = "DATE"
                    iso = (self.doctime).isoformat()
                    
            
            #if the ISO value has T00:00:00 in it, remove it.
            self.value = iso.replace("T00:00:00", "")
            self.type = mytype
            self.mod = mymod
            print("MY ISO:::: " + iso)
             
            
            
            
               
    
    
        
## Function to convert json output of TimePhrase to a list of TimePhraseEntities
# @author Amy Olex
# @param tempt_json The TimePhrase parsed json string (required)
# @param id_counter The number the ID counter should start at. Default is 0.
# @return A list of TimePhraseEntity objects in the same order as the input json list.
def import_TimePhrase(tempt_json, doctime = None, id_counter=0) :
    temp_list = []
    for j in tempt_json:
        temp_list.append(TimePhraseEntity(id=id_counter, text=j['text'], start_span=j['start'], end_span=j['end'], type=j['type'], value=j['value'], doctime=doctime))
        id_counter = id_counter +1
        
    return temp_list



