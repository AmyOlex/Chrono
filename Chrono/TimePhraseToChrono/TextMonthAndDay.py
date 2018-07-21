import datetime
import string

from nltk import WhitespaceTokenizer

from Chrono import chronoEntities as chrono, utils
from Chrono.TimePhraseToChrono.Modifier import hasModifier
from Chrono.utils import calculateSpan


## Parses a TimePhraseEntity's text field to determine if it contains a month of the year, written out in text form, followed by a day, then builds the associated chronoentity list
# @author Amy Olex
# @param s The TimePhraseEntity to parse
# @param chronoID The current chronoID to increment as new chronoentities are added to list.
# @param chronoList The list of chrono objects we currently have.  Will add to these.
# @return chronoList, chronoID Returns the expanded chronoList and the incremented chronoID.
# ISSUE: This method assumes the day appears after the month, but that may not always be the case as in "sixth of November"
# ISSUE: This method has much to be desired. It will not catch all formats, and will not be able to make the correct connections for sub-intervals.
#        It also will not be able to identify formats like "January 6, 1996" or "January third, nineteen ninety-six".
def buildTextMonthAndDay(s, chrono_id, chrono_list, flags, dct=None, ref_list=None):
    boo, val, idxstart, idxend = hasTextMonth(s, ref_list)
    if boo and not flags["month"]:
        flags["month"] = True
        ref_Sspan, ref_Espan = s.getSpan()
        abs_Sspan = ref_Sspan + idxstart
        abs_Espan = ref_Sspan + idxend
        my_month_entity = chrono.chronoMonthOfYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, month_type=val)
        chrono_id = chrono_id + 1

        ## assume all numbers 1-31 are days
        ## assume all numbers >1000 are years
        ## parse all text before month
            ## test to see if all text is a number or text year
            ## if no:
              ## remove all punctuation
              ## seperate by spaces
              ## parse each token, if find a number then assign to day or year as appropriate
            ## if yes:
              ## assign to day or year as appropriate

        ## parse all text after month
          ## test to see if all text is a number or text year
          ## if no:
            ## remove all punctuation
            ## seperate by spaces
            ## parse each token, if find a number then assign to day or year as appropriate
          ## if yes:
            ## assign to day or year as appropriate

        #idx_end is the last index of the month.  If there are any characters after it the length of the string will be greater than the endidx.
        if(idxend < len(s.getText())):
            substr = s.getText()[idxend:].strip(",.").strip()

            num = utils.getNumberFromText(substr)
            if num is not None:
                if num <= 31 and not flags["day"]:
                    flags["day"] = True
                    day_startidx, day_endidx = calculateSpan(s.getText(), str(num))#substr)
                    abs_Sspan = ref_Sspan + day_startidx
                    abs_Espan = ref_Sspan + day_endidx
                    my_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num)
                    chrono_list.append(my_day_entity)
                    chrono_id = chrono_id + 1

                    #now figure out if it is a NEXT or LAST
                    #create doctime
                    if False: #dct is not None:
                        mStart = my_month_entity.get_start_span()
                        mEnd = my_month_entity.get_end_span()
                        this_dct = datetime.datetime(int(dct.year),int(utils.getMonthNumber(my_month_entity.get_month_type())), int(my_day_entity.get_value()), 0, 0)
                        if this_dct > dct:
                            chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                            chrono_id = chrono_id + 1
                        elif this_dct < dct:
                            chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                            chrono_id = chrono_id + 1
                elif num >=1500 and num <=2050 and not flags["fourdigityear"] and not flags["loneDigitYear"]:
                    flags["fourdigityear"] = True
                    year_startidx, year_endidx = calculateSpan(s.getText(), substr)
                    abs_Sspan = ref_Sspan + year_startidx
                    abs_Espan = ref_Sspan + year_endidx

                    my_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num)
                    chrono_list.append(my_year_entity)
                    my_year_entity.set_sub_interval(my_month_entity.get_id())
                    chrono_id = chrono_id + 1
            else:
                ##parse and process each token
                ##replace punctuation
                substr = substr.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
                ##split on spaces
                tokenized_text = WhitespaceTokenizer().tokenize(substr)
                for i in range(0,len(tokenized_text)):
                    num = utils.getNumberFromText(tokenized_text[i])
                    if num is not None:
                        if num <= 31:
                            day_startidx, day_endidx = calculateSpan(s.getText(), tokenized_text[i])
                            abs_Sspan = ref_Sspan + day_startidx
                            abs_Espan = ref_Sspan + day_endidx
                            my_day_entity = chrono.ChronoDayOfMonthEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num)
                            chrono_list.append(my_day_entity)
                            chrono_id = chrono_id + 1

                            #now figure out if it is a NEXT or LAST
                            #create doctime
                            if False: #dct is not None:
                                mStart = my_month_entity.get_start_span()
                                mEnd = my_month_entity.get_end_span()
                                this_dct = datetime.datetime(int(dct.year),int(utils.getMonthNumber(my_month_entity.get_month_type())), int(my_day_entity.get_value()), 0, 0)
                                if this_dct > dct:
                                    chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                                    chrono_id = chrono_id + 1
                                elif this_dct < dct:
                                    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=mStart, end_span=mEnd, repeating_interval=my_month_entity.get_id()))
                                    chrono_id = chrono_id + 1
                        elif num >=1500 and num <=2050 and not flags["fourdigityear"] and not flags["loneDigitYear"]:
                            flags["fourdigityear"] = True
                            year_startidx, year_endidx = calculateSpan(s.getText(), tokenized_text[i])
                            abs_Sspan = ref_Sspan + year_startidx
                            abs_Espan = ref_Sspan + year_endidx

                            my_year_entity = chrono.ChronoYearEntity(entityID=str(chrono_id) + "entity", start_span=abs_Sspan, end_span=abs_Espan, value=num)
                            chrono_list.append(my_year_entity)
                            my_year_entity.set_sub_interval(my_month_entity.get_id())
                            chrono_id = chrono_id + 1

        ## if the start of the month is not 0 then we have leading text to parse
        if(idxstart > 0):
            #substr = s.getText()[:idxstart].strip(",.").strip()
            hasMod, mod_type, mod_start, mod_end = hasModifier(s)
            if(hasMod):
                if mod_type == "This":
                    chrono_list.append(chrono.ChronoThisOperator(entityID=str(chrono_id) + "entity", start_span=ref_Sspan+mod_start, end_span=ref_Sspan+mod_end, repeating_interval=my_month_entity.get_id()))
                    chrono_id = chrono_id + 1

                if mod_type == "Next":
                    chrono_list.append(chrono.ChronoNextOperator(entityID=str(chrono_id) + "entity", start_span=ref_Sspan+mod_start, end_span=ref_Sspan+mod_end, repeating_interval=my_month_entity.get_id()))
                    chrono_id = chrono_id + 1

                if mod_type == "Last":
                    # print("FOUND LAST")
                    chrono_list.append(chrono.ChronoLastOperator(entityID=str(chrono_id) + "entity", start_span=ref_Sspan+mod_start, end_span=ref_Sspan+mod_end, repeating_interval=my_month_entity.get_id(), semantics="Interval-Not-Included"))
                    chrono_id = chrono_id + 1

        chrono_list.append(my_month_entity)

    return chrono_list, chrono_id, flags


