import string
import re
from Chrono import chronoEntities as chrono


## Takes in a TimePhraseEntity and identifies if it should be annotated as a This entity
# @author Amy Olex
# @param s The TimePhraseEntity to parse
# @param chrono_id The current chrono_id to increment as new chronoEntities are added to list.
# @param chrono_list The list of Chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.

def buildThis(s, chrono_id, chrono_list):
    # convert to lowercase
    text = s.getText().lower()
    # remove all punctuation
    text_norm = text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation))).strip()
    # convert to list
    text_list = text_norm.split(" ")

    ## find the word "now" as a single token
    for tok in text_list:
        if tok == "now":
            ## get start end coordinates in original temporal phrase
            start_idx, end_idx = re.search("now", text).span(0)
            ref_startSpan, ref_endSpan = s.getSpan()

            ## create a This entity
            chrono_this_entity = chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity",
                                                           start_span=ref_startSpan + start_idx,
                                                           end_span=ref_startSpan + end_idx)
            chrono_id = chrono_id + 1
            chrono_list.append(chrono_this_entity)

        elif tok == "today" or tok == "todays":
            start_idx, end_idx = re.search("today", text).span(0)
            ref_startSpan, ref_endSpan = s.getSpan()

            ## create a This entity
            chrono_this_entity = chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity",
                                                           start_span=ref_startSpan + start_idx,
                                                           end_span=ref_startSpan + end_idx)
            chrono_id = chrono_id + 1

            chrono_interval_entity = chrono.ChronoCalendarIntervalEntity(entityID=str(chrono_id) + "entity",
                                                                         start_span=ref_startSpan + start_idx,
                                                                         end_span=ref_startSpan + end_idx,
                                                                         calendar_type="Day", number=None)
            chrono_id = chrono_id + 1

            chrono_this_entity.set_repeating_interval(chrono_interval_entity.get_id())

            chrono_list.append(chrono_this_entity)
            chrono_list.append(chrono_interval_entity)

        ## Note, may need to look for phrases like "current week" at some point.
        elif tok == "current":
            ## get start end coordinates in original temporal phrase
            start_idx, end_idx = re.search("current", text).span(0)
            ref_startSpan, ref_endSpan = s.getSpan()

            ## create a This entity
            chrono_this_entity = chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity",
                                                           start_span=ref_startSpan + start_idx,
                                                           end_span=ref_startSpan + end_idx)
            chrono_id = chrono_id + 1
            chrono_list.append(chrono_this_entity)

    return chrono_list, chrono_id

####
# END_MODULE
####
