import calendar
import re
import Chrono.utils
from Chrono import chronoEntities as chrono
from Chrono import utils
from Chrono.TimePhraseToChrono.DayOfMonth import hasDayOfMonth
from Chrono.TimePhraseToChrono.HourOfDay import hasHourOfDay
from Chrono.TimePhraseToChrono.MinuteOfHour import hasMinuteOfHour
from Chrono.TimePhraseToChrono.SecondOfMinute import hasSecondOfMinute

## Takes in list of TimePhrase output and converts to ChronoEntity
# @author Nicholas Morton and Amy Olex
# @param s The TimePhrase entity to parse 
# @param chrono_id The current chrono_id to increment as new chronoEntities are added to list.
# @param chrono_list The list of Chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
# The flags are in the order: [loneDigitYear, month, day, hour, minute, second]

def buildYear(s, chrono_id, chrono_list, flags):
    b, text, startSpan, endSpan, flags = hasYear(s, flags)
    if b:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = ref_StartSpan + endSpan
        chrono_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan,
                                                     end_span=abs_EndSpan, value=int(text))
        chrono_id = chrono_id + 1
        flags["fourdigityear"] = True

        # Check for Month in same element
        bMonth, textMonth, startSpanMonth, endSpanMonth = hasMonthOfYear(s)
        if bMonth and not flags["month"]:
            flags["month"] = True
            abs_StartSpanMonth = ref_StartSpan + startSpanMonth
            abs_EndSpanMonth = abs_StartSpanMonth + abs(endSpanMonth - startSpanMonth)
            m = utils.getMonthNumber(textMonth)

            if (m <= 12):
                chrono_month_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity",
                                                                     start_span=abs_StartSpanMonth,
                                                                     end_span=abs_EndSpanMonth,
                                                                     month_type=calendar.month_name[m])
                chrono_id = chrono_id + 1
                chrono_year_entity.set_sub_interval(chrono_month_entity.get_id())

            # Check for Day in same element
            bDay, textDay, startSpanDay, endSpanDay = hasDayOfMonth(s)
            if bDay and not flags["day"]:
                flags["day"] = True
                abs_StartSpanDay = ref_StartSpan + startSpanDay
                abs_EndSpanDay = abs_StartSpanDay + abs(endSpanDay - startSpanDay)
                if (int(textDay) <= 31):
                    chrono_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity",
                                                                      start_span=abs_StartSpanDay,
                                                                      end_span=abs_EndSpanDay, value=int(textDay))
                    chrono_id = chrono_id + 1
                    chrono_month_entity.set_sub_interval(chrono_day_entity.get_id())

                # Check for Hour in same element
                bHour, textHour, startSpanHour, endSpanHour = hasHourOfDay(s)
                if bHour and not flags["hour"]:
                    # print("Found Hour in Year")
                    flags["hour"] = True
                    ref_StartSpan, ref_EndSpan = s.getSpan()
                    abs_StartSpanHour = ref_StartSpan + startSpanHour
                    abs_EndSpanHour = abs_StartSpanHour + abs(endSpanHour - startSpanHour)
                    if (int(textHour) <= 24):
                        chrono_hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity",
                                                                          start_span=abs_StartSpanHour,
                                                                          end_span=abs_EndSpanHour, value=int(textHour))
                        chrono_id = chrono_id + 1
                        chrono_day_entity.set_sub_interval(chrono_hour_entity.get_id())

                    # Check for Minute in same element
                    bMinute, textMinute, startSpanMinute, endSpanMinute = hasMinuteOfHour(s)
                    if bMinute and not flags["minute"]:
                        flags["minute"] = True
                        ref_StartSpan, ref_EndSpan = s.getSpan()
                        abs_StartSpanMinute = ref_StartSpan + startSpanMinute
                        abs_EndSpanMinute = abs_StartSpanMinute + abs(endSpanMinute - startSpanMinute)
                        if (int(textMinute) <= 60):
                            chrono_minute_entity = chrono.ChronoMinuteOfHourEntity(entityID=str(chrono_id) + "entity",
                                                                                   start_span=abs_StartSpanMinute,
                                                                                   end_span=abs_EndSpanMinute,
                                                                                   value=int(textMinute))
                            chrono_id = chrono_id + 1
                            chrono_hour_entity.set_sub_interval(chrono_minute_entity.get_id())

                        # Check for Second in same element
                        bSecond, textSecond, startSpanSecond, endSpanSecond = hasSecondOfMinute(s)
                        if bSecond and not flags["second"]:
                            flags["second"] = True
                            ref_StartSpan, ref_EndSpan = s.getSpan()
                            abs_StartSpanSecond = ref_StartSpan + startSpanSecond
                            abs_EndSpanSecond = abs_StartSpanSecond + abs(endSpanSecond - startSpanSecond)
                            if (int(textSecond) <= 60):
                                chrono_second_entity = chrono.ChronoSecondOfMinuteEntity(
                                    entityID=str(chrono_id) + "entity", start_span=abs_StartSpanSecond,
                                    end_span=abs_EndSpanSecond, value=int(textSecond))
                                chrono_list.append(chrono_second_entity)
                                chrono_id = chrono_id + 1
                                chrono_minute_entity.set_sub_interval(chrono_second_entity.get_id())

                        chrono_list.append(chrono_minute_entity)

                    chrono_list.append(chrono_hour_entity)

                chrono_list.append(chrono_day_entity)

            chrono_list.append(chrono_month_entity)

        chrono_list.append(chrono_year_entity)

    return chrono_list, chrono_id, flags


