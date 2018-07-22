import string
import re
from Chrono import chronoEntities as chrono


def buildTimeZone(s, chrono_id, chrono_list):
    boo, val, startSpan, endSpan = hasTimeZone(s)

    if boo:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan - startSpan)

        chrono_tz_entity = chrono.ChronoTimeZoneEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan, end_span=abs_EndSpan)
        chrono_id = chrono_id + 1
        chrono_list.append(chrono_tz_entity)

    return chrono_list, chrono_id

####
#END_MODULE
####

## Takes in a single TimePhrase entity and determines if it has a time zone specified in the text.
# @author Amy Olex and Luke Maffey
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs the regex object or None
def hasTimeZone(tpentity):
    text = tpentity.getText()
    text_norm = text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    tz = re.search('(AST|EST|EDT|CST|CDT|MST|MDT|PST|PDT|HST|SST|SDT|GMT|UTC|BST|CET|IST|MSD|MSK|AKST|HAST|HADT|CHST|CEST|EEST)', text_norm)

    if tz is not None:
        return True, tz.group(1), tz.start(1), tz.end(1)
    '''    
        tz = re.search('\d{0,4}(AKST|HAST|HADT|CHST|CEST|EEST)', text_norm)
        if tz is None:
            return False, None, None, None
        elif len(tz.group()) == 4:
            return True, tz.group(), tz.start(), tz.end()
        elif len(tz.group()) == 6 or len(tz.group()) == 8:
            return True, tz.group()[-4:], tz.end()-4, tz.end()
        else:
            return False, None, None, None
    elif len(tz.group()) == 3:
        return True, tz.group(), tz.start(), tz.end()
    elif len(tz.group()) == 5 or len(tz.group()) == 7:
        return True, tz.group()[-3:], tz.end()-3, tz.end()
    '''
    return False, None, None, None

####
#END_MODULE
####