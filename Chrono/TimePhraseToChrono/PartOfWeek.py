import string
from Chrono import chronoEntities as chrono
from Chrono.utils import calculateSpan


## Parses a TimePhrase entity's text field to determine if it contains a part of the week expression, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildPartOfWeek(s, chrono_id, chrono_list):

    boo, val, idxstart, idxend = hasPartOfWeek(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoPartOfWeekEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, part_of_week_type=val)
        chrono_list.append(my_entity)
        chrono_id = chrono_id + 1
        #check here to see if it has a modifier

    return chrono_list, chrono_id

## Takes in a TimePhrase entity and identifies if it has any part of week terms, like "weekend"
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
#############ISSUE: I've coded this to return the sub-span of the "value".  For example, the span returned for "overnight" is just for the "night" portion.  This seems to be how the gold standard xml does it, which I think is silly, but that is what it does.
def hasPartOfWeek(tpentity):
    # convert to all lower
    # text_lower = tpentity.getText().lower()
    text = tpentity.getText()
    # remove all punctuation
    text_norm = text.translate(str.maketrans("", "", string.punctuation))
    # convert to list
    text_list = text_norm.split(" ")

    # define my period lists
    partofday = ["weekend", "weekends"]

    # figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(partofday))

    # only proceed if the intersect list has a length of 1 or more.
    # For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1:

        term = intersect[0]
        start_idx, end_idx = calculateSpan(text_norm, term)
        if term == "weekend" or term == "weekends":
            return True, "Weekend", start_idx, end_idx
        else:
            return False, None, None, None
    else:
        return False, None, None, None