import Chrono.utils
from Chrono import chronoEntities as chrono
import re


## Takes in list of TimePhrase output and converts to chronoEntity
# @author Nicholas Morton
# @param s The TimePhrase entity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildHourOfDay(s, chrono_id, chrono_list, flags):
    b, text, startSpan, endSpan = hasHourOfDay(s)
    if b and not flags["hour"]:
        # print("Found Hour in buildChronoHour")
        flags["hour"] = True
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan - startSpan)
        chrono_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan,
                                                     end_span=abs_EndSpan, value=int(text))
        chrono_list.append(chrono_entity)
        chrono_id = chrono_id + 1

    return chrono_list, chrono_id, flags


####
# END_MODULE
####

## Takes in a single text string and identifies if it has a hour of a day
# @author Nicholas Morton and Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasHourOfDay(tpentity):
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    # convert to list
    text_list = text_norm.split(" ")

    if len(text_list) > 0:
        # loop through list looking for expression
        for text in text_list:
            # define regular expression to find a numeric hour

            if (re.search('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$', text)):  # checks for HH:MM:SS String
                match = re.search('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$', text).group(0)
                if len(match.split(":")) == 2 or len(match.split(":")) == 3:
                    start_idx, end_idx = Chrono.utils.calculateSpan(text_norm, re.compile(":").split(match)[0])
                    return True, re.compile(":").split(match)[0], start_idx, end_idx
                else:
                    return False, None, None, None  # if no 2 digit hour expressions were found return false

        return False, None, None, None  # if no 2 digit hour expressions were found return false
    else:

        return False, None, None, None  # if the text_list does not have any entries, return false

####
# END_MODULE
####
