###############################
# Programmer Name: Luke Maffey
# Date: 9/19/17
# Module Purpose: Class definitions for all TimeNorm entities - Intervals, Periods, Repeating-Intervals, and Operators.
#################################

class t6Entity :
	def __init__(self, id, start_span, end_span, type, parent_type) :
		self.id = id
		self.start_span = start_span
		self.end_span = end_span
		self.type = type
		self.parent_type = parent_type

	def __str__(self) :
		return self.id + " " + self.type

	def setID(self, id) :
		self.id = id

	def getID(self) :
		return self.id

	def printString(self) :
		print __str__(self)

	def parentType(self) :
		return self.parent_type

	def printXML(self) :
		print "<XML>"

class t6IntervalEntity(t6Entity) :
	def __init__(self, id, start_span, end_span, value) :
		super().__init__(self, id, start_span, end_span, "Calendar-Interval", "Repeating-Interval")
		self.value = value

class t6PeriodEntity(t6Entity) :
	def __init__(self, id, start_span, end_span, periodType) :
		super().__init__(self, id, start_span, end_span, "Period", "Duration")
		self.periodType = periodType

class t6RepeatingIntervalEntity(t6Entity) :
	def __init__(self, id, start_span, end_span, repeatingType) :
		super().__init__(self, id, start_span, end_span, reapeatingType, "Repeating-Interval")

class t6Operator(t6Entity) :
	def __init__(self, id, start_span, end_span, operatorType) :
		super().__init__(self, id, start_span, end_span, operatorType, "Operator")

