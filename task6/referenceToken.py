## Class definitions to represent a whitespace-parsed token in the raw text file.
#
# Date: 9/19/17
#
# Programmer Name: Amy Olex

## Class to define a whitespace-parsed token from raw text.
# @param id Unique numerical ID
# @param text The text of the token
# @param start_span The location of the first character
# @param end_span The location of the last character
# @param pos The part of speech assigned to this token
# @param temporal A boolean indicating if this token contains any temporal components
class refToken :

	## The constructor
	def __init__(self, id, text, start_span, end_span, pos, temporal) :
		self.id = id
		self.text = text
		self.start_span = start_span
		self.end_span = end_span
		self.pos = pos
		self.temporal = temporal

	def __str__(self) :
		return self.id + " " + self.text

	#### Methods to SET properties ###
	
	## Sets the entity's ID
	#  @param id The ID to set it to
	def setID(self, id) :
		self.id = id
		
	## Sets the entity's text
	#  @param text The text to set it to
	def setText(self, text) :
		self.text = text
		
	## Sets the entity's span
	#  @param start The start index
	#  @param end The ending index
	def setSpan(self, start, end) :
		self.start_span = start
		self.end_span = end
		
	## Sets the entity's POS
	#  @param pos The part of speech assigned to the token
	def setPos(self, pos) :
		self.pos = pos
		
	## Sets the entity's temporal flag
	#  @param temp A boolean, 1 if it is a temporal token, 0 otherwise
	def setTemporal(self, temp) :
		self.temporal = temp
		
	#### Methods to GET properties ####
	
	## Gets the entity's ID
	def getID(self) :
		return(self.id)
		
	## Gets the entity's text
	def getText(self) :
		return(self.text)
		
	## Gets the entity's span
	def getSpan(self) :
		return(self.start_span, self.end_span)
		
	## Gets the entity's POS
	def getPos(self, pos) :
		return(self.pos)
		
	## Gets the entity's temporal flag
	def isTemporal(self, temp) :
		return(self.temporal)
