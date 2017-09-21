## Class definitions for all TimeNorm entities - Intervals, Periods, 
# Repeating-Intervals, and Operators.
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

	## Tells python how to convert a T6Entity to a string
	def __str__(self) :
		return self.id + " " + self.type

	##  @param id The ID to set it to
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
			  "\n\t<properties>".format(self.id, self.start_span,
			  self.end_span, self.type,	self.parent_type))

## Super class for Intervals which are defined as years
class T6IntervalEntity(T6Entity) :
	def __init__(self, id, start_span, end_span, type) :
		super().__init__(id, start_span, end_span, type, "Interval")

## A year interval
# @param value Which year, e.g. 1998
# @param sub_interval The associated sub-interval, defaults to None
# @param modifier Any modifiers, sometimes "approx", defaults to None
class T6YearEntity(T6IntervalEntity) :
	def __init__(self, id, start_span, end_span, value, sub_interval=None, 
		         modifier=None) :
		super().__init__(id, start_span, end_span, "Year")
		self.value = value
		self.sub_interval = sub_interval
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Value>{}</Value>\n\t\t<Sub-Interval>{}</Sub-Interval>\n"
			  "\t\t<Modifier>{}</Modifier>\n\t</properties>\n</entity>\n".format(
			  	self.value, self.sub_interval or '', self.modifier or ''))

## A period of the type of time given
# @param period_type Required {Weeks, Days,...}
# @param number Required
class T6PeriodEntity(T6Entity) :
	def __init__(self, id, start_span, end_span, period_type, number,
	             modifier=None) :
		super().__init__(id, start_span, end_span, "Period", "Duration")
		self.period_type = period_type
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Type>{}</Type>\n\t\t<Number>{}</Number>\n"
			  "\t\t<Modifier>{}</Modifier>\n\t</properties>\n</entity>\n".format(
			  self.period_type, self.number or '', self.modifier or ''))

## Super class for all Repeating-intervals
class T6RepeatingIntervalEntity(T6Entity) :
	def __init__(self, id, start_span, end_span, repeatingType) :
		super().__init__(id, start_span, end_span, repeatingType,
		                 "Repeating-Interval")

## @param month_type Required {January, Februray,...}
class T6MonthOfYearEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, month_type, sub_interval=None,
	             number=None, modifier=None) :
		super().__init__(id, start_span, end_span, "Month-Of-Year")
		self.month_type = month_type
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Type>{}</Type>\n\t\t<Sub-Interval>{}</Sub-Interval>\n"
			  "\t\t<Number>{}</Number>\n\t\t<Modifier>{}</Modifier>\n"
			  "\t</properties>\n</entity>\n".format(self.month_type,
			  self.sub_interval or '', self.number or '', self.modifier or ''))

## Based on the paper, I assume this takes a value to denote which week of the year
# @param value Required {1-52}
class T6WeekOfYearEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, sub_interval=None,
		         number=None, modifier=None) :
		super().__init__(id, start_span, end_span, "Week-Of-Year")
		self.value = value
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	#
	# No examples, so this is the assumed format
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Value>{}</Value>\n\t\t<Sub-Interval>{}</Sub-Interval>\n"
			  "\t\t<Number>{}</Number>\n\t\t<Modifier>{}</Modifier>\n"
			  "\t</properties>\n</entity>\n".format(self.sub_interval or '',
			  self.number or '', self.modifier or ''))

## @param value Required {1-31}
class T6DayOfMonthEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, sub_interval=None,
	             number=None, modifier=None) :
		super().__init__(id, start_span, end_span, "Day-Of-Month")
		self.value = value
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Value>{}</Value>\n\t\t<Sub-Interval>{}</Sub-Interval>\n"
			  "\t\t<Number>{}</Number>\n\t\t<Modifier>{}</Modifier>\n"
			  "\t</properties>\n</entity>\n".format(self.value,
			  self.sub_interval or '', self.number or '', self.modifier or ''))

