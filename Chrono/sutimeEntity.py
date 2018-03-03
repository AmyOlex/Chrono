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

## Class to define a SUTime entity parsed from the json output of SUTime
# @author Amy Olex
# @param id Unique numerical ID
# @param text The text parsed out by SUTime
# @param start_span The location of the first character
# @param end_span The location of the last character
# @param type The type of temporal entity parsed by SUTime.  Can be one of DATE, TIME, SET, DURATION, RANGE...I think!
# @param value The normalized date/time value from SUTime.
class sutimeEntity :
    
    ## The constructor
    def __init__(self, id, text, start_span, end_span, sutype, suvalue, doctime) :
        self.id = id
        self.text = text
        self.start_span = start_span
        self.end_span = end_span
        self.sutype = sutype
        self.suvalue = suvalue
        self.doctime = doctime
      
    ## String representation    
    def __str__(self) :
        span_str = "" if self.start_span is None else (" <" + str(self.start_span) + "," + str(self.end_span) + "> ")
        return(str(self.id) + " " + str(self.text) + span_str + str(self.sutype)  + " " + str(self.suvalue) + " " + str(self.doctime))
    

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
    #  @param sutype The type of SUTime temporal expression
    def setType(self, sutype) :
        self.sutype = sutype
        
    ## Sets the entity's SUTime normalized value
    #  @param suvalue The entities normalized SUTime value
    def setValue(self, suvalue) :
        self.suvalue = suvalue
    
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
        
    ## Gets the entity's sutype
    def getType(self) :
        return(self.sutype)
        
    ## Gets the entity's suvalue
    def getValue(self) :
        return(self.suvalue)
    
    ## Gets the entity's doctime
    def getDoctime(self):
        return(self.doctime)

## Function to convert json output of sutime to a list of sutimeEntities
# @author Amy Olex
# @param sut_json The SUTime parsed json string (required)
# @param id_counter The number the ID counter should start at. Default is 0.
# @return A list of sutimeEntity objects in the same order as the input json list.
def import_SUTime(sut_json, doctime = None, id_counter=0) :
    su_list = []
    for j in sut_json:
        su_list.append(sutimeEntity(id=id_counter, text=j['text'], start_span=j['start'], end_span=j['end'], sutype=j['type'], suvalue=j['value'], doctime=doctime))
        id_counter = id_counter +1
        
    return su_list

