## Class definitions to represent a temporalTime entity
#
# Date: 9/23/17
#
# Programmer Name: Amy Olex

import json

## Class to define a temporalTime entity parsed from the json output of temporalTime
# @author Amy Olex
# @param id Unique numerical ID
# @param text The text parsed out by temporalTime
# @param start_span The location of the first character
# @param end_span The location of the last character
# @param type The type of temporal entity parsed by temporalTime.  Can be one of DATE, TIME, SET, DURATION, RANGE...I think!
# @param value The normalized date/time value from temporalTime.
class temporalEntity :
    
    ## The constructor
    def __init__(self, id, text, start_span, end_span, temptype, tempvalue, doctime) :
        self.id = id
        self.text = text
        self.start_span = start_span
        self.end_span = end_span
        self.temptype = temptype
        self.tempvalue = tempvalue
        self.doctime = doctime
      
    ## String representation    
    def __str__(self) :
        span_str = "" if self.start_span is None else (" <" + str(self.start_span) + "," + str(self.end_span) + "> ")
        return(str(self.id) + " " + str(self.text) + span_str + str(self.temptype) + " " + str(self.tempvalue) + " " + str(self.doctime))
    

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
    #  @param temptype The type of temporalTime temporal expression
    def setType(self, temptype) :
        self.temptype = temptype
        
    ## Sets the entity's temporalTime normalized value
    #  @param tempvalue The entities normalized temporalTime value
    def setValue(self, tempvalue) :
        self.tempvalue = tempvalue
    
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
        
    ## Gets the entity's temptype
    def getType(self) :
        return(self.temptype)
        
    ## Gets the entity's tempvalue
    def getValue(self) :
        return(self.tempvalue)
    
    ## Gets the entity's doctime
    def getDoctime(self):
        return(self.doctime)

## Function to convert json output of temporaltime to a list of temporaltimeEntities
# @author Amy Olex
# @param tempt_json The TemporalTime parsed json string (required)
# @param id_counter The number the ID counter should start at. Default is 0.
# @return A list of temporalEntity objects in the same order as the input json list.
def import_TemporalTime(tempt_json, doctime = None, id_counter=0) :
    temp_list = []
    for j in tempt_json:
        temp_list.append(temporalEntity(id=id_counter, text=j['text'], start_span=j['start'], end_span=j['end'], temptype=j['type'], tempvalue=j['value'], doctime=doctime))
        id_counter = id_counter +1
        
    return temp_list

