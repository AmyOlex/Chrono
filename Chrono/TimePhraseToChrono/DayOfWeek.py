import Chrono.TimePhraseToChrono.Modifier
from Chrono import chronoEntities as chrono
import string
from Chrono import BuildEntities as be

## Parses a TimePhrase entity's text field to determine if it contains a day of the week written out in text form, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildDayOfWeek(s, chrono_id, chrono_list):
    boo, val, idxstart, idxend = hasDayOfWeek(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoDayOfWeekEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan,
                                                 end_span=abs_Espan, day_type=val)
        chrono_list.append(my_entity)
        chrono_id = chrono_id + 1
        # check here to see if it has a modifier
        hasMod, mod_type, mod_start, mod_end = Chrono.TimePhraseToChrono.Modifier.hasModifier(s)
        if (hasMod):
            if mod_type == "This":
                chrono_list.append(chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan,
                                                             end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1

            if mod_type == "Next":
                chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan,
                                                             end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1

            if mod_type == "Last":
                chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan,
                                                             end_span=abs_Espan, repeating_interval=my_entity.get_id(),
                                                             semantics="Interval-Included"))
                chrono_id = chrono_id + 1
            # else:
            #    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id(), semantics="Interval-Included"))
            #    chrono_id = chrono_id + 1

        # else:
        # TODO all last operators are getting added here except yesterday...
        #    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, semantics="Interval-Included", repeating_interval=my_entity.get_id()))
        #    chrono_id = chrono_id + 1

    return chrono_list, chrono_id


####
# END_MODULE
####

## Takes in a single text string and identifies if it is a day of week
# @author Amy Olex
# @param text The text to be parsed
# @return value The normalized string value for the day of week, or None if no Day of week found.
# @ISSUE If there are multiple days of week in the temporal phrase it only captures one of them.
def hasDayOfWeek(tpentity):
    # print("Before:" + text)
    # convert to all lower
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", string.punctuation))
    # print("After:" + text_norm)
    # convert to list
    text_list = text_norm.split(" ")

    # define my day lists
    M = ["monday", "mon", "m"]
    T = ["tuesday", "tue", "tues", "t"]
    W = ["wednesday", "wed", "w"]
    TR = ["thursday", "thur", "tr", "th"]
    F = ["friday", "fri", "f"]
    S = ["saturday", "sat", "s"]
    SU = ["sunday", "sun", "su"]
    days_of_week = M + T + W + TR + F + S + SU

    # figure out if any of the tokens in the text_list are also in the days of week list
    intersect = list(set(text_list) & set(days_of_week))

    # only proceed if the intersect list has a length of 1 or more.
    if len(intersect) >= 1:
        # test if the intersect list contains which days.
        if len(list(set(intersect) & set(M))) == 1:
            day_text = list(set(intersect) & set(M))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Monday", start_idx, end_idx

        if len(list(set(intersect) & set(T))) == 1:
            day_text = list(set(intersect) & set(T))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Tuesday", start_idx, end_idx

        if len(list(set(intersect) & set(W))) == 1:
            day_text = list(set(intersect) & set(W))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Wednesday", start_idx, end_idx

        if len(list(set(intersect) & set(TR))) == 1:
            day_text = list(set(intersect) & set(TR))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Thursday", start_idx, end_idx

        if len(list(set(intersect) & set(F))) == 1:
            day_text = list(set(intersect) & set(F))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Friday", start_idx, end_idx

        if len(list(set(intersect) & set(S))) == 1:
            day_text = list(set(intersect) & set(S))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Saturday", start_idx, end_idx

        if len(list(set(intersect) & set(SU))) == 1:
            day_text = list(set(intersect) & set(SU))[0]
            start_idx = text_norm.index(day_text)
            end_idx = start_idx + len(day_text)
            return True, "Sunday", start_idx, end_idx
        else:
            return False, None, None, None
    else:
        return False, None, None, None

####
# END_MODULE
####
