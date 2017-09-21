## Class definitions for all TimeNorm entities - Intervals, Periods, Repeating-Intervals, and Operators.
#---------------------------------------------------------------------------------------------------------
# Date: 9/19/17
#
# Programmer Name: Luke Maffey
#

## Superclass for all entities
#
# Entities are either an Interval, Period, Repeating-Interval, or Operator
# @param id Assigned ID number
# @param start_span The location of the first character
# @param end_span The location of the last character
# @param type The type of the entity
# @param parent_type The parent type of the entity
class T6Entity :

	## The constructor
	def __init__(self, id, start_span, end_span, type, parent_type) :
		self.id = id
		self.start_span = start_span
		self.end_span = end_span
		self.type = type
		self.parent_type = parent_type

	def __str__(self) :
		return self.id + " " + self.type

	## Sets the entity's ID
	#  @param id The ID to set it to
	def set_id(self, id) :
		self.id = id

	def get_id(self) :
		return self.id

	def print_string(self) :
		print(str(self))

	def parent_type(self) :
		return self.parent_type

	## Prints the XML representation of the entity
	#
	# Subclasses need to close the properties and entities tags
	def print_xml(self) :
		print("<entity>\n\t<id>{}</id>\n\t<span>{},{}</span>\n\t"
			  "<type>{}</type>\n\t<parentsType>{}</parentsType>"
			  "\n\t<properties>".format(
			  	self.id, self.start_span, self.end_span, self.type, 
			  	self.parent_type))

## An interval, just super classes for year interval for consistency
class T6IntervalEntity(T6Entity) :
	def __init__(self, id, start_span, end_span, type) :
		super().__init__(id, start_span, end_span, type, "Interval")

## A year interval
# @param value Which year
# @param sub_interval The associated sub-interval
# @param modifier Any modifiers, sometimes "approx"
class T6YearEntity(T6IntervalEntity) :
	def __init__(self, id, start_span, end_span, value, sub_interval=None, modifier=None) :
		super().__init__(id, start_span, end_span, "Year")
		self.value = value
		self.sub_interval = sub_interval
		self.modifier = modifier

	def print_xml(self) :
		super().print_xml()
		print("\t\t<Value>{}</Value>\n\t\t<Sub-Interval>{}</Sub-Interval>\n"
			  "\t\t<Modifier>{}</Modifier>\n\t</properties>\n</entity>".format(
			  	self.value, str(self.sub_interval or ''), str(self.modifier or '')))

class T6PeriodEntity(T6Entity) :
	def __init__(self, id, start_span, end_span, period_type=None, number=None, modifier=None) :
		super().__init__(id, start_span, end_span, "Period", "Duration")
		self.period_type = period_type
		self.number = number
		self.modifier = modifier

class T6repeatingIntervalEntity(T6Entity) :
	def __init__(self, id, start_span, end_span, type) :
		super().__init__(id, start_span, end_span, repeatingType, "Repeating-Interval")

class T6MonthOfYearEntity(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, month_type, sub_interval, number, modifier) :
		super().__init__(id, start_span, end_span, "Month-Of-Year")
		self.month_type = month_type
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

class T6WeekOfYearEntity(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, sub_interval, number, modifier) :
		super().__init__(id, start_span, end_span, "Week-Of-Year")
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

class T6DayOfMonthEntity(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, sub_interval, number, modifier) :
		super().__init__(id, start_span, end_span, "Day-Of-Month")
		self.value = value
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

class T6DayOfWeekEntity(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, dayType, sub_interval, number, modifier) :
		super().__init__(id, start_span, end_span, "Day-Of-Week")
		self.dayType = dayType
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

class T6HourOfDayEntity(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, ampm, time_zone, sub_interval, number, modifier) :
		super().__init__(id, start_span, end_span, "Hour-Of-Day")
		self.value = value
		self.ampm = ampm
		self.time_zone = time_zone
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

