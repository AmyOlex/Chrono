## Methods to identify temporal entities.
#
# Date: 12/23/17
#
# Programmer Name: Amy Olex

import string

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
    full_month = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    abbr_month = ["Jan.", "Feb.","Mar.","Apr.","Jun.","Jul.","Aug.","Sept.","Oct.","Nov.","Dec."]

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
    text_norm = text_lower.translate(str.maketrans("", "", string.punctuation))
    #convert to list
    text_list = text_norm.split(" ")
    
    #define my period lists
    terms = ["decades","decade","yesterday","day","week","month","year","daily","weekly","monthly","yearly","century","minute","second","hour","hourly","days","weeks","months","years","centuries", "minutes","seconds","hours"]
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
                print("True: "+str(text_list))
                t_flag = True

    
    return t_flag
    
####
#END_MODULE
####