## @param day_type Required {"Monday" - "Sunday"}
class T6DayOfWeekEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, day_type, sub_interval=None,
		         number=None, modifier=None) :
		super().__init__(id, start_span, end_span, "Day-Of-Week")
		self.dayType = day_type
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Type>{}</Type>\n\t\t<Sub-Interval>{}</Sub-Interval>\n"
			  "\t\t<Number>{}</Number>\n\t\t<Modifier>{}</Modifier>\n"
			  "\t</properties>\n</entity>\n".format(self.day_type,
			  self.sub_interval or '', self.number or '', self.modifier or ''))

## @param value Required {0-24}
# @param ampm Optional, refers to a T6AMPMOfDayEntity
# @param time_zone Optional, refers to a T6TimeZoneEntity
class T6HourOfDayEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, ampm=None, time_zone=None,
	             sub_interval=None, number=None, modifier=None) :
		super().__init__(id, start_span, end_span, "Hour-Of-Day")
		self.value = value
		self.ampm = ampm
		self.time_zone = time_zone
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Value>{}</Value>\n\t\t<AMPM-Of-Day>{}</AMPM-Of-Day>\n"
			  "\t\t<Time-Zone>{}</Time-Zone>\n\t\t<Sub-Interval>{}</Sub-Interval>\n"
			  "\t\t<Number>{}</Number>\n\t\t<Modifier>{}</Modifier>\n"
			  "\t</properties>\n</entity>\n".format(self.value, self.ampm or '',
			  self.time_zone or '', self.sub_interval or '', self.number or '',
			  self.modifier or ''))

## @param value Required {0-59}
class T6MinuteOfHourEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, sub_interval=None, number=None, modifier=None) :
		super().__init__(id, start_span, end_span, "Minute-Of-Hour")
		self.value = value
		self.sub_interval = sub_interval
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Value>{}</Value>\n\t\t<Sub-Interval>{}</Sub-Interval>\n"
			  "\t\t<Number>{}</Number>\n\t\t<Modifier>{}</Modifier>\n"
			  "\t</properties>\n</entity>\n".format(self.value,
			  self.sub_interval or '', self.number or '', self.modifier or ''))

## @param value Required {0-59}
class T6SecondOfMinuteEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, value, number=None, modifier=None) :
		super().__init__(id, start_span, end_span, "Second-Of-Minute")
		self.value = value
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Value>{}</Value>\n\t\t<Number>{}</Number>\n"
			  "\t\t<Modifier>{}</Modifier>\n\t</properties>\n</entity>\n".format(
			  self.value, self.number or '', self.modifier or ''))

## Specifies a number of {days, weeks, months, etc}
# @param calendar_type Required {Day, Month, Week, etc}
class T6CalendarIntervalEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, calendar_type, number=None,
		         modifier=None) :
		super().__init__(id, start_span, end_span, "Calendar-Interval")
		self.calendar_type = calendar_type
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Type>{}</Type>\n\t\t<Number>{}</Number>\n"
			  "\t\t<Modifier>{}</Modifier>\n\t</properties>\n</entity>\n".format(
			  self.calendar_type, self.number or '', self.modifier or ''))

## @param part_of_day_type Required {Night, Morning, etc}
class T6PartOfDayEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, part_of_day_type, number=None,
		         modifier=None) :
		super().__init__(id, start_span, end_span, "Part-Of-Day")
		self.part_of_day_type = part_of_day_type
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Type>{}</Type>\n\t\t<Number>{}</Number>\n"
			  "\t\t<Modifier>{}</Modifier>\n\t</properties>\n</entity>\n".format(
			  self.part_of_day_type, self.number or '', self.modifier or ''))

