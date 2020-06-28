import string
import re
from Chrono import chronoEntities as chrono
import inspect
import os

global dictpath
global FREQ
thisfilename = inspect.getframeinfo(inspect.currentframe()).filename
thispath = os.path.dirname(os.path.abspath(thisfilename))
dictpath = os.path.join(thispath,"../../dictionary")

FREQ = [line.rstrip() for line in open(os.path.join(dictpath,"Frequency.txt"), "r")]


def buildFrequency(s, chrono_id, chrono_list):
    boo, val, startSpan, endSpan = hasFrequency(s)

    if boo:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan - startSpan)

        chrono_last_entity = chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan, end_span=abs_EndSpan)
        
        chrono_id = chrono_id + 1
        chrono_list.append(chrono_last_entity)

    return chrono_list, chrono_id

####
#END_MODULE
####

## Takes in a single TimePhrase entity and determines if it has Frequency entity specified in the text.
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs the regex object or None
def hasFrequency(tpentity):
    text = tpentity.getText()
    #text_norm = text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    ## right now we are only looking at abbreviations for frequencies, so I will not transform the text or we will loose information.
    
    search_string = FREQ.join("|")
    print("FREQUENCY: " + search_string)
    lst = re.search('(last|previously|pre|later|earlier|early|previous|past|lately|final|latest|prior|recent|recently)', text_norm)

    if lst is not None:
        return True, lst.group(1), lst.start(1), lst.end(1)

    return False, None, None, None

####
#END_MODULE
####
