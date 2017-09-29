## For trying out things
# Programmer Name: Amy Olex/Luke Maffey
# Date: 9/16/17
# Module Purpose: To test functions and modules written.


from task6 import utils
from task6 import referenceToken
import nltk
import os
import json
from sutime import SUTime
from nltk import word_tokenize
from nltk.corpus import stopwords

#file_path = "../../TrialData/TimeBank/wsj_0152/wsj_0152"
file_path = "SampleText.txt"
stopwords_path = "../task6/stopwords_long"
with open(stopwords_path) as raw:
    stopwords = raw.read().splitlines()

r, t, s = utils.getWhitespaceSpans(file_path)

words = word_tokenize(r)

#print("Raw text is:", r)
#print("Parsed Tokens are:", t)
#print("Parsed Spans are:", s)
filtered_words = []
for w in words :
    if w not in stopwords :
        filtered_words.append(w) 
# Just printing to make sure this works
#print("Filtered words: ", filtered_words)
print("Raw length: {}\nFiltered length: {}".format(len(words), len(filtered_words)))

## Converting to a reference Token list

su_words = ''

my_list = referenceToken.convertToRefTokens(t, span=s)
my_list[1].setTemporal(1)
print(str(len(my_list)))
for tok in my_list:
    if tok.getText() not in stopwords:
        su_words = su_words + tok.getText() + ' '
    
jar_files = '/home/luke/NLP/python-sutime/jars/'
sutime=SUTime(jars=jar_files, mark_time_ranges=True)
print(json.dumps(sutime.parse(su_words),sort_keys=True,indent=4))
