import Chrono.utils
from Chrono import chronoEntities as chrono
from Chrono import utils
from Chrono import BuildEntities as be
import re

## Takes in list of TimePhrase output and converts to chronoEntity
# @author Nicholas Morton
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildDayOfMonth(s, chrono_id, chrono_list, flags):
    b, text, startSpan, endSpan = hasDayOfMonth(s)
    if b and not flags["day"]:
        flags["day"] = True
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan - startSpan)
        if (int(text) <= 31):
            chrono_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan,
                                                          end_span=abs_EndSpan, value=int(text))
            chrono_list.append(chrono_entity)
            chrono_id = chrono_id + 1

    return chrono_list, chrono_id, flags


####
# END_MODULE
####

## Takes in a single text string and identifies if it has a day of the month in numeric format
# @author Nicholas Morton and Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasDayOfMonth(tpentity):
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text_lower.translate(str.maketrans(",", " "))
    # convert to list
    text_list = text_norm.split(" ")

    if len(text_list) > 0:
        # loop through list looking for expression
        for text in text_list:
            # get start coordinate of this token in the full string so we can calculate the position of the temporal matches.
            text_start, text_end = Chrono.utils.calculateSpan(text_norm, text)

            # define regular expression to find a 2-digit month
            twodigitstart = re.search('([0-9]{1,2})[-/:]([0-9]{1,2}|[A-Za-z]{3,4})[-/:]([0-9]{2})', text)
            fourdigitstart = re.search('([0-9]{4})[-/:]([0-9]{1,2}|[A-Za-z]{3,4})[-/:]([0-9]{2})', text)

            if (fourdigitstart):
                # If start with 4 digits then assum the format yyyy/mm/dd
                start_idx, end_idx = Chrono.utils.calculateSpan(text, fourdigitstart[3])
                return True, fourdigitstart[3], text_start + start_idx, text_start + end_idx
            elif (twodigitstart):
                # If only starts with 2 digits assume the format mm/dd/yy or mm/dd/yyyy
                # Note for dates like 12/03/2012, the text 12/11/03 and 11/03/12 can't be disambiguated, so will return 12 as the month for the first and 11 as the month for the second.
                # check to see if the middle is text, if yes then treat the first 2 digits as a day
                if re.search('[A-Za-z]{3,4}', twodigitstart[2]) and utils.getMonthNumber(twodigitstart[2]) <= 12:
                    # if the second entity is all characters and is a valid text month get the first number as the day
                    if int(twodigitstart[1]) <= 31:
                        start_idx, end_idx = Chrono.utils.calculateSpan(text, twodigitstart[1])
                        return True, twodigitstart[1], text_start + start_idx, text_start + end_idx
                    else:
                        return False, None, None, None

                # check to see if the first two digits are less than or equal to 12.  If greater then we have the format yy/mm/dd
                elif int(twodigitstart[1]) <= 12:
                    # print("found 2digit start mm-dd-yy: " + str(twodigitstart.span(2)[0]+text_start) + " : " + str(twodigitstart.group(2)))
                    # assume mm/dd/yy
                    start_idx, end_idx = Chrono.utils.calculateSpan(text, twodigitstart[2])
                    return True, twodigitstart[2], text_start + start_idx, text_start + end_idx
                elif int(twodigitstart[1]) > 12:
                    # assume yy/mm/dd
                    start_idx, end_idx = Chrono.utils.calculateSpan(text, twodigitstart[3])
                    return True, twodigitstart[3], text_start + start_idx, text_start + end_idx
                else:
                    return False, None, None, None

        return False, None, None, None  # if no 2 digit month expressions were found return false
    else:

        return False, None, None, None  # if the text_list does not have any entries, return false

        return False, None, None, None  # if the text_list does not have any entries, return false

####
# END_MODULE
####
