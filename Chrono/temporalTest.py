## Methods to identify temporal entities.
#
# Date: 12/23/17
#
# Programmer Name: Amy Olex

import string
from Chrono import utils

## Takes in a single text string and identifies if it is a month of the year
# @author Amy Olex
# @param text The text to parse
# @return value The normalized string value for the month of the year, or None if no month of year found.
def hasTextMonth(text):
    
    #Note: I took out converting to lower case because the capitilazation adds information for month mentions.
    #remove all commas
    text_norm = text.translate(str.maketrans("", "", ","))
    #convert to list
    #text_list = text_norm.split(" ")
    
    #define my day lists
    full_month = ["January","February","March","April","May","June","July","August","September","October","November","December","january","february","march","april","june","july","august","september","october","november","december"]
    abbr_month = ["Jan.", "Feb.","Mar.","Apr.","Jun.","Jul.","Aug.","Sept.","Oct.","Nov.","Dec.","jan.","feb.","mar.","apr.","jun.","jul.","aug.","sept.","oct.","nov.","dec."]
    
    answer = next((m for m in full_month if m in text_norm), None)
    if answer is not None:
        return True
    else:
        answer2 = next((a for a in abbr_month if a in text_norm), None)
        if answer2 is not None:
            return True
        else:
            return False

    
####
#END_MODULE
####

## Takes in a single text string and identifies if it is a day of the week
# @author Amy Olex
# @param text The text to parse
# @return value True if day of week is found, False otherwise.
def hasDayOfWeek(text):
    
    #Note: I took out converting to lower case because the capitilazation adds information for day of week mentions.
    #remove all commas
    text_norm = text.translate(str.maketrans("", "", ","))
    #convert to list
    #text_list = text_norm.split(" ")
    
    #define my day lists
    full_day = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    abbr_day = ["Mon.","Tues.","Wed.","Thurs.","Fri.","Sat.","Sun."]

    answer = next((m for m in full_day if m in text_norm), None)
    if answer is not None:
        return True
    else:
        answer2 = next((a for a in abbr_day if a in text_norm), None)
        if answer2 is not None:
            return True
        else:
            return False

####
#END_MODULE
####

## Takes in a text string and identifies if it has any calendar interval phrases like "week" or "days"
# @author Amy Olex
# @param text The string being parsed
# @return True if a calendar interval or period phrase exists, False otherwise.
def hasPeriodInterval(text):
    
    #convert to all lower
    text_lower = text.lower()
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my period lists
    terms = ["quarter","decades","decade","yesterday","yesterdays","today","todays","day","week","month","year","daily","weekly","monthly","yearly","century","minute","second","hour","hourly","days","weeks","months","years","centuries", "minutes","seconds","hours"]#,"recently"]
    ## possibly add in abbreviations like yr, sec, min, etc.
    
    answer = next((m for m in terms if m in text_norm), None)
    if answer is not None:
        return True
    else:
        return False
    
####
#END_MODULE
####

## Takes in a single text string and identifies if it has any AM or PM phrases
# @author Amy Olex
# @param text The string being parsed
# @return Outputs True if an AMPM exists, False otherwise.
# Note: this may be a little strict. I require the text to be found in the list, and a list item to be found in the text string.
# Thus, strings such as 1330AM won't be identified, but that could probably be caught with some other method.
def hasAMPM(text):
    
    #remove all ounctuation except periods
    punct = "!\"#$%&\'()*+,-/:;<=>?@[]^_`{|}~"
    text_norm = text.translate(str.maketrans(punct, ' '*len(punct))).strip()
    #convert to list
    text_list = text_norm.split(' ')
    
    #define my day lists
    am = ["AM","am","A.M.","AM.","a.m.","am."]
    pm = ["PM","pm","P.M.","p.m.","pm.","PM."]
    
    ampm = am+pm
    
    t_flag = False
    for t in text_list:
        answer = next((m for m in ampm if t in m), None)
        if answer is not None and not t_flag:
            answer2 = next((m for m in ampm if m in t), None)
            if answer2 is not None and not t_flag:
                t_flag = True

    
    return t_flag
    
####
#END_MODULE
####

## Takes in a single text string and identifies if it has any 4 digit 24-hour time phrases
# @author Amy Olex
# @param text The string being parsed
# @return Outputs True if possible 24-hour time, False otherwise
def has24HourTime(text):
    
    punct = "!\"#$%&\'()*+,-/:;<=>?@[]^_`{|}~"
    text_norm = text.translate(str.maketrans(punct, ' '*len(punct))).strip()
    #convert to list
    text_list = text_norm.split(' ')
    

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            if len(text) == 4:
                num = utils.getNumberFromText(text)
                if num is not None:
                    hour = utils.getNumberFromText(text[:2])
                    minute = utils.getNumberFromText(text[2:])
                    if (hour is not None) and (minute is not None):
                        if (minute > 60) or (hour > 24):
                            return False
                        else:
                            return True

    return False
    
####
#END_MODULE
####

