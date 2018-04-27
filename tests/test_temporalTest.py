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

def test_noAMPM():
    assert tt.hasAMPM("last 24 cupcakes") == False


# 24 hour time tests
def test_has24HourTime():
    assert tt.has24HourTime("I went to the store at 2347!") == True

def test_no24HourTime():
    assert tt.has24HourTime("I went to the store at 11:47pm!") == False

def test_no24HourTime2():
    assert tt.has24HourTime("I went to the store in 1986!") == False


# Date or Time tests
def test_hasDateOrTime():
    assert tt.hasDateOrTime("1986") == True

def test_hasDateOrTimeText():
    assert tt.hasDateOrTime("nineteen eighty six") == True

def test_hasDateOrTimeSix():
    assert tt.hasDateOrTime("060586") == True

def test_hasDateOrTimeEight():
    assert tt.hasDateOrTime("06051986") == True

def test_hasNoDateOrTime():
    assert tt.hasDateOrTime("060519867") == False


# Part of Week tests
def test_hasPartOfWeek():
    assert tt.hasPartOfWeek("weekend") == True

def test_hasNoPartOfWeek():
    assert tt.hasPartOfWeek("year") == False



# Season Tests
def test_hasSeason():
    assert tt.hasSeasonOfYear("winter") == True

def test_hasNoSeason():
    assert tt.hasSeasonOfYear("weekend") == False

def test_hasEmptySeason():
    assert tt.hasSeasonOfYear("") == False