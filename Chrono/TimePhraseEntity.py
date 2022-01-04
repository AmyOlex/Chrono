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

import dateutil.parser as dp
from datetime import timedelta as td
from Chrono import utils
from Chrono.ChronoBert import bert_utils


## Class to define a TimePhrase entity parsed from the json output of TimePhrase
# @author Amy Olex
# @param id Unique numerical ID
# @param text The text parsed out by TimePhrase
# @param abs_start_span The location of the first character
# @param abs_end_span The location of the last character
# @param type The type of temporal entity parsed by TimePhrase.  Can be one of DATE, TIME, SET, DURATION, RANGE...I think!
# @param value The normalized date/time value from TimePhrase.
class TimePhraseEntity :
    
    ## The constructor
    def __init__(self, id, text, abs_start_span, abs_end_span, rel_start_span, rel_end_span,
                 abs_token_idx_start, abs_token_idx_end, rel_token_idx_start, rel_token_idx_end,
                 type, mod, value, doctime, sent_membership, sent_text) :
        self.id = id
        self.text = text
        self.abs_start_span = abs_start_span  # this is the character-level span, not token
        self.abs_end_span = abs_end_span  # this is the character-level span, not token
        self.rel_start_span = rel_start_span  # this is the character-level span, not token
        self.rel_end_span = rel_end_span  # this is the character-level span, not token
        self.abs_token_idx_start = abs_token_idx_start  # this is the token-level span
        self.abs_token_idx_end = abs_token_idx_end  # this is the token-level span
        self.rel_token_idx_start = rel_token_idx_start  # this is the token-level span
        self.rel_token_idx_end = rel_token_idx_end  # this is the token-level span
        self.type = type
        self.mod = mod
        self.value = value
        self.doctime = doctime
        self.sent_membership = sent_membership
        self.sent_text = sent_text
      
    ## String representation    
    def __str__(self) :
        span_str = "" if self.abs_start_span is None else (" <" + str(self.abs_start_span) + "," + str(self.abs_end_span) + "> ")
        return(str(self.id) + " " + str(self.text) + span_str + " Type: " +str(self.type) + " Mod: " +str(self.mod) + " Value: " + str(self.value) + " DocTime: " + str(self.doctime) + " sent_membership: " + str(self.sent_membership) + "\nFULL SENTENCE:\n" + str(self.sent_text))
    

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
        self.abs_start_span = start
        self.abs_end_span = end
        
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

    def setSentMembership(self, sent_membership) :
        self.sent_membership = sent_membership

    def setSentText(self, sent_text) :
        self.sent_text = sent_text
        
    #### Methods to GET properties ####
    
    ## Gets the entity's ID
    def getID(self) :
        return(self.id)
        
    ## Gets the entity's text
    def getText(self) :
        return(self.text)
        
    ## Gets the entity's span
    def getSpan(self) :
        return(self.abs_start_span, self.abs_end_span)

    ## Gets the entity's span
    def getRelSpan(self):
        return (self.rel_start_span, self.rel_end_span)

    ## Gets the entity's token abs span
    def getTokenSpan(self) :
        return(self.abs_token_idx_start, self.abs_token_idx_end)

    ## Gets the entity's token relative span
    def getTokenRelSpan(self):
        return (self.rel_token_idx_start, self.rel_token_idx_end)

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

    def getSentMembership(self):
        return(self.sent_membership)

    def getSentText(self):
        return(self.sent_text)
    
    ## Print i2b2 format
    def i2b2format(self):
        #<TIMEX3 id="T0" start="18" end="26" text="10/17/95" type="DATE" val="1995-10-17" mod="NA" />
    
        return("<TIMEX3 id=\"T" + str(self.id) + "\" start=\"" + str(self.abs_start_span) + "\" end=\"" + str(self.abs_end_span) + "\" text=\"" + str(self.text) + "\" type=\"" + str(self.type) + "\" val=\"" + str(self.value) + "\" mod=\"" + str(self.mod) + "\" />")
        
        
    
    ## Uses the parsed Chrono entities to create the ISO value
    # chronolist is a list of the SCATE entities for this phrase only.
    def getISO(self, chronolist, bert_model, bert_tokenizer, bert_classifier):
        
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

        #print("Year Value: " + str(yearV))
        #print("Month Value: " + str(monthV))
        #print("Day Value: " + str(dayV))


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
                #print("Converting hour to 24-hour time.")
                hourV = int(hour.get_value()) + 12
                
            

        iso = ""
        
        ## Convert dates and times
        try:
            #if month or day or year or hour or minute or second:
            tmpdate = dp.parse(self.text, fuzzy = True, default=self.doctime)
            #    #print("First date parse attempt: " + str(tmpdate))
            #else:
            #    tmpdate = ""
            #print("TMPDATE IS: " + str(tmpdate.isoformat()))
           
        except:
            if month or day or year or hour or minute or second:
                mytext = str(monthV) + " " + str(dayV) + ", " + str(yearV) + " " + str(hourV) + ":" + str(minuteV) + ":" + str(secondV)
                #print("My Full Date Text is: " + mytext)
                tmpdate = dp.parse(mytext, fuzzy = True, default=self.doctime)

            else:
                tmpdate = ""
        else:
            ### This code does not work.  It gets overwritten by the interval or period control below.  I need to figure this out.
            if lastx and period:
                #print("HELLO LASTX")
                if periodV in "Weeks" or dayweek:
                    #print("try parsing Weeks: " + self.text)
                    tmpdate = dp.parse(self.text, fuzzy = True, default=self.doctime - td(days=7))
                elif periodV in "Months":
                    #print("try parsing Months: " + self.text)
                    tmpdate = dp.parse(self.text, fuzzy = True, default=self.doctime - td(days=30))
                elif periodV in "Years":
                    #print("try parsing Years: " + self.text)
                    tmpdate = dp.parse(self.text, fuzzy = True, default=self.doctime - td(days=365))
                else:
                    #print("assume 7 days: " + self.text)
                    tmpdate = dp.parse(self.text, fuzzy = True, default=self.doctime - td(days=7))
        finally:
            
            if month and day and year and not (hour or minute or second):
                #print("hello1")
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
                #print("hello2")
                m = tmpdate.month
                y = tmpdate.year
                if m < 10:
                    m = "0" + str(m)
                iso = str(y) + "-" + str(m)
                mytype = "DATE"
                
            elif year and not (day or month):
                #print("hello3")
                iso = str(tmpdate.year)
                mytype = "DATE"
            elif dayweek:
                #print("hello4")
                iso = str(dp.parse(self.text, fuzzy = True, default=self.doctime).isoformat())
                mytype = "DATE"
            elif tmpdate:
                #print("hello5")
                #print(str(tmpdate))
                iso = tmpdate.isoformat()
                mytype = "DATE"
                #print("GOOD: " + str(iso))
            else:
                #print("hello6")
                #print("tmpdate should be blank: " + tmpdate)
                iso = tmpdate
            
            
            ## Convert periods and intervals that do not have dates and times.
            ## year,month,day,hour,minute,second,daypart,dayweek,interval,period,nth,nxt,this,tz,ampm,modifier,last
            
            ## low hanging fruit, periods and intervals
            ## I will have to pull out Frequency from this as the term "daily" is a frequency, but will work on that later.
            
            if interval or period:
                #print("HELLO DURATION")
                mytype = utils.bert_classify(self.rel_token_idx_start, self.rel_token_idx_end, self.sent_text,
                                          self.sent_membership, bert_model, bert_tokenizer, bert_classifier)


                if interval:
                    granulatiry = intervalV
                    dtime,na = utils.getPhraseNumber(self.text, chronolist, interval.get_number())
                    print("INTERVAL HERE: " + str(granulatiry) + " Num: " + str(dtime) + " Mod: " + str(mymod))

                else:
                    granulatiry = periodV
                    dtime,na = utils.getPhraseNumber(self.text, chronolist, period.get_number())
                    print("PERIOD HERE: " + str(granulatiry) + " Num: " + str(dtime) + " Mod: " + str(mymod))

                if mytype == "DATE":
                    #print("BERT Type is a DATE!!!\n")
                    delta = 0  # delta is at the granularity of days. If the granularity is hours, seconds or minutes, our day delta is going to be zero.

                    if granulatiry in "Days":
                        delta = 1
                    if granulatiry in "Weeks":
                        delta = 7
                    if granulatiry in "Months":
                        delta = 30
                    if granulatiry in "Years":
                        delta = 365

                    multiple = dtime if dtime else 1  # this is how many days, weeks, etc. set to 1 by default

                    direction = "FUTURE" if nxt or thisx else "PAST"

                    print("Modifier Value: " + str(modifierV))
                    print("Direction: " + str(direction))
                    print("Multiple: " + str(multiple))
                    print("Delta: " + str(delta))

                    if direction == "FUTURE":
                        iso = (self.doctime + td(days=int(delta)*int(multiple))).isoformat()
                    else:
                        iso = (self.doctime - td(days=int(delta)*int(multiple))).isoformat()

                if mytype == "DURATION":
                    if granulatiry in "Days" and dtime:
                        iso = "P" + str(dtime) + "D"
                    if granulatiry in "Weeks" and dtime:
                        iso = "P" + str(dtime) + "W"
                    if granulatiry in "Months" and dtime:
                        iso = "P" + str(dtime) + "M"
                    if granulatiry in "Years" and dtime:
                        iso = "P" + str(dtime) + "Y"
                    if granulatiry in "Hours" and dtime:
                        iso = "PT" + str(dtime) + "H"
                    if granulatiry in "Minutes" and dtime:
                        iso = "PT" + str(dtime) + "M"
                    if granulatiry in "Seconds" and dtime:
                        iso = "PT" + str(dtime) + "S"
                    if granulatiry in "Decades" and dtime:
                        iso = "P" + str(int(dtime) * 10) + "Y"
                    if granulatiry in "Century" and dtime:
                        iso = "P100Y"
                    if granulatiry in "Centuries" and dtime:
                        iso = "P" + str(int(dtime) * 100) + "Y"
                    if granulatiry in "Day" and dtime:
                        iso = "P" + str(dtime) + "D"
                    if granulatiry in "Week" and dtime:
                        iso = "P" + str(dtime) + "W"
                    if granulatiry in "Month" and dtime:
                        iso = "P" + str(dtime) + "M"
                    if granulatiry in "Year" and dtime:
                        iso = "P" + str(dtime) + "Y"
                    if granulatiry in "Hour" and dtime:
                        iso = "PT" + str(dtime) + "H"
                    if granulatiry in "Minute" and dtime:
                        iso = "PT" + str(dtime) + "M"
                    if granulatiry in "Second" and dtime:
                        iso = "PT" + str(dtime) + "S"
                    if granulatiry in "Decade" and dtime:
                        iso = "P" + str(int(dtime) * 10) + "Y"
                    
            if daypart:
                #print("hello8")
                #look for last, this, or next
                #print("Found Daypart: " + str(daypart) + " " + str(daypartV) + " " + self.text.lower())
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
        temp_list.append(TimePhraseEntity(id=id_counter, text=j['text'], abs_start_span=j['start'], abs_end_span=j['end'], type=j['type'], value=j['value'], doctime=doctime))
        id_counter = id_counter +1
        
    return temp_list



