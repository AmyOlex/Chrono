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
    def __init__(self, id, text, start_span, end_span, type, value, doctime) :
        self.id = id
        self.text = text
        self.start_span = start_span
        self.end_span = end_span
        self.type = type
        self.value = value
        self.doctime = doctime
      
    ## String representation    
    def __str__(self) :
        span_str = "" if self.start_span is None else (" <" + str(self.start_span) + "," + str(self.end_span) + "> ")
        return(str(self.id) + " " + str(self.text) + span_str + " Type: " +str(self.type) + " Value: " + str(self.value) + " DocTime: " + str(self.doctime))
    

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
        
    ## Gets the entity's value
    def getValue(self) :
        return(self.value)
    
    ## Gets the entity's doctime
    def getDoctime(self):
        return(self.doctime)
    
    ## Uses the parsed Chrono entities to create the ISO value   
    def getISO(self, chronolist):
        #determine which types are in the phrase
        year,month,day,hour,minute,second,daypart,dayweek,interval,period,nth,nxt,this,tz,ampm,modifier,last = utils.getEntityValues(chronolist)
        
        ## convert hour to 24 hour time if needed
        if hour and ampm:
            if ampm == "PM" and int(hour) < 12:
                print("Converting hour to 24-hour time.")
                hour = int(hour) + 12

        iso = ""
        try:
            iso = dp.parse(self.text, fuzzy = True, default=self.doctime)
        except:
            if month or day or year or hour or minute or second:
                mytext = str(month) + " " + str(day) + ", " + str(year) + " " + str(hour) + ":" + str(minute) + ":" + str(second)
                print("My Full Date Text is: " + mytext)
                iso = dp.parse(mytext, fuzzy = True, default=self.doctime)
            else:
                iso = ""
        else:
            if last:
                iso = dp.parse(self.text, fuzzy = True, default=self.doctime - td(days=7))
        finally:
            print("MY ISO:::: " + str(iso))
            self.value = iso
        
        
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