####
# END_MODULE
####

## Takes in a single text string and identifies if it has any 4 digit year phrases
# @author Nicholas Morton and Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasYear(tpentity, flags):
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text_lower.translate(str.maketrans(",", ' ')).strip()
    # convert to list
    text_list = text_norm.split(" ")

    if len(text_list) > 0:
        # loop through list looking for expression
        for text in text_list:
            # get start coordinate of this token in the full string so we can calculate the position of the temporal matches.
            text_start, text_end = Chrono.utils.calculateSpan(text_norm, text)

            result = re.search('([0-9]{1,2})[-/:]([0-9]{1,2}|[A-Za-z]{3,4})[-/:]([0-9]{4})', text)

            # define regular expression to find a 4-digit year from the date format
            if result:
                result = result.group(0)
                split_result = re.split('[/:-]', result)

                if len(split_result) == 3:
                    start_idx, end_idx = Chrono.utils.calculateSpan(text, split_result[2])
                    return True, split_result[2], text_start + start_idx, text_start + end_idx, flags
                else:
                    return False, None, None, None, flags
            ## look for year at start of date
            ## added by Amy Olex
            elif len(text) > 7:
                result = re.search('([0-9]{4})[-/:]([0-9]{1,2}|[A-Za-z]{3,4})[-/:]([0-9]{1,2})', text)
                if result:
                    result = result.group(0)
                    split_result = re.split('[/:-]', result)
                    if len(split_result) == 3:
                        start_idx, end_idx = Chrono.utils.calculateSpan(result, split_result[0])
                        return True, split_result[0], text_start + start_idx, text_start + end_idx, flags
                    else:
                        return False, None, None, None, flags
            ## special case to look for c.yyyy
            elif len(text) == 6:
                result = re.search("c\.([0-9]{4})", text)
                if result:
                    rval = utils.getNumberFromText(result.group(1))
                    if rval:
                        if rval >= 1500 and rval <= 2050:
                            start_idx, end_idx = result.span(1)
                            return True, rval, start_idx, end_idx, flags

        return False, None, None, None, flags  # if no 4 digit year expressions were found return false

    else:
        return False, None, None, None, flags  # if the text_list does not have any entries, return false


####
# END_MODULE
####

