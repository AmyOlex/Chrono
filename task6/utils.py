###############################
# Programmer Name: Amy Olex
# Date: 9/16/17
# Module Purpose: Provides all helper functions for task6 project.  These can be seperated into files later if needed.
#################################

import nltk
from nltk.tokenize import WhitespaceTokenizer

#### getWhitespaceTokens()
# Function Purpose: Pasrses a text file to idenitfy all tokens seperated by white space with their original file span coordinates.
# Input: String containing the location and name of the text file to be parsed.
# Outputs: 
#   text - String containing the raw text blob from reading in the file.
#   tokenized_text - a list containing each token that was seperated by white space.
#   spans - the coordinates for each token.
####
def getWhitespaceTokens(file_path):
    file = open(file_path, "r")
    text = file.read()
    span_generator = WhitespaceTokenizer().span_tokenize(text)
    spans = [span for span in span_generator]
    tokenized_text = WhitespaceTokenizer().tokenize(text)
    return text, tokenized_text, spans

#def getSubspan(tok)
#    
