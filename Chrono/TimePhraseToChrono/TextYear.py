import re
import string
from nltk import WhitespaceTokenizer
from Chrono import chronoEntities as chrono, utils


def buildTextYear(s, chrono_id, chrono_list):

    boo, val, idxstart, idxend = hasTextYear(s)

    if boo:
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=val)
        chrono_id = chrono_id + 1
        chrono_list.append(my_year_entity)

    return chrono_list, chrono_id


## Parses a TimePhraseEntity's text field to determine if it contains a month of the year, written out in text form, followed by a day, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhraseEntity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
def hasTextYear(tpentity):
    #remove ending punctuation
    text1 = tpentity.getText().strip(",.")
    #replace all other punctuation and replace with spaces
    text = text1.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    #make sure it is all letters
    m = re.search('[a-z,A-Z,-,\s]*', text)
    if m.group(0) is not '':
        ##split on spaces
        tokenized_text = WhitespaceTokenizer().tokenize(text)
        for t in tokenized_text:
            if utils.getNumberFromText(t) is None:
                return False, None, None, None
        val = utils.getNumberFromText(text)

        if val is not None:
            if val >= 1500 and val <= 2050:
                r = re.search(text1, tpentity.getText())
                start, end = r.span(0)
                return True, val, start, end
            else:
                return False, None, None, None
        else:
            return False, None, None, None
    return False, None, None, None