## Takes in list of TimePhrase output and converts to ChronoEntity
# @author Nicholas Morton
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def build2DigitYear(s, chrono_id, chrono_list, flags):
    b, text, startSpan, endSpan = has2DigitYear(s)
    if b and not flags["fourdigityear"]:
        # In most cases this will be at the end of the Span
        ref_StartSpan, ref_EndSpan = s.tpc.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan - startSpan)
        chrono_2_digit_year_entity = chrono.ChronoTwoDigitYearOperator(entityID=str(chrono_id) + "entity",
                                                                       start_span=abs_StartSpan, end_span=abs_EndSpan,
                                                                       value=text)
        chrono_id = chrono_id + 1

        # Check for Month in same element
        bMonth, textMonth, startSpanMonth, endSpanMonth = hasMonthOfYear(s)
        if bMonth and not flags["month"]:
            flags["month"] = True
            abs_StartSpanMonth = ref_StartSpan + startSpanMonth
            abs_EndSpanMonth = abs_StartSpanMonth + abs(endSpanMonth - startSpanMonth)
            m = utils.getMonthNumber(textMonth)

            if (m <= 12):
                chrono_month_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity",
                                                                     start_span=abs_StartSpanMonth,
                                                                     end_span=abs_EndSpanMonth,
                                                                     month_type=calendar.month_name[m])
                chrono_id = chrono_id + 1
                chrono_2_digit_year_entity.set_sub_interval(chrono_month_entity.get_id())

            # Check for Day in same element
            bDay, textDay, startSpanDay, endSpanDay = hasDayOfMonth(s)
            if bDay and not flags["day"]:
                flags["day"] = True
                abs_StartSpanDay = ref_StartSpan + startSpanDay
                abs_EndSpanDay = abs_StartSpanDay + abs(endSpanDay - startSpanDay)
                if (int(textDay) <= 31):
                    chrono_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity",
                                                                      start_span=abs_StartSpanDay,
                                                                      end_span=abs_EndSpanDay, value=int(textDay))
                    chrono_id = chrono_id + 1
                    chrono_month_entity.set_sub_interval(chrono_day_entity.get_id())

                # Check for Hour in same element
                bHour, textHour, startSpanHour, endSpanHour = hasHourOfDay(s)
                if bHour and not flags["hour"]:
                    # print("Found Hour in 2-digit year")
                    flags["hour"] = True
                    ref_StartSpan, ref_EndSpan = s.tpc.getSpan()
                    abs_StartSpanHour = ref_StartSpan + startSpanHour
                    abs_EndSpanHour = abs_StartSpanHour + abs(endSpanHour - startSpanHour)
                    if (int(textHour) <= 24):
                        chrono_hour_entity = chrono.ChronoHourOfDayEntity(entityID=str(chrono_id) + "entity",
                                                                          start_span=abs_StartSpanHour,
                                                                          end_span=abs_EndSpanHour, value=int(textHour))
                        chrono_id = chrono_id + 1
                        chrono_day_entity.set_sub_interval(chrono_hour_entity.get_id())

                    # Check for Minute in same element
                    bMinute, textMinute, startSpanMinute, endSpanMinute = hasMinuteOfHour(s)
                    if bMinute and not flags["minute"]:
                        flags["minute"] = True
                        ref_StartSpan, ref_EndSpan = s.tpc.getSpan()
                        abs_StartSpanMinute = ref_StartSpan + startSpanMinute
                        abs_EndSpanMinute = abs_StartSpanMinute + abs(endSpanMinute - startSpanMinute)
                        if (int(textMinute) <= 60):
                            chrono_minute_entity = chrono.ChronoMinuteOfHourEntity(entityID=str(chrono_id) + "entity",
                                                                                   start_span=abs_StartSpanMinute,
                                                                                   end_span=abs_EndSpanMinute,
                                                                                   value=int(textMinute))
                            chrono_id = chrono_id + 1
                            chrono_hour_entity.set_sub_interval(chrono_minute_entity.get_id())

                        # Check for Second in same element
                        bSecond, textSecond, startSpanSecond, endSpanSecond = hasSecondOfMinute(s)
                        if bSecond and not flags["second"]:
                            flags["second"] = True
                            ref_StartSpan, ref_EndSpan = s.tpc.getSpan()
                            abs_StartSpanSecond = ref_StartSpan + startSpanSecond
                            abs_EndSpanSecond = abs_StartSpanSecond + abs(endSpanSecond - startSpanSecond)
                            if (int(textSecond) <= 60):
                                chrono_second_entity = chrono.ChronoSecondOfMinuteEntity(
                                    entityID=str(chrono_id) + "entity", start_span=abs_StartSpanSecond,
                                    end_span=abs_EndSpanSecond, value=int(textSecond))
                                chrono_list.append(chrono_second_entity)
                                chrono_id = chrono_id + 1
                                chrono_minute_entity.set_sub_interval(chrono_second_entity.get_id())

                        chrono_list.append(chrono_minute_entity)

                    chrono_list.append(chrono_hour_entity)

                chrono_list.append(chrono_day_entity)

            chrono_list.append(chrono_month_entity)

        chrono_list.append(chrono_2_digit_year_entity)

    return chrono_list, chrono_id, flags


