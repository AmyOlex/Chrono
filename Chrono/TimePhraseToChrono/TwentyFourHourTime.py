import re

from Chrono import chronoEntities as chrono, utils
from Chrono.utils import calculateSpan


## Parses a TimePhrase entity's text field to determine if it contains a 24-hour time expression, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def build24HourTime(s, chrono_id, chrono_list, flags):

    boo, val, idxstart, idxend = has24HourTime(s, flags)
    ref_Sspan, ref_Espan = s.getSpan()
    if boo and not flags["loneDigitYear"]:
        ## assume format of hhmm or hhmmzzz
        try:
            hour = int(val[0:2])
            minute = int(val[2:4])
        except ValueError:
            # print("Skipping, not a 24hour time")
            return chrono_list, chrono_id, flags
            # hour = w2n.number_formation(val[0:2])
            # minute = w2n.word_to_num(val[2:4])
        #     print("TIME ZONE: {}".format(val))
        #     tz = hasTimeZone(s)
        #     my_tz_entity = chrono.ChronoTimeZoneEntity(str(chrono_id) + "entity", start_span=tz.span(0)[0] + ref_Sspan,
        #                                                end_span=tz.span(0)[1] + ref_Sspan)
        #     chrono_list.append(my_tz_entity)
        #     chrono_id = chrono_id + 1
        #     return chrono_list, chrono_id
        # #search for time zone
        # ## Identify if a time zone string exists
        # tz = hasTimeZone(s)
        # if tz is not None:
        #     my_tz_entity = chrono.ChronoTimeZoneEntity(str(chrono_id) + "entity", start_span =tz.span(0)[0] + ref_Sspan, end_span=tz.span(0)[1] + ref_Sspan)
        #     chrono_list.append(my_tz_entity)
        #     chrono_id = chrono_id + 1
        # else:
        #     my_tz_entity = None

        ## build minute entity
        min_entity = chrono.ChronoMinuteOfHourEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan + idxstart + 2, end_span=ref_Sspan + idxstart + 4, value=minute)
        # print("24Minute Value Added: " + str(min_entity.get_value()))
        chrono_list.append(min_entity)
        chrono_id = chrono_id + 1

        # if my_tz_entity is not None:
        #     hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan + idxstart, end_span=ref_Sspan + idxstart + 2, value=hour, time_zone=my_tz_entity.get_id())
        # else:
        hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity", start_span=ref_Sspan + idxstart, end_span=ref_Sspan + idxstart + 2, value=hour)
        # print("24Hour Value Added: " + str(hour_entity.get_value()))
        hour_entity.set_sub_interval(min_entity.get_id())
        chrono_list.append(hour_entity)
        chrono_id = chrono_id + 1


    return chrono_list, chrono_id, flags


## Takes in a single text string and identifies if it has any 4 digit 24-hour time phrases
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
# Note: This need to be called after it has checked for years
def has24HourTime(tpentity, flags):
    # text_lower = tpentity.getText().lower()
    # remove all punctuation
    # text_norm = text_lower.translate(str.maketrans("", "", ","))
    # convert to list
    stext = tpentity.getText()
    text_list = stext.split(" ")

    if not flags["loneDigitYear"]:
        # loop through list looking for expression
        for text in text_list:
            tz_format = re.search(
                '\d{0,4}(AST|EST|EDT|CST|CDT|MST|MDT|PST|PDT|AKST|HST|HAST|HADT|SST|SDT|GMT|CHST|UTC)', text)
            if len(text) == 4:
                num = utils.getNumberFromText(text)
                if num is not None:
                    hour = utils.getNumberFromText(text[:2])
                    minute = utils.getNumberFromText(text[2:])
                    if (hour is not None) and (minute is not None):
                        if (minute > 60) or (hour > 24):
                            return False, None, None, None
                        else:
                            start_idx, end_idx = calculateSpan(stext, text)
                            return True, text, start_idx, end_idx
            elif tz_format is not None:
                time = tz_format[0]
                # print("THIS TIME: {}".format(time))
                hour = utils.getNumberFromText(time[0:2])
                minute = utils.getNumberFromText(time[2:4])
                # if (minute > 60) or (hour > 24):
                #     return False, None, None, None
                # else:
                start_idx, end_idx = calculateSpan(stext, time)
                return True, time, start_idx, end_idx

        return False, None, None, None  # if no 4 digit year expressions were found return false
    else:
        return False, None, None, None  # if loneDigitYearFlag has already been set