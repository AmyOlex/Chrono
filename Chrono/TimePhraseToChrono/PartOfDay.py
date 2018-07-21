import re
import string

from Chrono import chronoEntities as chrono
from Chrono.utils import calculateSpan


## Parses a TimePhrase entity's text field to determine if it contains a part of the day expression, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildPartOfDay(s, chrono_id, chrono_list):

    boo, val, idxstart, idxend = hasPartOfDay(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoPartOfDayEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, part_of_day_type=val)
        chrono_list.append(my_entity)
        chrono_id = chrono_id + 1
        #check here to see if it has a modifier

    return chrono_list, chrono_id


## Takes in a TimePhrase entity and identifies if it has any part of day terms, like "overnight" or "morning"
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
#############ISSUE: I've coded this to return the sub-span of the "value".  For example, the span returned for "overnight" is just for the "night" portion.  This seems to be how the gold standard xml does it, which I think is silly, but that is what it does.
def hasPartOfDay(tpentity):
    # convert to all lower
    text = tpentity.getText().lower()
    # text = tpentity.getText()
    # remove all punctuation
    text_norm = text.translate(str.maketrans("", "", string.punctuation))
    # convert to list
    text_list = text_norm.split(" ")

    # define my period lists
    partofday = ["morning", "evening", "afternoon", "night", "dawn", "dusk", "tonight", "overnight", "nights",
                 "mornings", "evening", "afternoons", "noon", "bedtime", "midnight", "eve"]

    # figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(partofday))

    # only proceed if the intersect list has a length of 1 or more.
    # For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1:

        term = intersect[0]
        start_idx, end_idx = calculateSpan(text_norm, term)
        if term == "morning" or term == "mornings":
            return True, "Morning", start_idx, end_idx
        if term == "dawn":
            return True, "Dawn", start_idx, end_idx
        elif term == "evening" or term == "dusk" or term == "evenings" or term == "eve":
            return True, "Evening", start_idx, end_idx
        elif term == "afternoon" or term == "afternoons":
            return True, "Afternoon", start_idx, end_idx
        elif term == "nights":
            return True, "Night", start_idx, end_idx
        elif term == "noon":
            return True, "Noon", start_idx, end_idx
        elif term == "bedtime":
            return True, "Unknown", start_idx, end_idx
        elif term == "midnight":
            return True, "Midnight", start_idx, end_idx
        elif term == "night" or term == "overnight" or term == "tonight":
            m = re.search("night", text_norm)
            sidx = m.span(0)[0]
            eidx = m.span(0)[1]
            return True, "Night", sidx, eidx
        else:
            return False, None, None, None
    else:
        return False, None, None, None