## @param ampm_type Required {AM, PM}
class T6AMPMOfDayEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span, ampm_type, number=None,
		         modifier=None) :
		super().__init__(id, start_span, end_span, "AMPM-Of-Day")
		self.ampm_type = ampm_type
		self.number = number
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Type>{}</Type>\n\t\t<Number>{}</Number>\n"
			  "\t\t<Modifier>{}</Modifier>\n\t</properties>\n</entity>\n".format(
			  self.ampm_type, self.number or '', self.modifier or ''))

## No special parameters, just identifies the location of a time zone in text
class T6TimeZoneEntity(T6RepeatingIntervalEntity) :
	def __init__(self, id, start_span, end_span) :
		super().__init__(id, start_span, end_span, "Time-Zone")

	def print_xml(self) :
		super().print_xml()
		print("\t</properties>\n</entity>\n")

## Super class for all Operators
class T6Operator(T6Entity) :
	def __init__(self, id, start_span, end_span, operator_type) :
		super().__init__(id, start_span, end_span, operator_type, "Operator")


class T6SumOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, period_1, period_2) :
		super().__init__(id, start_span, end_span, "Sum")
		self.period_1 = period_1
		self.period_2 = period_2

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Period>{}</Period>\n\t\t<Period>{}</Period>\n"
			  "\t</properties>\n</entity>\n".format(self.period_1, self.period_2))

class T6DifferenceOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, period_1, period_2) :
		super().__init__(id, start_span, end_span, "Difference")
		self.period_1 = period_1
		self.period_2 = period_2

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Period>{}</Period>\n\t\t<Period>{}</Period>\n"
			  "\t</properties>\n</entity>\n".format(self.period_1, self.period_2))


class T6UnionOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, repeating_intervals_1,
		         repeating_intervals_2) :
		super().__init__(id, start_span, end_span, "Union")
		self.repeating_intervals_1 = repeating_intervals_1
		self.repeating_intervals_2 = repeating_intervals_2

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Repeating-Intervals>{}</Repeating-Intervals>\n"
			  "\t\t<Repeating-Intervals>{}</Repeating-Intervals>\n"
			  "\t</properties>\n</entity>\n".format(self.repeating_intervals_1,
			  self.repeating_intervals_2))

class T6IntersectionOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, repeating_intervals_1,
		         repeating_intervals_2) :
		super().__init__(id, start_span, end_span, "Intersection")
		self.repeating_intervals_1 = repeating_intervals_1
		self.repeating_intervals_2 = repeating_intervals_2

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Repeating-Intervals>{}</Repeating-Intervals>\n"
			  "\t\t<Repeating-Intervals>{}</Repeating-Intervals>\n"
			  "\t</properties>\n</entity>\n".format(self.repeating_intervals_1,
			  self.repeating_intervals_2))

## No examples, currently a placeholder
class T6EveryNthOperator(T6Operator) :
	def __init__(self, id, start_span, end_span) :
		super().__init__(id, start_span, end_span, "Every-Nth")

## Create a last(Period) or last(Repeating-Interval) operator, 
# must specify one or the other
# @param semantics {Interval-Included, Interval-Not-Included(default)}
# @param interval_type Defaults to "DocTime"
# @param interval Defaults to None
# @param period Defaults to None
# @param repeating_interval Defaults to None
class T6LastOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, semantics="Interval-Not-Included",
	             interval_type="DocTime",interval=None, period=None,
	             repeating_interval=None) :
		super().__init__(id, start_span, end_span, "Last")
		self.semantics = semantics
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Semantics>{}</Semantics>\n"
			  "\t\t<Interval-Type>{}</Interval-Type>\n"
			  "\t\t<Interval>{}</Interval>\n\t\t<Period>{}</Period>\n"
			  "\t\t<Repeating-Interval>{}</Repeating-Interval>\n"
			  "\t</properties>\n</entity>\n".format(self.semantics,
			  self.interval_type, self.interval or '', self.period or '',
			  self.repeating_interval or ''))

