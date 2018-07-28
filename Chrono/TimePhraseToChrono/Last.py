import string
import re
from Chrono import chronoEntities as chrono
from config import DICTIONARY


def buildLast(s, chrono_id, chrono_list):
    boo, val, startSpan, endSpan = hasLast(s)

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

## Takes in a single TimePhrase entity and determines if it has an explicit Last entity specified in the text.
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs the regex object or None
def hasLast(tpentity):
    text = tpentity.getText()
    text_norm = text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    last_words = '|'.join(DICTIONARY["Last"])
    lst = re.search('('+last_words+')', text_norm)

    if lst is not None:
        return True, lst.group(1), lst.start(1), lst.end(1)

    return False, None, None, None

####
#END_MODULE
####
