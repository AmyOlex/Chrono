import re
import string

from Chrono import chronoEntities as chrono, utils
from Chrono.TimePhraseToChrono.Modifier import hasModifier
from Chrono.utils import calculateSpan


## Parses a TimePhrase entity's text field to determine if it contains a season of the year written out in text form, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhrase entity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def buildSeasonOfYear(s, chrono_id, chrono_list, ref_list):

    boo, val, idxstart, idxend = hasSeasonOfYear(s, ref_list)
    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_entity = chrono.ChronoSeasonOfYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, season_type=val)
        chrono_id = chrono_id + 1

        #check here to see if it has a modifier
        hasMod, mod_type, mod_start, mod_end = hasModifier(s)
        if(hasMod):
            if mod_type == "This":
                chrono_list.append(chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1

            if mod_type == "Next":
                chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1

            if mod_type == "Last":
                chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
                chrono_id = chrono_id + 1
            #else:
            #    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
            #    chrono_id = chrono_id + 1

       # else:
    #        chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, repeating_interval=my_entity.get_id()))
     #       chrono_id = chrono_id+1

        #check to see if it has a number associated with it.  We assume the number comes before the interval string
        if idxstart > 0:
            substr = s.getText()[0:idxstart]
            m = re.search('([0-9]{1,2})', substr)
            if m is not None :
                num_val = m.group(0)
                abs_Sspan = ref_Sspan + m.span(0)[0]
                abs_Espan = ref_Sspan + m.span(0)[1]

                my_number_entity = chrono.ChronoNumber(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num_val)
                chrono_id = chrono_id + 1

                #add the number entity to the list
                chrono_list.append(my_number_entity)
                my_entity.set_number(my_number_entity.get_id())
                #else search for a text number
            else:
                texNumVal = utils.getNumberFromText(substr)
                if texNumVal is not None:
                    #create the number entity
                    my_number_entity = chrono.ChronoNumber(entityID=str(chrono_id) + "entity", start_span=ref_Sspan, end_span=ref_Sspan + (idxstart - 1), value=texNumVal)
                    chrono_id = chrono_id + 1
                    #append to list
                    chrono_list.append(my_number_entity)
                    #link to interval entity
                    my_entity.set_number(my_number_entity.get_id())

        chrono_list.append(my_entity)

    return chrono_list, chrono_id


## Takes in a TimePhrase entity and identifies if it has any season terms, like "summer" or "fall"
# @author Amy Olex
# @param tpentity The TimePhrase entity object being parsed
# @return Outputs 4 values: Boolean Flag, Value text, start index, end index
def hasSeasonOfYear(tpentity, ref_list):
    refStart_span, refEnd_span = tpentity.getSpan()

    # convert to all lower
    # text_lower = tpentity.getText().lower()
    text = tpentity.getText().lower()
    # remove all punctuation
    text_norm = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).strip()

    # convert to list
    text_list = text_norm.split(" ")

    # define my period lists
    seasonofyear = ["summer", "winter", "fall", "spring", "summers", "falls", "winters", "springs"]

    # figure out if any of the tokens in the text_list are also in the ampm list
    intersect = list(set(text_list) & set(seasonofyear))

    # only proceed if the intersect list has a length of 1 or more.
    # For this method I'm assuming it will only be a length of 1, if it is not then we don't know what to do with it.
    if len(intersect) == 1:

        term = intersect[0]
        start_idx, end_idx = calculateSpan(text_norm, term)
        if term == "summer" or term == "summers":
            start_idx, end_idx = calculateSpan(text_norm, "summer")
            absStart = refStart_span + start_idx
            absEnd = refStart_span + end_idx
            postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

            if postag == "NN":
                return True, "Summer", start_idx, end_idx

        elif term == "winter" or term == "winters":
            start_idx, end_idx = calculateSpan(text_norm, "winter")
            absStart = refStart_span + start_idx
            absEnd = refStart_span + end_idx
            postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

            if postag == "NN":
                return True, "Winter", start_idx, end_idx

        elif term == "fall" or term == "falls":
            start_idx, end_idx = calculateSpan(text_norm, "fall")
            absStart = refStart_span + start_idx
            absEnd = refStart_span + end_idx
            postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

            if postag == "NN":
                return True, "Fall", start_idx, end_idx

        elif term == "spring" or term == "springs":
            start_idx, end_idx = calculateSpan(text_norm, "spring")
            absStart = refStart_span + start_idx
            absEnd = refStart_span + end_idx
            postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

            if postag == "NN":
                return True, "Spring", start_idx, end_idx

        else:
            return False, None, None, None

    return False, None, None, None