import string
from Chrono import chronoEntities as chrono
from Chrono.utils import calculateSpan


## Parses a TimePhrase entity's text field to determine if it contains a modifier text expression, then builds the associated chronoentity list
# @author Luke Maffey
# @param s The TimePhrase entity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildModifierText(s, chrono_id, chrono_list):
    boo, val, idxstart, idxend = hasModifierText(s)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        if val is not None:
            if val in ("nearly", "almost", "<"):
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, modifier="Less-Than")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val in ("about", "approximately"):
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="Approx")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val == "late":
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="End")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val == "mid":
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="Mid")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val == "fiscal" or val == "fy":
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="Fiscal")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val == "over":
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="More-Than")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            elif val in ("early", "beginning"):
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="Start")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
            else:
                my_modifier_entity = chrono.ChronoModifier(str(chrono_id) + "entity",
                                                           start_span=abs_Sspan, end_span=abs_Espan, modifier="Approx")
                chrono_list.append(my_modifier_entity)
                chrono_id = chrono_id + 1
        else:
            my_modifier_entity = None

    return chrono_list, chrono_id


## Takes in a single text string and identifies if it has a modifier text
# @author Luke Maffey
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasModifierText(tpentity):

    text_lower = tpentity.getText().lower()
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans("", "", ","))
    #convert to list
    text_list = text_norm.split(" ")

    if len(text_list)>0:
        #loop through list looking for expression
        temp_text = ["nearly", "almost", "<", "late", "mid", "fiscal", "fy", "over", "early", "approximately", "beginning"]

        for t in text_list:
            answer = next((m for m in temp_text if m in t), None)
            if answer is not None:
                answer2 = next((m for m in temp_text if t in m), None)
                if answer2 is not None:
                    return True, t, calculateSpan(text_norm, t)[0], calculateSpan(text_norm, t)[1]
                else:
                    return False, None, None, None  # if no 2 digit hour expressions were found return false
            else:
                return False, None, None, None  # if no 2 digit day expressions were found return false
    else:

        return False, None, None, None  # if the text_list does not have any entries, return false


## Takes in a single text string and identifies if it has any modufying phrases
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasModifier(tpentity):
    # convert to all lower
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text_lower.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    # convert to list
    text_list = text_norm.split(" ")

    # define my day lists
    modifiers = ["this", "next", "last", "a", "each", "between", "from"]

    # figure out if any of the tokens in the text_list are also in the modifiers list
    intersect = list(set(text_list) & set(modifiers))

    # only proceed if the intersect list has a length of 1 or more.
    # I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1:
        # test if the intersect list contains which days.
        if intersect[0] == "this":
            start_idx = text_norm.index("this")
            end_idx = start_idx + len("this")
            return True, "This", start_idx, end_idx

        if intersect[0] == "next":
            start_idx = text_norm.index("next")
            end_idx = start_idx + len("next")
            return True, "Next", start_idx, end_idx

        if intersect[0] == "last":
            start_idx = text_norm.index("last")
            end_idx = start_idx + len("last")
            return True, "Last", start_idx, end_idx

        if intersect[0] == "a":
            start_idx = text_norm.index("a")
            end_idx = start_idx + len("a")
            return True, "Period", start_idx, end_idx

        if intersect[0] == "each":
            start_idx = text_norm.index("each")
            end_idx = start_idx + len("each")
            return True, "Period", start_idx, end_idx

        if intersect[0] == "between":
            start_idx = text_norm.index("between")
            end_idx = start_idx + len("between")
            return True, "Period", start_idx, end_idx

        if intersect[0] == "from":
            start_idx = text_norm.index("from")
            end_idx = start_idx + len("from")
            return True, "Period", start_idx, end_idx
        else:
            return False, None, None, None
    else:
        return False, None, None, None