## Create a next(Period) or next(Repeating-Interval) operator, 
# must specify one or the other
# @param interval_type Defaults to "DocTime"
# @param interval Defaults to None
# @param period Defaults to None
# @param repeating_interval Defaults to None
# @param semantics {Interval-Included, Interval-Not-Included(default)}
class T6NextOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type="DocTime",
		         interval=None, period=None, repeating_interval=None,
		         semantics="Interval-Not-Included") :
		super().__init__(id, start_span, end_span, "Next")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval
		self.semantics = semantics

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Interval-Type>{}</Interval-Type>\n"
			  "\t\t<Interval>{}</Interval>\n\t\t<Period>{}</Period>\n"
			  "\t\t<Repeating-Interval>{}</Repeating-Interval>\n"
			  "\t\t<Semantics>{}</Semantics>\n"
			  "\t</properties>\n</entity>\n".format(self.interval_type,
			  self.interval or '', self.period or '',
			  self.repeating_interval or '', self.semantics))

## Create a This(Period) or This(Repeating-Interval) operator, 
# must specify one or the other
# @param interval_type Defaults to "DocTime"
# @param interval Defaults to None
# @param period Defaults to None
# @param repeating_interval Defaults to None
class T6ThisOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type="DocTime",
	             interval=None, period=None, repeating_interval=None) :
		super().__init__(id, start_span, end_span, "This")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Interval-Type>{}</Interval-Type>\n"
			  "\t\t<Interval>{}</Interval>\n\t\t<Period>{}</Period>\n"
			  "\t\t<Repeating-Interval>{}</Repeating-Interval>\n"
			  "\t</properties>\n</entity>\n".format(self.interval_type,
			  self.interval or '', self.period or '',
			  self.repeating_interval or ''))

## Create a before(Period) or before(Repeating-Interval) operator, 
# must specify one or the other
# @param interval_type Defaults to "DocTime"
# @param interval Defaults to None
# @param period Defaults to None
# @param repeating_interval Defaults to None
# @param semantics {Interval-Included, Interval-Not-Included(default)}
class T6BeforeOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type="DocTime",
		         interval=None, period=None, repeating_interval=None,
		         semantics="Interval-Not-Included") :
		super().__init__(id, start_span, end_span, "Before")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval
		self.semantics = semantics

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Interval-Type>{}</Interval-Type>\n"
			  "\t\t<Interval>{}</Interval>\n\t\t<Period>{}</Period>\n"
			  "\t\t<Repeating-Interval>{}</Repeating-Interval>\n"
			  "\t\t<Semantics>{}</Semantics>\n"
			  "\t</properties>\n</entity>\n".format(self.interval_type,
			  self.interval or '', self.period or '',
			  self.repeating_interval or '', self.semantics))

## Create an after(Period) or after(Repeating-Interval) operator, 
# must specify one or the other
# @param interval_type Defaults to "DocTime"
# @param interval Defaults to None
# @param period Defaults to None
# @param repeating_interval Defaults to None
# @param semantics {Interval-Included, Interval-Not-Included(default)}
class T6AfterOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type="DocTime",
		         interval=None, period=None, repeating_interval=None,
		         semantics="Interval-Not-Included") :
		super().__init__(id, start_span, end_span, "After")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.repeating_interval = repeating_interval
		self.semantics = semantics

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Interval-Type>{}</Interval-Type>\n"
			  "\t\t<Interval>{}</Interval>\n\t\t<Period>{}</Period>\n"
			  "\t\t<Repeating-Interval>{}</Repeating-Interval>\n"
			  "\t\t<Semantics>{}</Semantics>\n"
			  "\t</properties>\n</entity>\n".format(self.interval_type,
			  self.interval or '', self.period or '',
			  self.repeating_interval or '', self.semantics))


