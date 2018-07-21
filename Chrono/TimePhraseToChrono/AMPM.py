import re

from Chrono import chronoEntities as chrono, utils
from Chrono.utils import calculateSpan


## Parses a TimePhrase entity's text field to determine if it contains a AM or PM time indication, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildAMPM(s, chrono_id, chrono_list, flags):
    am_flag = True
    ref_Sspan, ref_Espan = s.getSpan()
    ## Identify if a time zone string exists
    # tz = hasTimeZone(s)
    # if tz is not None:
    #     my_tz_entity = chrono.ChronoTimeZoneEntity(str(chrono_id) + "entity", start_span =tz.span(0)[0] + ref_Sspan, end_span=tz.span(0)[1] + ref_Sspan)
    #     chrono_list.append(my_tz_entity)
    #     chrono_id = chrono_id + 1
    # else:
    #     my_tz_entity = None

    boo, val, idxstart, idxend = hasAMPM(s)
    if boo:
        if val == "PM":
            am_flag = False

        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_AMPM_entity = chrono.ChronoAMPMOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, ampm_type=val)
        chrono_id = chrono_id + 1
        chrono_list.append(my_AMPM_entity)

        #check to see if it has a time associated with it.  We assume the time comes before the AMPM string
        #We could parse out the time from the TimePhrase normalized value.  The problem is getting the correct span.
        #idx_start is the first index of the ampm.  If there are any characters before it, it will be greater than 0.
        if idxstart > 0 and not flags['hour']:
            substr = s.getText()[0:idxstart]
            m = re.search('([0-9]{1,2})', substr)
            if m is not None :
                hour_val = m.group(0)
                abs_Sspan = ref_Sspan + m.span(0)[0]
                abs_Espan = ref_Sspan + m.span(0)[1]
                #print("Adding Hour in AMPM")
                my_hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=hour_val, ampm=my_AMPM_entity.get_id())
                chrono_id = chrono_id + 1
                chrono_list.append(my_hour_entity)

            #else search for a text number
            else:
                texNumVal = utils.getNumberFromText(substr)

                if texNumVal is not None:
                    #create the hour entity
                    if not flags['hour']:
                        my_hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan, end_span=ref_Sspan + (idxstart - 1), value=texNumVal, ampm=my_AMPM_entity.get_id())
                        chrono_id = chrono_id + 1
                        chrono_list.append(my_hour_entity)


    return chrono_list, chrono_id


## Takes in a single text string and identifies if it has any AM or PM phrases
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasAMPM(tpentity):
    # convert to all lower
    # text_lower = tpentity.getText().lower()
    text = tpentity.getText()
    # remove all punctuation
    text_norm = text.translate(str.maketrans("", "", ","))
    # convert to list
    text_list = text_norm.split(" ")

    if len(text_list) > 0:
        for text in text_list:
            if (re.search('AM|A\.M\.|am|a\.m\.', text)):
                match = re.search('AM|A\.M\.|am|a\.m\.', text).group(0)
                start_idx, end_idx = calculateSpan(text_norm, match)
                return True, "AM", start_idx, end_idx
            elif (re.search('PM|P\.M\.|pm|p\.m\.', text)):
                match = re.search('PM|P\.M\.|pm|p\.m\.', text).group(0)
                start_idx, end_idx = calculateSpan(text_norm, match)
                return True, "PM", start_idx, end_idx
    return False, None, None, None