## Takes in a single text string and identifies if it has any 6 or 8 digit dates
# @author Amy Olex
# @param text The string being parsed
# @return Outputs True if possible date, False otherwise
def hasDateOrTime(text):
    
    punct = "!\"#$%&\'()*+,-/:;<=>?@[]^_`{|}~"
    text_norm = text.translate(str.maketrans(punct, ' '*len(punct))).strip()
    #convert to list
    text_list = text_norm.split(' ')
    

    if len(text_list)>0:
        #loop through list looking for expression
        for text in text_list:
            if len(text) == 4:
                num = utils.getNumberFromText(text)
                if (num >= 1800) and (num <= 2050):
                    ## for 4 digit years, but not all 4 digit numbers will be temporal. I set a specific range for 4-digit years.
                    return True
            if len(text) == 6:
                ## could be yymmdd or mmddyy
                ## possible ranges for the year: 00 - 99
                ## possible ranges for the month: 01-12
                ## possible ranges for the day: 01-31
                ## It will be hard to narrow down these ranges at this point without context.
                return True
            if len(text) == 8:
                return True

    return False
    
####
#END_MODULE
####


## Takes in a string and identifies if it has any part of week terms, like "weekend"
# @author Amy Olex
# @param text String being parsed
# @return Outputs True if it contains a Part of Week.
def hasPartOfWeek(text):
    
    #convert to all lower
    text_lower = text.lower()
    #remove all punctuation
    text_norm = text.translate(str.maketrans(string.punctuation, " "*len(string.punctuation))).strip()
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my period lists
    partofday = ["weekend", "weekends"]
    
    for t in text_list:
        answer = next((m for m in partofday if m in t), None)
        if answer is not None:
            return True
        else:
            return False
    
####
#END_MODULE
####

## Takes in a string and identifies if it has any season terms, like "Summer"
# @author Amy Olex
# @param text String being parsed
# @return Outputs True if it contains a season.
def hasSeasonOfYear(text):
    
    #convert to all lower
    text_lower = text.lower()
    #remove all punctuation
    text_norm = text.translate(str.maketrans(string.punctuation, " "*len(string.punctuation))).strip()
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my season lists
    seasonofyear = ["summer", "winter", "fall", "spring"]
    
    for t in text_list:
        answer = next((m for m in seasonofyear if m in t), None)
        if answer is not None:
            answer2 = next((m for m in seasonofyear if t in m), None)
            if answer2 is not None:
                return True
            else:
                return False
    return False
####
#END_MODULE
####

## Takes in a string and identifies if it has any part of day terms, like "morning"
# @author Amy Olex
# @param text String being parsed
# @return Outputs True if it contains a part of day.
def hasPartOfDay(text):
    
    #convert to all lower
    text_lower = text.lower()
    #remove all punctuation
    text_norm = text_lower.translate(str.maketrans(string.punctuation, " "*len(string.punctuation))).strip()
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my part of day lists
    partofday = ["morning","evening","afternoon","night","dawn","dusk","tonight","overnight","nights","mornings","evening","afternoons","noon"] 
    
    for t in text_list:
        answer = next((m for m in partofday if m in t), None)
        if answer is not None:
            return True
        else:
            return False
    return False
####
#END_MODULE
####

## Takes in a string and identifies if it has a lone time zone like "EST"
# @author Amy Olex
# @param text String being parsed
# @return Outputs True if it contains a time zone.
def hasTimeZone(text):
    
    #remove all punctuation
    text_norm = text.translate(str.maketrans(string.punctuation, " "*len(string.punctuation))).strip()
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my season lists
    zones = ["AST","EST","EDT","CST","CDT","MST","MDT","PST","PDT","AKST","HST","HAST","HADT","SST","SDT","GMT","CHST","UTC"]
    
    for t in text_list:
        answer = next((m for m in zones if m in t), None)
        if answer is not None:
            answer2 = next((m for m in zones if t in m), None)
            if answer2 is not None:
                return True
            else:
                return False
    return False
####
#END_MODULE
####


## Takes in a string and identifies if it contains the temporal word "now"
# @author Amy Olex
# @param text String being parsed
# @return Outputs True if it contains "now"
def hasTempText(text):
    
    #remove all punctuation and convert to lowercase
    text_norm = text.translate(str.maketrans(string.punctuation, " "*len(string.punctuation))).strip().lower()
    #convert to list
    text_list = text_norm.split(" ")
    
    temp_text = ["now", "current", "last", "before", "previously", "ago", "pre", "after", "later", "earlier", "until", "quarter", "time"]
    
    for t in text_list:
        answer = next((m for m in temp_text if m in t), None)
        if answer is not None:
            answer2 = next((m for m in temp_text if t in m), None)
            if answer2 is not None:
                return True
            else:
                return False
    return False


## Takes in a string and identifies if it contains a temporal modifier
# @author Luke Maffey
# @param text String being parsed
# @return Outputs True if it contains a modifier
def hasModifierText(text):
    # remove all punctuation and convert to lowercase
    text_norm = text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation))).strip().lower()
    # convert to list
    text_list = text_norm.split(" ")

    temp_text = ["nearly", "almost", "or so", "late", "mid","fiscal","fy", "over", "early"]

    for t in text_list:
        answer = next((m for m in temp_text if m in t), None)
        if answer is not None:
            answer2 = next((m for m in temp_text if t in m), None)
            if answer2 is not None:
                return True
            else:
                return False
    return False
####
#END_MODULE
####