## Creates a between operator e.g. Between(Last(January(13)), DocTime)
# @param start_interval_type {Link, DocTime}
# @param start_interval Takes a link to an interval or None(Default) for DocTime
# @param end_interval_type {Link, DocTime}
# @param end_interval Takes a link to an interval or None(Default) for DocTime
# @param start_included {Included, Not-Included(default)}
# @param end_included {Included, Not-Included(default)}
class T6BetweenOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, start_interval_type,
	             start_interval=None, end_interval_type, end_interval=None,
	             start_included="Not-Included", end_included="Not-Included") :
		super().__init__(id, start_span, end_span, "Between")
		self.start_interval_type = start_interval_type
		self.start_interval = start_interval
		self.end_interval_type = end_interval_type
		self.end_interval = end_interval
		self.start_included = start_included
		self.end_included = end_included

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Start-Interval-Type>{}</Start-Interval-Type>\n"
			  "\t\t<Start-Interval>{}</Start-Interval>\n"
			  "\t\t<End-Interval-Type>{}</End-Interval-Type>\n"
			  "\t\t<End-Interval>{}</End-Interval>\n"
			  "\t\t<Start-Included>{}</Start-Included>\n"
			  "\t\t<End-Included>{}</End-Included>\n"
			  "\t</properties>\n</entity>\n".format(self.start_interval_type,
			  self.start_interval or '', self.end_interval_type,
			  self.end_interval or '', self.star_included, self.end_included))

## Creates and Nth operator e.g. 5th(Value) day(Calendar-Interval) 
# of 2016(Repeating-Interval)
# @param value The N in Nth
# @param interval The Calendar-Interval to link to
# @param repeating_interval The repeating interval to link to
class T6NthOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, value, interval,
	             repeating_interval) :
		super().__init__(id, start_span, end_span, "Nth")
		self.value = value
		self.interval = interval
		self.repeating_interval = repeating_interval

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Value>{}</Value>\n\t\t<Interval>{}</Interval>\n"
			  "\t\t<Repeating-Interval>{}</Repeating-Interval>\n"
			  "\t</properties>\n</entity>\n".format(self.value,
			  self.interval, self.repeating_interval or ''))

## Creates a two digit year operator
# @param interval_type Defaults to DocTime
# @param interval Defaults to None
class T6TwoDigitYearOperator(T6Operator) :
	def __init__(self, id, start_span, end_span, interval_type="DocTime",
	             interval=None, period, sub_interval) :
		super().__init__(id, start_span, end_span, "Two-Digit-Year")
		self.interval_type = interval_type
		self.interval = interval
		self.period = period
		self.sub_interval = sub_interval

	def print_xml(self) :
		super().print_xml()
		print("\t\t<Interval-Type>{}</Interval-Type>\n"
			  "\t\t<Interval>{}</Interval>\n\t\t<Value>{}</Value>\n"
			  "\t\t<Sub-Interval>{}</Sub-Interval>"
			  "\t</properties>\n</entity>\n".format(self.interval_type,
			  self.interval, self.value, self.sub_interval))

## Super class for all Other entities
class T6OtherEntity(T6Entity) :
	def __init__(self, id, start_span, end_span, otherType) :
		super().__init__(id, start_span, end_span, otherType, "Other")

class T6Number(T6OtherEntity) :
	def __init__(self, id, start_span, end_span, value) :
		super().__init__(id, start_span, end_span, "Number")
		self.value = value

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Value>{}</Value>\n\t</properties>\n"
			  "</entity>\n".format(self.value))

class T6Modifier(T6OtherEntity) :
	def __init__(self, id, start_span, end_span, modifier) :
		super().__init__(id, start_span, end_span, "Modifier")
		self.modifier = modifier

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t\t<Modifier>{}</Modifier>\n\t</properties>\n"
			  "</entity>\n".format(self.modifier))

class T6Event(T6OtherEntity) :
	def __init__(self, id, start_span, end_span) :
		super().__init__(id, start_span, end_span, "Event")

	## Prints the xml leaving empty variables blank
	def print_xml(self) :
		super().print_xml()
		print("\t</properties>\n</entity>\n")

