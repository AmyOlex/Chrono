## Class definitions to represent a whitespace-parsed token in the raw text file.
#
# Date: 9/19/17
#
# Programmer Name: Amy Olex

import string

## Class to define a whitespace-parsed token from raw text.
# @author Amy Olex
# @param id Unique numerical ID
# @param text The text of the token
# @param start_span The location of the first character
# @param end_span The location of the last character
# @param pos The part of speech assigned to this token
# @param temporal A boolean indicating if this token contains any temporal components
class refToken :

    ## The constructor
    def __init__(self, id, text, start_span=None, end_span=None, pos=None, temporal=None, t6list=None, numeric=None) :
        self.id = id
        self.text = text
        self.start_span = start_span
        self.end_span = end_span
        self.pos = pos
        self.temporal = temporal
        self.numeric = numeric
        self.t6list = t6list

    ## Defines how to convert a refToken to string
    def __str__(self) :
        #return str(self.id) + " " + self.text
        span_str = "" if self.start_span is None else (" <" + str(self.start_span) + "," + str(self.end_span) + "> ")
        pos_str = "" if self.pos is None else ("pos: " + self.pos)
        temp_str = "" if self.temporal is None else (" isTemp: " + str(self.temporal))
        num_str = "" if self.numeric is None else (" isNumeric: " + str(self.numeric))
        t6_str = "" if self.t6list is None else (" T6List: " + str(self.t6list))
        #return str(self.id) + " " + self.text
        return str(self.id) + " " + self.text + span_str + pos_str  + temp_str + num_str + t6_str

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
        
    ## Sets the entity's POS
    #  @param pos The part of speech assigned to the token
    def setPos(self, pos) :
        self.pos = pos
        
    ## Sets the entity's temporal flag
    #  @param temp A boolean, 1 if it is a temporal token, 0 otherwise
    def setTemporal(self, temp) :
        self.temporal = temp
    
    ## Sets the entity's numeric flag
    #  @param temp A boolean, 1 if it is a numeric token, 0 otherwise
    def setNumeric(self, num) :
        self.numeric = num

    ## Adds to the entities list of T6 entities
    #  @param t6id an integer of the t6 entities ID
    def t6Append(self, t6id) :
        if self.t6list is None :
            self.t6list = []
            self.t6list.append(t6id)
        else :
            self.t6list.append(t6id)


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
        
    ## Gets the entity's POS
    def getPos(self) :
        return(self.pos)
        
    ## Gets the entity's temporal flag
    def isTemporal(self) :
        return(self.temporal)
        
    ## Gets the entity's numeric flag
    def isNumeric(self) :
        return(self.numeric)

    ## Gets the entity's t6list
    def getT6list(self) :
        return(self.t6list)
        
    ## Function to determine if the input span overlaps this objects span
    # @author Amy Olex
    # @param start
    # @param end
    # @output True or False
    def spanOverlap(self, start, end) :
        if self.start_span<=start and self.end_span >=start:
            return True
        elif self.end_span >=end and self.start_span <= end:
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
def convertToRefTokens(tok_list, id_counter=0, span=None, pos=None, temporal=None, remove_stopwords=None) :
    ref_list = list()
    tok_len = len(tok_list)
    ## figure out which lists were sent in
    include = [1, 0, 0, 0]
    if span is not None:
        if len(span)==tok_len:
            include[1]=1
        else:
            raise ValueError('span list is not same length as token list.')
              
    if pos is not None:
        if len(pos)==tok_len:
            include[2]=1
        else:
            raise ValueError('pos list is not same length as token list.')
        
    if temporal is not None:
        if len(temporal)==tok_len:
            include[3]=1
        else:
            raise ValueError('temporal list is not same length as token list.')
    
    
    for idx in range(0,tok_len):
        ref_list.append(refToken(id=id_counter, text=tok_list[idx], start_span=span[idx][0] if include[1] else None, end_span=span[idx][1] if include[1] else None, pos=pos[idx] if include[2] else None, temporal=temporal[idx] if include[3] else None))
        id_counter = id_counter +1
        
    if remove_stopwords is not None:
        ref_list = removeStopWords(ref_list, remove_stopwords)
        
    return ref_list

## Function to remove stopwords from a list of refToken objects
# @author Luke Maffey
# @param tok_list The list of tokens (required)
# @param stopwords_path The file with stopwords, defaults to "./stopwords_short"
# @return A list of refTokens in the same order as the input tok_list with stopwords removed

def removeStopWords(tok_list, stopwords_path="./stopwords_short") :
    with open(stopwords_path) as raw:
        stopwords = raw.read().splitlines()
    
    filtered_tokens = []
    for tok in tok_list :
        if tok.getText().lower() not in stopwords :
            filtered_tokens.append(tok) 
            
    return filtered_tokens
    
## Function to remove all punctuation from a list of refToken objects
# @author Amy Olex
# @param tok_list The list of tokens (required)
# @return A list of refTokens in the same order as the input tok_list with punctuation removed

def replacePunctuation(tok_list) :
    
    for t in range(0,len(tok_list)):
        tok_list[t].setText(tok_list[t].getText().translate(str.maketrans("", "", string.punctuation))) 
            
    return tok_list

## Function to convert all refToken objects to lowercase
# @author Amy Olex
# @param tok_list The list of tokens (required)
# @return A list of refTokens in the same order as the input tok_list converted to lowercase

def lowercase(tok_list) :
    
    for t in range(0,len(tok_list)):
        tok_list[t].setText(tok_list[t].getText().lower()) 
            
    return tok_list  