class T6MinuteOfHourEntity(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, sub_interval, number, modifier) :
		super().__init__(id, start_span, end_span, "Minute-Of-Hour")
		self.value = value
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

class T6SecondOfMinuteEntity(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, number, modifier) :
		super().__init__(id, start_span, end_span, "Second-Of-Minute")
		self.value = value
		self.number = number
		self.modifier = modifier

class T6CalendarIntervalEntity(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, calendar_type, number, modifier) :
		super().__init__(id, start_span, end_span, "Calendar-Interval")
		self.calendar_type = calendar_type
		self.number = number
		self.modifier = modifier

class T6PartOfDayEntity(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, part_of_day_type, number, modifier) :
		super().__init__(id, start_span, end_span, "Part-Of-Day")
		self.part_of_day_type = part_of_day_type
		self.number = number
		self.modifier = modifier

class T6AMPMOfDay(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, ampm_type, number, modifier) :
		super().__init__(id, start_span, end_span, "AMPM-Of-Day")
		self.ampm_type = ampm_type
		self.number = number
		self.modifier = modifier

class T6time_zoneEntity(T6repeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span) :
		super().__init__(id, start_span, end_span, "Time-Zone")

class T6Operator(T6Entity) :
	def __init__(self, id, start_span, end_span, operator_type) :
		super().__init__(id, start_span, end_span, operator_type, "Operator")


class T6SumOperator(T6Operator) :
	def __init__(self, id, start_span, end_span) :
		super().__init__(id, start_span, end_span, "Sum")


class T6DifferenceOperator(T6Operator) :
	def __init__(self, id, start_span, end_span) :
		super().__init__(id, start_span, end_span, "Difference")


class T6UnionOperator(T6Operator) :
	def __init__(self, id, start_span, end_span) :
		super().__init__(id, start_span, end_span, "Union")


class T6IntersectionOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, intervals, repeating_intervals) :
		super().__init__(id, start_span, end_span, "Intersection")
		self.intervals = intervals
		self.repeating_intervals = repeating_intervals


class T6EveryNthOperator(T6Operator) :
	def __init__(self, id, start_span, end_span) :
		super().__init__(id, start_span, end_span, "Every-Nth")

## Create a last(Period) or last(Repeating-Interval) operator
# @param semantics {Interval-Included, Interval-Not-Included}
class T6LastOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, semantics, interval_type, interval, period, repeating_interval) :
		super().__init__(id, start_span, end_span, "Last")
		self.semantics = semantics
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval

class T6NextOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type, interval, period, repeating_interval, semantics) :
		super().__init__(id, start_span, end_span, "Next")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval
		self.semantics = semantics

class T6ThisOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type, interval, period, repeating_interval) :
		super().__init__(id, start_span, end_span, "This")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval

class T6BeforeOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type, interval, period, repeating_interval) :
		super().__init__(id, start_span, end_span, "Before")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval

class T6AfterOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type, interval, period, repeating_interval, semantics) :
		super().__init__(id, start_span, end_span, "After")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval
		self.semantics = semantics

class T6BetweenOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type, interval, period, repeating_interval) :
		super().__init__(id, start_span, end_span, "Between")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval

class T6NthOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type, interval, period, repeating_interval) :
		super().__init__(id, start_span, end_span, "Nth")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval

class T6TwoDigitYearOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type, interval, period, sub_interval) :
		super().__init__(id, start_span, end_span, "Two-Digit-Year")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.sub_interval = sub_interval

class T6Number(T6Entity) :
	def __init__(self, id, start_span, end_span, value) :
		super().__init__(id, start_span, end_span, "Number", "Other")
		self.value = value

class T6Modifier(T6Entity) :
	def __init__(self, id, start_span, end_span, modifier) :
		super().__init__(id, start_span, end_span, "Modifier", "Other")
		self.modifier = modifier

class T6Event(T6Entity) :
	def __init__(self, id, start_span, end_span) :
		super().__init__(id, start_span, end_span, "Event", "Other")