####
# END_MODULE
####

## Takes in a single text string and identifies if it has any 2 digit year phrases
# @author Nicholas Morton
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def has2DigitYear(tpentity):
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

            # define regular expression to find a 2-digit year
            regex = re.search('([0-9]{1,2})[-/:]([0-9]{1,2}|[A-Za-z]{3,4})[-/:]([0-9]{2})', text)
            if regex and len(regex.group(0)) == 8:
                if len(regex.group(0).split("/")) == 3:
                    start_idx, end_idx = Chrono.utils.calculateSpan(text, re.compile("/").split(regex.group(0))[2])
                    return True, re.compile("/").split(regex.group(0))[2], text_start + start_idx, text_start + end_idx
                elif len(regex.group(0).split("-")) == 3:
                    start_idx, end_idx = Chrono.utils.calculateSpan(text, re.compile("-").split(regex.group(0))[2])
                    return True, re.compile("-").split(regex.group(0))[2], text_start + start_idx, text_start + end_idx
                else:
                    return False, None, None, None

        return False, None, None, None  # if no 2 digit year expressions were found return false
    else:

        return False, None, None, None  # if the text_list does not have any entries, return false


####
# END_MODULE
####

## Takes in list of TimePhrase output and converts to chronoEntity
# @author Nicholas Morton
# @param s The TimePhrase entity to parse 
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildMonthOfYear(s, chrono_id, chrono_list, flags):
    b, text, startSpan, endSpan = hasMonthOfYear(s)
    if b and not flags["month"]:
        flags["month"] = True
        ref_StartSpan, ref_EndSpan = s.tpc.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan - startSpan)
        if (int(text) <= 12):
            chrono_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan,
                                                           end_span=abs_EndSpan,
                                                           month_type=calendar.month_name[utils.getMonthNumber(text)])
            chrono_list.append(chrono_entity)
            chrono_id = chrono_id + 1

    return chrono_list, chrono_id, flags


####
# END_MODULE
####

## Takes in a single text string and identifies if it has a month of year
# @author Nicholas Morton and Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasMonthOfYear(tpentity):
    # text_lower = tpentity.getText().lower()
    thisText = tpentity.getText()
    # remove all punctuation
    text_norm = thisText.translate(str.maketrans(",", " "))
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
                start_idx, end_idx = Chrono.utils.calculateSpan(text, fourdigitstart[2])
                return True, fourdigitstart[2], text_start + start_idx, text_start + end_idx
            elif (twodigitstart):
                # If only starts with 2 digits assume the format mm/dd/yy or mm/dd/yyyy
                # Note for dates like 12/03/2012, the text 12/11/03 and 11/03/12 can't be disambiguated, so will return 12 as the month for the first and 11 as the month for the second.
                # check to see if the first two digits are less than or equal to 12.  If greater then we have the format yy/mm/dd
                if int(twodigitstart[1]) <= 12:
                    # assume mm/dd/yy
                    start_idx, end_idx = Chrono.utils.calculateSpan(text, twodigitstart[1])  # twodigitstart.span(1)  #
                    # print("found 2digit start mm-dd-yy: " + str(twodigitstart.span(1)[0]+text_start) + " : " + str(twodigitstart.group(1)))
                    ##### Trying to DEBUG string formats like AP-JN-08-16-90 ##########
                    return True, twodigitstart[1], text_start + start_idx, text_start + end_idx
                elif int(twodigitstart[1]) > 12:
                    # assume yy/mm/dd
                    start_idx, end_idx = Chrono.utils.calculateSpan(text, twodigitstart[
                        2])  # twodigitstart.span(2) #tpc.getSpan(text_norm,twodigitstart[2])
                    return True, twodigitstart[2], text_start + start_idx, text_start + end_idx
                else:
                    return False, None, None, None

        return False, None, None, None  # if no 2 digit month expressions were found return false
    else:

        return False, None, None, None  # if the text_list does not have any entries, return false

####
# END_MODULE
####
