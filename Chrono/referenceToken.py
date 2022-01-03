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


## Class definitions to represent a whitespace-parsed token in the raw text file.


import string


## Class to define a whitespace-parsed token from raw text.
# @author Amy Olex
# @param id Unique numerical ID
# @param text The text of the token
# @param abs_start_span The location of the first character
# @param abs_end_span The location of the last character
# @param pos The part of speech assigned to this token
# @param temporal A boolean indicating if this token contains any temporal components
# @param sent_boundary A boolean indicating if this token is at the end of a sentence or line
class refToken:

    ## The constructor
    def __init__(self, id, rel_id, text, abs_start_span=None, abs_end_span=None, rel_start_span=None, rel_end_span=None, pos=None, temporal=None, numeric=None,
                 sent_boundary=None, sent_membership=None, link_term=None):
        self.id = id  ## essentially the absolute token index
        self.rel_id = rel_id
        self.text = text
        self.abs_start_span = abs_start_span
        self.abs_end_span = abs_end_span
        self.rel_start_span = rel_start_span
        self.rel_end_span = rel_end_span
        self.pos = pos
        self.temporal = temporal
        self.numeric = numeric
        self.sent_boundary = sent_boundary
        self.link_term = link_term
        self.sent_membership = sent_membership

    ## Defines how to convert a refToken to string
    def __str__(self):
        # return str(self.id) + " " + self.text
        span_str = "" if self.abs_start_span is None else (" <" + str(self.abs_start_span) + "," + str(self.abs_end_span) + "> ")
        pos_str = "" if self.pos is None else ("pos: " + self.pos)
        temp_str = "" if self.temporal is None else (" isTemp: " + str(self.temporal))
        num_str = "" if self.numeric is None else (" isNumeric: " + str(self.numeric))
        sentb_str = "" if self.sent_boundary is None else (" isEndSent: " + str(self.sent_boundary))
        linkt_str = "" if self.link_term is None else (" isLinkTerm: " + str(self.link_term))
        sentmem_str = "" if self.sent_membership is None else (" sent_membership: " + str(self.sent_membership))
        # return str(self.id) + " " + self.text
        return str(
            self.id) + " " + self.text + span_str + pos_str + temp_str + num_str + sentb_str + linkt_str + sentmem_str

    #### Methods to SET properties ###

    ## Sets the entity's ID
    #  @param id The ID to set it to
    def setID(self, id):
        self.id = id

    ## Sets the entity's text
    #  @param text The text to set it to
    def setText(self, text):
        self.text = text

    ## Sets the entity's span
    #  @param start The start index
    #  @param end The ending index
    def setSpan(self, start, end):
        self.abs_start_span = start
        self.abs_end_span = end

    ## Sets the entity's POS
    #  @param pos The part of speech assigned to the token
    def setPos(self, pos):
        self.pos = pos

    ## Sets the entity's temporal flag
    #  @param temp A boolean, 1 if it is a temporal token, 0 otherwise
    def setTemporal(self, temp):
        self.temporal = temp

    ## Sets the entity's numeric flag
    #  @param temp A boolean, 1 if it is a numeric token, 0 otherwise
    def setNumeric(self, num):
        self.numeric = num

    ## Sets the entity's sentence boundary flag
    #  @param temp A boolean, 1 if it is a numeric token, 0 otherwise
    def setSentBoundary(self, num):
        self.sent_boundary = num

    ## Sets the entity's link term flag
    #  @param temp A boolean, 1 if it is a numeric token, 0 otherwise
    def setLinkTerm(self, num):
        self.link_term = num

    def setSentMembership(self, sent_membership):
        self.sent_membership = sent_membership

    #### Methods to GET properties ####

    ## Gets the entity's ID
    def getID(self):
        return (self.id)

    ## Gets the entity's ID
    def getRelID(self):
        return (self.rel_id)

    ## Gets the entity's text
    def getText(self):
        return (self.text)

    ## Gets the entity's absolute character span
    def getSpan(self):
        return (self.abs_start_span, self.abs_end_span)

    ## Gets the entity's relative character span
    def getRelSpan(self):
        return (self.rel_start_span, self.rel_end_span)

    ## Gets the entity's POS
    def getPos(self):
        return (self.pos)

    ## Gets the entity's temporal flag
    def isTemporal(self):
        return (self.temporal)

    ## Gets the entity's numeric flag
    def isNumeric(self):
        return (self.numeric)

    ## Gets the entity's sentence boundary flag
    def getSentBoundary(self):
        return (self.sent_boundary)

    ## Gets the entity's link term flag
    def isLinkTerm(self):
        return (self.link_term)

    def getSentMembership(self):
        return (self.sent_membership)


    # Function to determine if the input span overlaps this objects span
    # @author Amy Olex
    # @param start
    # @param end
    # @output True or False
    def spanOverlap(self, start, end):
        if self.abs_start_span <= start and self.abs_end_span >= start:
            return True
        elif self.abs_end_span >= end and self.abs_start_span <= end:
            return True
        else:
            return False


