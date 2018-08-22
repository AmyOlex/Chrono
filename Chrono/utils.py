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



## Provides all helper functions for Chrono methods.


## Parses a text file to idenitfy all sentences, then identifies all tokens in each sentence seperated by white space with their original file span coordinates.
# @author Amy Olex
# @param file_path The path and file name of the text file to be parsed.
# @return text String containing the raw text blob from reading in the file.
# @return tokenized_text A list containing each token that was seperated by white space.
# @return spans The coordinates for each token.


## Reads in the dct file and converts it to a datetime object.
# @author Amy Olex
# @param file_path The path and file name of the dct file.
# @return A datetime object


## Writes out the full XML file for all Chrono in list.
# @author Amy Olex
# @param chrono_list The list of Chrono objects needed to be written in the file.
# @param outfile A string containing the output file location and name.
####
 #END_MODULE
 ####

    
## Takes in a text string and returns the numerical value
# @author Amy Olex
# @param text The string containing our number
# @return value The numerical value of the text string, None is returned if there is no number
####
#END_MODULE
####  

## Function to identify an ordinal number
# @author Amy Olex
# @param text The text string to be tested for an ordinal.

####
#END_MODULE
####    
  
## Function to get the integer representation of a text month
# @author Amy Olex  
# @param text The text string to be converted to an integer.

## Function to determine if the input span overlaps this objects span
# @author Amy Olex
# @param sp1 a 2-tuple with the first start and end span
# @param sp2 a 2-tuple with the second start and end span
# @output True or False
# @author Amy Olex
# @param reftok_list The full document being parsed as a list of tokens.
# @param reftok_idx The index of the target token in the reference list.
# @param feature_dict A dictionary with the features to be extracted listed as the keys and the values all set to zero.
# @return A dictionary with the features as keys and the values set to 0 if not present, and 1 if present for the target word.
######
## END Function
###### 


## Function that get the list of features to extract from the input training data matrix file.
# @author Amy Olex
# @param data_file The name and path the the data file that contains the training matrix.  The first row is assumed to be the list of features.
# @return A dictionary with all the features stored as keys and the values set to zero.
######
## END Function
###### 


## Marks all the reference tokens that are identified as temporal.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @return modified list of reftoks
####
#END_MODULE
####

## Tests to see if the token is a number.
# @author Amy Olex
# @param tok The token string
# @return Boolean true if numeric, false otherwise
####
#END_MODULE
#### 


## Tests to see if the token is a temporal value.
# @author Amy Olex
# @param tok The token string
# @return Boolean true if temporal, false otherwise

####
#END_MODULE
#### 

## Takes in a Reference List that has had numeric and temporal tokens marked, and identifies all the 
## temporal phrases by finding consecutive temporal tokens.
# @author Amy Olex
# @param chroList The list of temporally marked reference tokens
# @return A list of temporal phrases for parsing

####
#END_MODULE
#### 


## Takes in a list of reference tokens identified as a temporal phrase and returns one TimePhraseEntity.
# @author Amy Olex
# @param items The list of reference tokesn
# @param counter The ID this TimePhrase entity should have
# @param doctime The document time.
# @return A single TimePhrase entity with the text span and string concatenated.

####
#END_MODULE
####   


## Takes in a reference list of tokens, a start span and an end span
# @author Amy Olex
# @param ref_list The list of reference tokens we want an index for.
# @param start_span The start span of the token we need to find in ref_list
# @param end_span The ending span of the token we need to find
# @return Returns the index of the ref_list token that overlaps the start and end spans provided, or -1 if not found.

####
#END_MODULE
####           

## Identifies the local span of the serach_text in the input "text"
# @author Amy Olex
# @param text The text to be searched
# @param search_text The text to search for.
# @return The start index and end index of the search_text string.

# http://ominian.com/2016/03/29/os-walk-for-pathlib-path/


## Marks all the reference tokens that show up in the TimePhrase entity list.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @param tpList The list of TimePhrase entities to compare against
### I don't think we need/use this any longer.  Maybe can be recycled for something else.
#def markTemporalRefToks(refToks, tpList):
#    for ref in refToks:
#        for tp in tpList:
#            tpStart, tpEnd = tp.getSpan()
#            if ref.spanOverlap(tpStart, tpEnd):
#                ref.setTemporal(True)
#        if ref.isTemporal() is None:
#            ref.setTemporal(False)
#    return refToks
####
#END_MODULE
####

