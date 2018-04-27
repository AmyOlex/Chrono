import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "\\..\\")

from Chrono import temporalTest as tt


# Text Month tests
def test_hasTextMonthFull():
    assert tt.hasTextMonth("January") == True

def test_hasTextMonthAbbr():
    assert tt.hasTextMonth("Jan.") == True

def test_hasNoTextMonth():
    assert tt.hasTextMonth("Cold") == False


# Day of week tests
def test_hasDayOfWeekFull():
    assert tt.hasDayOfWeek("Monday") == True

def test_hasDayOfWeekAbbr():
    assert tt.hasDayOfWeek("Mon.") == True

def test_hasNoTextMonth():
    assert tt.hasDayOfWeek("Cold") == False


# Period Interval tests
def test_hasPeriodInterval():
    assert tt.hasPeriodInterval("this century") == True

def test_noPeriodInterval():
    assert tt.hasPeriodInterval("last 24 cupcakes") == False


# AMPM tests
def test_hasAMPM():
    assert tt.hasAMPM("in the a.m.!") == True

def test_hasAMPMSentence():
    assert tt.hasAMPM("I am going at 10 am and 3 pm") == True

def test_noAMPM():
    assert tt.hasAMPM("last 24 cupcakes") == False


# 24 hour time tests
def test_has24HourTime():
    assert tt.has24HourTime("I went to the store at 2359!") == True

def test_no24HourTime():
    assert tt.has24HourTime("I went to the store at 11:47pm!") == False

def test_no24HourTime2():
    assert tt.has24HourTime("I went to the store in 1986!") == False

def test_no24HourTime5():
    assert tt.has24HourTime("I went to the store in 23471!") == False

def test_no24HourTime3():
    assert tt.has24HourTime("I went to the store in 234!") == False

def test_24HourTime24():
    assert tt.has24HourTime("I went to the store in 2430!") == False

def test_24HourTime60():
    assert tt.has24HourTime("I went to the store in 1160!") == False

def test_24HourTimeSingle():
    assert tt.has24HourTime("0039") == True

def test_24HourTimeEmpty():
    assert tt.has24HourTime("") == False


# Date or Time tests
def test_hasDateOrTime():
    assert tt.hasDateOrTime("1986") == True

def test_hasNoDateOrTime5():
    assert tt.hasDateOrTime("18999") == False

def test_hasNoDateOrTime3():
    assert tt.hasDateOrTime("189") == False

def test_hasDateOrTimeText():
    assert tt.hasDateOrTime("nineteen eighty six") == True

def test_hasDateOrTimeSix():
    assert tt.hasDateOrTime("060586") == True

def test_hasDateOrTimeEight():
    assert tt.hasDateOrTime("06051986") == True

def test_hasNoDateOrTime9():
    assert tt.hasDateOrTime("060519867") == False

def test_hasDateOrTime2050():
    assert tt.hasDateOrTime("2050") == True

def test_hasDateOrTimeNull():
    assert tt.hasDateOrTime("") == False

def test_hasDateOrTime2051():
    assert tt.hasDateOrTime("2051") == False

def test_hasDateOrTime1799():
    assert tt.hasDateOrTime("1799") == False

def test_hasDateOrTime1800():
    assert tt.hasDateOrTime("1800") == True




# Part of Week tests
def test_hasPartOfWeek():
    assert tt.hasPartOfWeek("weekend") == True

def test_hasNoPartOfWeek():
    assert tt.hasPartOfWeek("year") == False


# Season Tests
def test_hasSeason():
    assert tt.hasSeasonOfYear("winter") == True

# Implement after bug fix
# def test_hasCapitalSeason():
#     assert tt.hasSeasonOfYear("Winter") == True

def test_hasNoSeason():
    assert tt.hasSeasonOfYear("weekend") == False

def test_hasEmptySeason():
    assert tt.hasSeasonOfYear("") == False


# Part of Day tests
def test_hasPartOfDay():
    assert tt.hasPartOfDay("morning") == True

def test_hasNoPartOfDay():
    assert tt.hasPartOfDay("weekend") == False


# Timezone tests
def test_hasTimeZone3():
    assert tt.hasTimeZone("EST") == True

def test_hasTimeZone4():
    assert tt.hasTimeZone("EEST") == True

# Implement after bug fix
# def test_hasNoTimeZone():
#     assert tt.hasTimeZone("EBST") == False

def test_hasNoTimeZone():
    assert tt.hasTimeZone("ABCD") == False

def test_hasEmptyTimeZone():
    assert tt.hasTimeZone("") == False


# Temp text tests
def test_hasTempText():
    assert tt.hasTempText("This past week") == True

def test_hasNoTempText():
    assert tt.hasTempText("In another year") == False


# Modifier text tests
def test_hasModifierText():
    assert tt.hasModifierText("Almost there now") == True

def test_hasNoModifierText():
    assert tt.hasModifierText("This time last year") == False