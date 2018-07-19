import string
from Chrono import chronoEntities as chrono
from Chrono import BuildEntities as be

## Takes in a TimePhraseEntity and identifies if it should be annotated as a After entity
# @author Amy Olex
# @param s The TimePhraseEntity to parse
# @param chrono_id The current chrono_id to increment as new chronoEntities are added to list.
# @param chrono_list The list of Chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.

def buildBeforeAfter(s, chrono_id, chrono_list):
    boo, val, startSpan, endSpan = hasBeforeAfter(s)

    ## find the word "after" or "later" as a single token
    if boo:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan - startSpan)

        if val == "After":
            chrono_after_entity = chrono.ChronoAfterOperator(entityID=str(chrono_id) + "entity",
                                                             start_span=abs_StartSpan, end_span=abs_EndSpan,
                                                             interval_type="Link")
            chrono_id = chrono_id + 1
            chrono_list.append(chrono_after_entity)


        elif val == "Before":
            chrono_before_entity = chrono.ChronoBeforeOperator(entityID=str(chrono_id) + "entity",
                                                               start_span=abs_StartSpan, end_span=abs_EndSpan,
                                                               interval_type="Link")
            chrono_id = chrono_id + 1
            chrono_list.append(chrono_before_entity)

    return chrono_list, chrono_id


####
# END_MODULE
####

## Takes in a single text string and identifies if it has any Before or After phrases
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasBeforeAfter(tpentity):
    # convert to all lower
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text_lower.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    # convert to list
    text_list = text_norm.split(" ")

    # define my day lists
    b_words = ["before", "ago", "pre", "previously", "earlier", "until"]
    a_words = ["after", "later"]
    ba_words = b_words + a_words

    # figure out if any of the tokens in the text_list are also in the modifiers list
    intersect = list(set(text_list) & set(ba_words))

    # only proceed if the intersect list has a length of 1 or more.
    # I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1:
        # test if the intersect list contains which days.
        if len(list(set(intersect) & set(b_words))) == 1:
            start_idx, end_idx = be.getSpan(text_lower, list(set(intersect) & set(b_words))[0])
            return True, "Before", start_idx, end_idx

        if len(list(set(intersect) & set(a_words))) == 1:
            start_idx, end_idx = be.getSpan(text_lower, list(set(intersect) & set(a_words))[0])
            return True, "After", start_idx, end_idx

        else:
            return False, None, None, None
    else:
        return False, None, None, None

####
# END_MODULE
####