## Takes in a single text string and identifies if it is a month of the year
# @author Amy Olex
# @param tpentity The entity to parse
# @return value The normalized string value for the month of the year, or None if no month of year found.
# @ISSUE If there are multiple months of the year in the temporal phrase it only captures one of them.
def hasTextMonth(tpentity, ref_list):
    refStart_span, refEnd_span = tpentity.getSpan()

    # convert to all lower
    text_lower = tpentity.getText().lower()
    # remove all punctuation
    # text_norm = text_lower.translate(str.maketrans(",", ' ')).strip()
    text_norm = text_lower.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).strip()
    # convert to list
    text_list = text_norm.split(" ")

    # define my month lists
    full_month = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
                  "november", "december"]

    # run for full month
    t_flag = False
    for tok in text_list:
        answer = next((m for m in full_month if tok in m), None)
        if answer is not None and not t_flag:
            answer2 = next((m for m in full_month if m in tok), None)
            if answer2 is not None and not t_flag:
                t_flag = True
                # answer2 should contain the element that matches.  We need to find the span in the original phrase and return the correct value
                start_idx, end_idx = calculateSpan(text_lower, answer2)
                absStart = refStart_span + start_idx
                absEnd = refStart_span + end_idx
                postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

                if postag == "NNP":
                    if answer2 in ["january"]:
                        return True, "January", start_idx, end_idx
                    elif answer2 in ["february"]:
                        return True, "February", start_idx, end_idx
                    elif answer2 in ["march"]:
                        return True, "March", start_idx, end_idx
                    elif answer2 in ["april"]:
                        return True, "April", start_idx, end_idx
                    elif answer2 in ["may"]:
                        return True, "May", start_idx, end_idx
                    elif answer2 in ["june"]:
                        return True, "June", start_idx, end_idx
                    elif answer2 in ["july"]:
                        return True, "July", start_idx, end_idx
                    elif answer2 in ["august"]:
                        return True, "August", start_idx, end_idx
                    elif answer2 in ["september"]:
                        return True, "September", start_idx, end_idx
                    elif answer2 in ["october"]:
                        return True, "October", start_idx, end_idx
                    elif answer2 in ["november"]:
                        return True, "November", start_idx, end_idx
                    elif answer2 in ["december"]:
                        return True, "December", start_idx, end_idx

    # run for abbr month
    abbr_month = ["jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug.", "sept.", "sep.", "oct.", "nov.", "dec."]
    adj_punc = '!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~'
    text_norm2 = text_lower.translate(str.maketrans(adj_punc, ' ' * len(adj_punc))).strip()
    # convert to list
    text_list2 = text_norm2.split(" ")

    t_flag = False
    for tok in text_list2:
        answer = next((m for m in abbr_month if tok in m), None)
        if answer is not None and not t_flag:
            answer2 = next((m for m in abbr_month if m in tok), None)
            if answer2 is not None and not t_flag:
                t_flag = True
                # answer2 should contain the element that matches.  We need to find the span in the original phrase and return the correct value
                start_idx, end_idx = calculateSpan(text_lower, answer2)
                absStart = refStart_span + start_idx
                absEnd = refStart_span + end_idx
                postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

                if postag == "NNP":
                    if answer2 in ["jan."]:
                        return True, "January", start_idx, end_idx
                    elif answer2 in ["feb."]:
                        return True, "February", start_idx, end_idx
                    elif answer2 in ["mar."]:
                        return True, "March", start_idx, end_idx
                    elif answer2 in ["apr."]:
                        return True, "April", start_idx, end_idx
                    elif answer2 in ["jun."]:
                        return True, "June", start_idx, end_idx
                    elif answer2 in ["jul."]:
                        return True, "July", start_idx, end_idx
                    elif answer2 in ["aug."]:
                        return True, "August", start_idx, end_idx
                    elif answer2 in ["sept.", "sep."]:
                        return True, "September", start_idx, end_idx
                    elif answer2 in ["oct."]:
                        return True, "October", start_idx, end_idx
                    elif answer2 in ["nov."]:
                        return True, "November", start_idx, end_idx
                    elif answer2 in ["dec."]:
                        return True, "December", start_idx, end_idx

    # run for abbr month without punctuation
    abbr_month = ["jan", "feb", "mar", "apr", "jun", "jul", "aug", "sept", "sep", "oct", "nov", "dec"]
    adj_punc = '!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~'
    text_norm2 = text_lower.translate(str.maketrans(adj_punc, ' ' * len(adj_punc))).strip()
    # convert to list
    text_list2 = text_norm2.split(" ")

    t_flag = False
    for tok in text_list2:
        answer = next((m for m in abbr_month if tok in m), None)
        if answer is not None and not t_flag:
            answer2 = next((m for m in abbr_month if m in tok), None)
            if answer2 is not None and not t_flag:
                t_flag = True
                # answer2 should contain the element that matches.  We need to find the span in the original phrase and return the correct value
                start_idx, end_idx = calculateSpan(text_lower, answer2)
                absStart = refStart_span + start_idx
                absEnd = refStart_span + end_idx
                postag = ref_list[utils.getRefIdx(ref_list, absStart, absEnd)].getPos()

                if postag == "NNP":
                    if answer2 in ["jan"]:
                        return True, "January", start_idx, end_idx
                    elif answer2 in ["feb"]:
                        return True, "February", start_idx, end_idx
                    elif answer2 in ["mar"]:
                        return True, "March", start_idx, end_idx
                    elif answer2 in ["apr"]:
                        return True, "April", start_idx, end_idx
                    elif answer2 in ["jun"]:
                        return True, "June", start_idx, end_idx
                    elif answer2 in ["jul"]:
                        return True, "July", start_idx, end_idx
                    elif answer2 in ["aug"]:
                        return True, "August", start_idx, end_idx
                    elif answer2 in ["sept", "sep"]:
                        return True, "September", start_idx, end_idx
                    elif answer2 in ["oct"]:
                        return True, "October", start_idx, end_idx
                    elif answer2 in ["nov"]:
                        return True, "November", start_idx, end_idx
                    elif answer2 in ["dec"]:
                        return True, "December", start_idx, end_idx

    return False, None, None, None