import string

import Chrono.utils
from Chrono import utils
from Chrono import BuildEntities as tpc
from Chrono import chronoEntities as chrono

## Takes in a TimePhraseEntity and identifies if it has an NthFromStart entity
# @author Amy Olex
# @param s The TimePhraseEntity to parse
# @param chrono_id The current chrono_id to increment as new chronoEntities are added to list.
# @param chrono_list The list of Chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
### Note: Currently this only identified ordinals. the other oddities I don't completely understand yet are ignored.
def buildNthFromStart(s, chrono_id, chrono_list, ref_list):
    boo, val, startSpan, endSpan = hasNthFromStart(s, ref_list)

    if boo:
        ref_StartSpan, ref_EndSpan = s.getSpan()
        abs_StartSpan = ref_StartSpan + startSpan
        abs_EndSpan = abs_StartSpan + abs(endSpan - startSpan)

        chrono_nth_entity = chrono.ChronoNthOperator(entityID=str(chrono_id) + "entity", start_span=abs_StartSpan,
                                                     end_span=abs_EndSpan, value=val)
        chrono_id = chrono_id + 1
        chrono_list.append(chrono_nth_entity)

    return chrono_list, chrono_id


def hasNthFromStart(tpentity, ref_list):
    refStart_span, refEnd_span = tpentity.getSpan()

    # convert to all lower
    text = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    # convert to list
    text_list = text_norm.split(" ")

    ## if the term does not exist by itself it may be a substring. Go through each word in the TimePhrase string and see if a substring matches.
    for t in text_list:
        val = utils.isOrdinal(t)

        if val is not None:
            start_idx, end_idx = Chrono.utils.calculateSpan(text_norm, t)
            # now get the reference index of this token and see if there are any temporal tokens next to it.
            idx = utils.getRefIdx(ref_list, refStart_span + start_idx, refStart_span + end_idx)
            if ref_list[idx - 1].isTemporal() or ref_list[idx + 1].isTemporal():
                return True, val, start_idx, end_idx

    return False, None, None, None
####
# END_MODULE
####