## Function to convert a list of tokens into a list of refToken objects
# @author Amy Olex
# @param tok_list The list of tokens (required)
# @param id_counter The number the ID counter should start at. Default is 0.
# @param span A list of spans for each token in the tok_list. Must be the same length as tok_list. Assumes it is a one-to-one relationship in the same order as tok_list.
# @param pos A list of part-of-speech tags for each token in the tok_list. list. Must be the same length as tok_list. Assumes it is a one-to-one relationship in the same order as tok_list.
# @param temporal A boolean list of 0's and 1' indicating which token contains temporal information. Must be the same length as tok_list. Assumes it is a one-to-one relationship in the same order as tok_list.
# @param remove_stopwords A boolean that, if true, removes tokens in the stopword list.  Defaults to False.
# @return A list of refToken objects in the same order as the input tok_list.
def convertToRefTokens(tok_list, id_counter=0, rel_id_counter=0, abs_span=None, rel_span=None, pos=None, temporal=None, remove_stopwords=None,
                       sent_boundaries=None, sent_membership=None, link_term=None):
    ref_list = list()
    tok_len = len(tok_list)  #total number of tokens in list.
    ## figure out which lists were sent in
    include = [1, 0, 0, 0, 0, 0, 0, 0]
    if abs_span is not None:
        if len(abs_span) == tok_len:
            include[1] = 1
        else:
            raise ValueError('abs_span list is not same length as token list.')

    if rel_span is not None:
        if len(rel_span) == tok_len:
            include[2] = 1
        else:
            raise ValueError('rel_span list is not same length as token list.')

    if pos is not None:
        if len(pos) == tok_len:
            include[3] = 1
        else:
            raise ValueError('pos list is not same length as token list.')

    if temporal is not None:
        if len(temporal) == tok_len:
            include[4] = 1
        else:
            raise ValueError('temporal list is not same length as token list.')

    if sent_boundaries is not None:
        if len(sent_boundaries) == tok_len:
            include[5] = 1
        else:
            raise ValueError('sentence boundary flag array is not same length as token list.')

    if link_term is not None:
        if len(link_term) == tok_len:
            include[6] = 1
        else:
            raise ValueError('sentence boundary flag array is not same length as token list.')

    if sent_membership is not None:
        if len(sent_membership) == tok_len:
            include[7] = 1
        else:
            raise ValueError('sentence membership flag array is not same length as token list.')


    for idx in range(0, tok_len):
        ## if we have a new sentence
        if idx > 0 and sent_membership[idx] - sent_membership[idx-1] == 1:
            rel_id_counter = 0
        ref_list.append(refToken(id=id_counter, rel_id=rel_id_counter, text=tok_list[idx],
                                 abs_start_span=abs_span[idx][0] if include[1] else None,
                                 abs_end_span=abs_span[idx][1] if include[1] else None,
                                 rel_start_span=rel_span[idx][0] if include[2] else None,
                                 rel_end_span=rel_span[idx][1] if include[2] else None,
                                 pos=pos[idx][1] if include[3] else None,
                                 temporal=temporal[idx] if include[4] else None,
                                 sent_boundary=sent_boundaries[idx] if include[5] else None,
                                 link_term=link_term[idx] if include[6] else None,
                                 sent_membership=sent_membership[idx] if include[7] else None))
        id_counter = id_counter + 1
        rel_id_counter = rel_id_counter + 1

    if remove_stopwords is not None:
        ref_list = removeStopWords(ref_list, remove_stopwords)

    return ref_list


## Function to remove stopwords from a list of refToken objects
# @author Luke Maffey
# @param tok_list The list of tokens (required)
# @param stopwords_path The file with stopwords, defaults to "./stopwords_short"
# @return A list of refTokens in the same order as the input tok_list with stopwords removed

def removeStopWords(tok_list, stopwords_path="./stopwords_short"):
    with open(stopwords_path) as raw:
        stopwords = raw.read().splitlines()

    filtered_tokens = []
    for tok in tok_list:
        if tok.getText().lower() not in stopwords:
            filtered_tokens.append(tok)

    return filtered_tokens


## Function to remove all punctuation from a list of refToken objects
# @author Amy Olex
# @param tok_list The list of tokens (required)
# @return A list of refTokens in the same order as the input tok_list with punctuation removed

def replacePunctuation(tok_list):
    for t in range(0, len(tok_list)):
        tok_list[t].setText(tok_list[t].getText().translate(str.maketrans("", "", string.punctuation)))

    return tok_list


## Function to convert all refToken objects to lowercase
# @author Amy Olex
# @param tok_list The list of tokens (required)
# @return A list of refTokens in the same order as the input tok_list converted to lowercase

def lowercase(tok_list):
    for t in range(0, len(tok_list)):
        tok_list[t].setText(tok_list[t].getText().lower())

    return tok_list
