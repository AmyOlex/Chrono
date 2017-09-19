## Class definitions for all TimeNorm entities - Intervals, Periods, Repeating-Intervals, and Operators.
#
# Date: 9/19/17
#
# Programmer Name: Luke Maffey

## Superclass for all entities
# @param id Assigned ID number
# @param start_span The location of the first character
# @param end_span The location of the last character
# @param type The type of the entity
# @param parent_type The parent type of the entity
class t6Entity :

	## The constructor
	def __init__(self, id, start_span, end_span, type, parent_type) :
		self.id = id

		## @var start_span
		# Where the entity starts in the text
		self.start_span = start_span
		self.end_span = end_span
		self.type = type
		self.parent_type = parent_type

	def __str__(self) :
		return self.id + " " + self.type

	## Sets the entity's ID
	#  @param id The ID to set it to
	def setID(self, id) :
		self.id = id

	def getID(self) :
		return self.id

	def printString(self) :
		print __str__(self)

	def parentType(self) :
		return self.parent_type

	##Prints the XML representation of the entity
	def printXML(self) :
		print "<XML>"
		
class t6IntervalEntity(t6Entity) :
	def __init__(self, id, start_span, end_span, type) :
		super().__init__(self, id, start_span, end_span, type, "Interval")

class t6YearEntity(t6IntervalEntity) :
	def __init__(self, id, start_span, end_span, value, subInterval, modifier) :
		super().__init__(self, id, start_span, end_span, "Year")
		self.value = value
		self.subInterval = subInterval
		self.modifier = modifier

class t6PeriodEntity(t6Entity) :
	def __init__(self, id, start_span, end_span, periodType, number, modifier) :
		super().__init__(self, id, start_span, end_span, "Period", "Duration")
		self.periodType = periodType
		self.number = number
		self.modifier = modifier

class t6RepeatingIntervalEntity(t6Entity) :
	def __init__(self, id, start_span, end_span, type) :
		super().__init__(self, id, start_span, end_span, repeatingType, "Repeating-Interval")

class t6MonthOfYearEntity(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, monthType, subInterval, number, modifier) :
		super().__init__(self, id, start_span, end_span, "Month-Of-Year")
		self.monthType = monthType
		self.subInterval = subInterval
		self.number = number
		self.modifier = modifier

class t6WeekOfYearEntity(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, subInterval, number, modifier) :
		super().__init__(self, id, start_span, end_span, "Week-Of-Year")
		self.subInterval = subInterval
		self.number = number
		self.modifier = modifier

class t6DayOfMonthEntity(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, subInterval, number, modifier) :
		super().__init__(self, id, start_span, end_span, "Day-Of-Month")
		self.value = value
		self.subInterval = subInterval
		self.number = number
		self.modifier = modifier

class t6DayOfWeekEntity(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, dayType, subInterval, number, modifier) :
		super().__init__(self, id, start_span, end_span, "Day-Of-Week")
		self.dayType = dayType
		self.subInterval = subInterval
		self.number = number
		self.modifier = modifier

class t6HourOfDayEntity(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, ampm, timeZone, subInterval, number, modifier) :
		super().__init__(self, id, start_span, end_span, "Hour-Of-Day")
		self.value = value
		self.ampm = ampm
		self.timeZone = timeZone
		self.subInterval = subInterval
		self.number = number
		self.modifier = modifier

class t6MinuteOfHourEntity(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, subInterval, number, modifier) :
		super().__init__(self, id, start_span, end_span, "Minute-Of-Hour")
		self.value = value
		self.subInterval = subInterval
		self.number = number
		self.modifier = modifier

class t6SecondOfMinuteEntity(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, number, modifier) :
		super().__init__(self, id, start_span, end_span, "Second-Of-Minute")
		self.value = value
		self.number = number
		self.modifier = modifier

class t6CalendarIntervalEntity(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, calendarType, number, modifier) :
		super().__init__(self, id, start_span, end_span, "Calendar-Interval")
		self.calendarType = calendarType
		self.number = number
		self.modifier = modifier

class t6PartOfDayEntity(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, partOfDayType, number, modifier) :
		super().__init__(self, id, start_span, end_span, "Part-Of-Day")
		self.partOfDayType = partOfDayType
		self.number = number
		self.modifier = modifier

class t6AMPMOfDay(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, ampmType, number, modifier) :
		super().__init__(self, id, start_span, end_span, "AMPM-Of-Day")
		self.ampmType = ampmType
		self.number = number
		self.modifier = modifier

class t6TimeZoneEntity(t6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span) :
		super().__init__(self, id, start_span, end_span, "Time-Zone")

class t6Operator(t6Entity) :
	def __init__(self, id, start_span, end_span, operatorType) :
		super().__init__(self, id, start_span, end_span, operatorType, "Operator")

