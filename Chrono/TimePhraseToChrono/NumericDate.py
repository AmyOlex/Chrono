from Chrono import chronoEntities as chrono
from Chrono import utils
import re
import calendar


## Takes in a TimePhraseEntity and identifies if it is a numeric date format
# @author Amy Olex
# @param s The TimePhraseEntity to parse
# @param chrono_id The current chrono_id to increment as new chronoEntities are added to list.
# @param chrono_list The list of Chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
# The flags are in the order: [loneDigitYear, month, day, hour, minute, second]
# chrono_time_flags = {"loneDigitYear"=False, "month"=False, "day"=False, "hour"=False, "minute"=False, "second"=False}
def buildNumericDate(s, chrono_id, chrono_list, flags):
    # convert to all lower
    text_lower = s.getText().lower()
    # remove all punctuation
    # text_norm = text_lower.translate(str.maketrans("", "", string.punctuation))
    # print("After:" + text_norm)
    # convert to list
    text_norm = text_lower.strip(".,")
    text_list = text_norm.split(" ")

    for text in text_list:
        ## See if there is a 4 digit number and assume it is a year if between 1500 and 2050
        ## Note that 24hour times in this range will be interpreted as years.  However, if a timezone like 1800EDT is attached it will not be parsed here.
        if len(text) == 4:

            num = utils.getNumberFromText(text)
            if num is not None:
                if (num >= 1500) and (num <= 2050) and not flags["fourdigityear"] and not flags["loneDigitYear"]:
                    flags["loneDigitYear"] = True
                    # print("Found Lone Digit Year")
                    ## build year
                    ref_StartSpan, ref_EndSpan = s.getSpan()
                    start_idx, end_idx = re.search(text, s.getText()).span(0)

                    chrono_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity",
                                                                 start_span=ref_StartSpan + start_idx,
                                                                 end_span=ref_StartSpan + end_idx, value=num)
                    chrono_id = chrono_id + 1
                    chrono_list.append(chrono_year_entity)

        ## parse out the condesnsed date format like 19980303 or 03031998.
        elif len(text) == 8 and utils.getNumberFromText(text) is not None:
            # Identify format yyyymmdd
            y = utils.getNumberFromText(text[0:4])
            m = utils.getNumberFromText(text[4:6])
            d = utils.getNumberFromText(text[6:8])
            if y is not None:
                if (y >= 1500) and (y <= 2050) and (m <= 12) and (d <= 31):
                    ref_StartSpan, ref_EndSpan = s.getSpan()
                    # add year

                    chrono_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity",
                                                                 start_span=ref_StartSpan, end_span=ref_StartSpan + 4,
                                                                 value=y)
                    chrono_id = chrono_id + 1
                    # add month
                    chrono_month_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity",
                                                                         start_span=ref_StartSpan + 4,
                                                                         end_span=ref_StartSpan + 6,
                                                                         month_type=calendar.month_name[m])
                    chrono_id = chrono_id + 1
                    chrono_year_entity.set_sub_interval(chrono_month_entity.get_id())
                    # add day
                    chrono_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity",
                                                                      start_span=ref_StartSpan + 6,
                                                                      end_span=ref_StartSpan + 8, value=d)
                    chrono_id = chrono_id + 1
                    chrono_month_entity.set_sub_interval(chrono_day_entity.get_id())

                    chrono_list.append(chrono_year_entity)
                    chrono_list.append(chrono_month_entity)
                    chrono_list.append(chrono_day_entity)
                else:
                    # test for mmddyyyy
                    y2 = utils.getNumberFromText(text[4:8])
                    m2 = utils.getNumberFromText(text[0:2])
                    d2 = utils.getNumberFromText(text[2:4])
                    if y2 is not None:
                        if (y2 >= 1500) and (y2 <= 2050) and (m2 <= 12) and (d2 <= 31):
                            ref_StartSpan, ref_EndSpan = s.getSpan()
                            # add year

                            chrono_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity",
                                                                         start_span=ref_StartSpan + 4,
                                                                         end_span=ref_StartSpan + 8, value=y)
                            chrono_id = chrono_id + 1
                            # add month
                            chrono_month_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity",
                                                                                 start_span=ref_StartSpan,
                                                                                 end_span=ref_StartSpan + 2,
                                                                                 month_type=calendar.month_name[m2])
                            chrono_id = chrono_id + 1
                            chrono_year_entity.set_sub_interval(chrono_month_entity.get_id())
                            # add day
                            chrono_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity",
                                                                              start_span=ref_StartSpan + 2,
                                                                              end_span=ref_StartSpan + 4, value=d)
                            chrono_id = chrono_id + 1
                            chrono_month_entity.set_sub_interval(chrono_day_entity.get_id())

                            chrono_list.append(chrono_year_entity)
                            chrono_list.append(chrono_month_entity)
                            chrono_list.append(chrono_day_entity)

        ## parse out the condesnsed date format like 030399 or 990303.
        ## Note that dates such as 12-01-2006 (120106 vs 061201) and similar are not distinguishable.
        elif len(text) == 6 and utils.getNumberFromText(text) is not None:
            # Identify format mmddyy

            y = utils.getNumberFromText(text[4:6])
            m = utils.getNumberFromText(text[0:2])
            d = utils.getNumberFromText(text[2:4])
            if y is not None and m is not None and d is not None:
                if (m <= 12) and (d <= 31):
                    ref_StartSpan, ref_EndSpan = s.getSpan()
                    # add year
                    chrono_year_entity = chrono.ChronoTwoDigitYearOperator(entityID=str(chrono_id) + "entity",
                                                                           start_span=ref_StartSpan + 4,
                                                                           end_span=ref_StartSpan + 6, value=y)
                    chrono_id = chrono_id + 1
                    # add month
                    chrono_month_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity",
                                                                         start_span=ref_StartSpan,
                                                                         end_span=ref_StartSpan + 2,
                                                                         month_type=calendar.month_name[m])
                    chrono_id = chrono_id + 1
                    chrono_year_entity.set_sub_interval(chrono_month_entity.get_id())
                    # add day
                    chrono_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity",
                                                                      start_span=ref_StartSpan + 2,
                                                                      end_span=ref_StartSpan + 4, value=d)
                    chrono_id = chrono_id + 1
                    chrono_month_entity.set_sub_interval(chrono_day_entity.get_id())

                    chrono_list.append(chrono_year_entity)
                    chrono_list.append(chrono_month_entity)
                    chrono_list.append(chrono_day_entity)
                else:
                    # test for yymmdd
                    y2 = utils.getNumberFromText(text[0:2])
                    m2 = utils.getNumberFromText(text[2:4])
                    d2 = utils.getNumberFromText(text[4:6])
                    if y2 is not None:
                        if (m2 <= 12) and (d2 <= 31):
                            ref_StartSpan, ref_EndSpan = s.getSpan()
                            # add year
                            chrono_year_entity = chrono.ChronoTwoDigitYearOperator(entityID=str(chrono_id) + "entity",
                                                                                   start_span=ref_StartSpan,
                                                                                   end_span=ref_StartSpan + 2, value=y2)
                            chrono_id = chrono_id + 1
                            # add month
                            chrono_month_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity",
                                                                                 start_span=ref_StartSpan + 2,
                                                                                 end_span=ref_StartSpan + 4,
                                                                                 month_type=calendar.month_name[m2])
                            chrono_id = chrono_id + 1
                            chrono_year_entity.set_sub_interval(chrono_month_entity.get_id())
                            # add day
                            chrono_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity",
                                                                              start_span=ref_StartSpan + 4,
                                                                              end_span=ref_StartSpan + 6, value=d2)
                            chrono_id = chrono_id + 1
                            chrono_month_entity.set_sub_interval(chrono_day_entity.get_id())

                            chrono_list.append(chrono_year_entity)
                            chrono_list.append(chrono_month_entity)
                            chrono_list.append(chrono_day_entity)

    return chrono_list, chrono_id, flags

####
# END_MODULE
####