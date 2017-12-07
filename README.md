<!---
output:
  html_document: default
  pdf_document: default
--->

# SemEval-2018 Task 6 - Parsing Time Normalizations

### Amy Olex, Nicholas Morton, Luke Maffey

### CMSC516 - Advanced Natural Language Processing Fall 2017

---

### Usage
To use type:

```bash
>> source runit.sh [NB | NN | DT]
```

Input argument selects the type of machine learning algorithm to use:

* NB - Naive Bayes
* NN - Neural Network
* DT - Decision Tree

Full documentation available at documentation/index.html

### Roles and Contributions
 - *Amy Olex:* Team lead, workflow development lead, framework implementation, run_task6.py author, sutimeEntity.py 
 author, SUTime_To-T6.py method contributer, utils.py author, referenceToken.py author, presentation preparation, 
 README co-author, installation co-author and tester, literature review, naive bayes implementation, ML algorithm integration, lead feature vector developer and parsing implementation, gold standard parsing createMLTrainingMatrix.py author, gold_standard_utils.py author.
 - *Luke Maffey:* Doxygen code documentation lead, t6Entities.py author, stopword identification/editing and method 
 implementation, presentation preparation, README co-author, installation co-author and tester, literature review, GUTime testing, presentation preparation, neural network implementation.
 - *Nicholas Morton:* SUTime installation and implementation lead, HeidelTime/GUTime baseline implementation lead, SUTime python wrapper author, workflow development, SUTime_To-T6.py author, README co-author, installation co-author and tester, literature review, GUTime integration and testing, decision tree implementation.

---

### 1.  Introduction
Understanding and processing temporal information is vital for navigating life.  Humans are continually processing 
temporal information in their daily lives, including in written text. It is not possible to have a cohesive 
conversation, or write a coherent document without the use of temporal information.  For example, "I had a drink" versus 
"I have a drink" differ by only one word, but infer two different timelines of events.  The first phrase implies you 
have already ingested a drink prior to the statement, whereas the second implies you currently posses a drink, but it is 
not known whether or not you have ingested some of it already. The human mind processes this subtle temporal information 
instantly and effortlessly; however, it is difficult for computers to identify, process, and utilize this information in 
an automated fashion because it requires knowledge and understanding of syntax, semantics, and context to link time 
information to the correct events to order them on a timeline. For instance, Kuzey et al identified four types of 
temporal expressions, each of which presents a unique challenge for computers[<sup>1</sup>](#references):
> 1. _Explicit temporal expressions_ denote a precise time point or period...
> 2. _Relative temporal expressions_ refer to dates that can be interpreted with respect to a reference date...
> 3. _Implicit temporal expressions_ refer to special kinds of named events...
> 4. _Free-text temporal expressions_ refer to arbitrary kinds of named events or facts with temporal scopes that are 
merely given by a text phrase but have unique interpretations given the context and background knowledge...

Over the past few decades, the automated identification and extraction of temporal information from text has been an 
active field of study[<sup>2</sup>](#references).  Applications range from information extraction, automated question 
answering, and in the clinical field the identification of a patient's medical timeline from clinical texts. Since 2007, 
the SemEval tasks have included a temporal challege task[<sup>3</sup>](#references). In 2013, the TempEval3 challenge 
utilized the TimeBank/AQUAINT[<sup>4</sup>](#references) newswire corpus and focused on three tasks: A) time expression 
extraction and evaluation,  B) event identification, and c) identifying realtionships between the time expressions and 
their associated events[<sup>5</sup>](#references).  Since then the challenges have incorporated extrinsic evaluations 
by utilizing temporal annotations in a QA application[<sup>6</sup>](#references), and have moved from the news article 
domain to the clinical domain[<sup>7</sup>](#references). 

The TIMEX3[<sup>8</sup>](#references) scheme is used by TimeML[<sup>9</sup>](#references) and was developed out of the 
older TIMEX scheme created by DARPA in 1995[<sup>10,11</sup>](#references). TimeML annotates temporal information as a 
phrase and a normalized value that the phrase represents. For example, the phrase "The accident was on July 8, 2017 at 
5pm" would map to the temporal phrase "July 8, 2017 at 5am" and the value "2017-07-08T05:00:00". All SemEval challenges 
thus far, and most temporal annotation tools, have utilized the TimeML/TIMEX3[<sup>12</sup>](#references) standard for 
annotating temporal information.  While TIMEX3 can capture a lot of information, it has trouble representing times that 
are not discrete calendar units (i.e. day, week, etc), for example "the next two winters".  Additionally, TimeML does 
not allow events to be the anchor for temporal expressions, for example, "three weeks after diagnosis", which can limit 
its use for applications that require ordering events on a timeline.  Finally, Bethard and Parker argue that just 
annotating an entire phrase looses a lot of semantic information that can be used to reconstruct a timeline of 
events[<sup>13</sup>](#references).

The SemEval 2018 Task 6 revolves around parsing out fine-grained temporal information and relationships into a 
"Semantically Compositional Annotation Scheme" developed by Bethard and Parker[<sup>13</sup>](#references).  This 
scheme is able to represent a wider variety of temporal phrases, allows for events to act as anchors, and uses 
mathematical operations over a timeline to define the semantics of each annotation. For example, the phrase "three 
weeks after diagnosis" would annotate "diagnosis" as the anchor event, and then define a "period" containing "weeks" 
with the number 3.  The intent of the this annotation scheme is to capture periods of time that are not well covered by 
currently existing schemes. Ultimately, the annotations generated in this format can be used by other applications to 
automatically generate useful information, such as a patient's medical timeline from doctor's notes. The available 
corpora for Task 6 is the TimeBank/AQUAINT corpus of annotated newswire text, and the THYME colon cancer clinical notes 
corpus; however, as the THYME corpus is currently unavailable we utilized the TimeBank/AQUAINT corpus for all evaluations.  
To address this challenge we developed Chrono, a hybrid rule-based and machine learning Python package that normalizes temporal expressions from the 
TimeBank/AQUAINT corpus into the Semantically Compositional Annotation Scheme of Bethard and Parker.

### 2.  Method
Our approach is to utilize an already proven temporal annotator to identify the majority of temporal phrases in the text, 
then build from there to incorporate more complex temporal relations.  We chose SUTime for initial phrase tagging, and 
while written in java, has a python wrapper written by Frank Blechschmidt[<sup>14</sup>](#references).  
SUTime[<sup>15</sup>](#references) is a rule-based temporal annotator that was the top scoring for recall and F1 in the 
TempEval3 challenge utilizing the TimeBank/AQUAINT corpus. SUTime outputs its parsed temporal phrases and their normalized 
values as a json string.  These json strings are then parsed into Bethard's scheme and output into the required 
Anafora XML format for evaluation (see Bethard and Parker[<sup>13</sup>](#references) for a detailed description of the annotation scheme).  Parsing the SUTime phrases is primarily done using a rule-based approach; however, for select ambiguous phrases machine learning is utilized in order to consider contextual information in classifying the ambiguous temporal entity.  This approach and the program structure are described in more detail below.

#### Chrono Program Structure
Chrono has 5 main components: "run_T6.py" is the driver script that imports the data files and controls the the main 
program flow; "sutimeEntity.py" is the class file that defines a SUTime entity object; "t6entity.py" is the class file 
that defines all possible annotation types described by Bethard and Parker; "SUTime_To_T6.py" is the primary method 
and list of functions that parse a SUTime entity object to the appropriate set of T6 entities; and the fifth component comprises the three machine learning methods--NB_nltk_classifier.py, DecisionTree.py, and ChronoKeras.py--which will be discussed in the next section.

__run_T6.py:__ This is the main method for the Chrono program.  It handles all input arguments, identifies the list of files to be annotated, trains the requested machine learning classifier, and loops through each file to 1) identify temporal expressions using SUTime, 2) import the SUTime expressions into a list of SUTime entities, 3) convert the SUTime entities to T6 entities, and 4) writes the T6 entities to an XML file.

__sutimeEntities.py:__ This file defines the "sutimeEntity" object. SUTime parses raw text files and returns the following as a JSON string: the parsed temporal phrase, the beginning and end spans of the parsed phrase, the type of temporal entity (DATE, TIME, DURATION, SET), and finally the normalized temporal value. The sutimeEntities.py file contains a method to import SUTime's JSON string into the sutimeEntity object.  The SUTime entities are then stored in a Python List structure in the run_T6.py main method.

__t6entity.py:__ This file defines the t6entity class that stores all of the information for each annotation type. For example, the phrase "May 20, 2017" would be represented as the following three t6entities: Year, MonthOfYear, and DayOfMonth. Each entity has several properties that must be identified and set correctly, including the type or value, span indicies, and a sub-interval. In the given example "year" would have the value "2017" and would point to its sub-interval MonthOfYear. MonthOfYear would be of the type "May" and have a sub-interval that points to DayOfMonth. DayOfMonth would have the value 20 and would not point to any sub-interval. Each object would also have it's span specified, which is the original coordinates of the phrase in the input text file. There are 32 types of entities with 5 parent types described by Bethard and Parker that we have included in our program. The t6entity class also has several methods to perform operations on each object.  This includes a method to print each entity in the required Anafora XML format and a method to compare 2 entities using their location in the text and entity type.    

__SUTime_To_T6.py:__ This file contains all methods needed to convert a list of SUTime entities to a set of T6 Entities. For example, the raw string "11/02/89" has three T6 Entities: a T6 twoDigitYear, '89'; a T6 MonthOfYear 'November', where November is a sub-interval of the twoDigitYear entity, and a DayOfMonth, '02', which is a sub-interval of the MonthOfYear entity. SUTime does noramlize all of it's parsed phrases into the temporal value; however, this normalization can be flawed depending on the phrase.  For example, a phrase without a year such as "Nov. 6" is automatically given the current year.  This is not correct according to the new annotation scheme.  Therefore, all of our methods parse the identified text of the SUTime entity and not the normalized value. 

Parsing the temporal patterns is done using rule-based logic, regular expressions, and a machine learning classifier for selected termporal types.  Prior to any parsing the temporal phrase is normalized by converting to lowercase and removing all punctuation (except for a few specific cases as mentioned below).  For example, when identifying T6 entities of the type DayOfWeek, the text representations for each day of the week are searched for (e.g. monday, mon, etc). The majority of the parsing methods are rule-based, however, the T6 entity type can be ambiguous for cetain entity type, like Period and Calendar-Interval.  Disambiguation is done using contextual information input into a machine learning classifier, which is dicussed in more detail in the next section. There are several base methods that look for typical temporal expressions like 11/02/89.  There are also several methods which look for atypical temporal expressions like a specific day of the week ('Tuesday' for example).  As each T6 Entity is found it is appended to a master T6 list, also a specific T6 id is assigned to each identified entity.  Finally, once all of the SUTime objects have been parsed into their respective T6 entities, the master list is passed back to the main function for further processing.

The following is a list of T6Entity types that are parsed using a rule-based system:

* *Day of Week:* Days of the week were identified by looking for specific sub-strings such as "monday" or "mon". All punctuation 
was removed prior to parsing out these strings. Single letter abbreviations, such as M for Monday, are not identified.
* *Text Month and Day:* A "Text Month and Day" refers to a non-numeric month reference, such as "Nov. 6". Each temporal phrase string was normalized to all lowercase, and only commas were removed.  Phrase text was then searched for each month, such as "november" or "nov.". Periods were kept because they needed to be included in the reported span. Once a month was identified it was assumed any associated day would be mentioned downstream of the month mention; thus, an interger or number word was searched for in downstream text from the identified month. One disadvantage of this set of rules is that phrases such as " the sixth of November" are currently missed.
* *AM or PM:* Due to possible ambiguity of "AM" when converted to lowercase, and the potential inclusion of punctuation into the temporal phrase (e.g. a.m.) that needed to be accounted for when calculating the span, no text normalization was done when searching for AMPM annotations.  Phrases were instead directly search for inclusion of one of the following forms: "AM","am","A.M.","AM.","a.m.","am.","PM","pm","P.M.","p.m.","pm.","PM."
* *Part of Day:* Temporal phrases were normalized by converting to lowercase and removing all punctuation.  Then the following terms were searched for in the temporal phrase: "morning","evening","afternoon","night","dawn","dusk","tonight","overnight","today","nights","mornings","evening","afternoons", "noon".
* *Part of Week:* Temporal phrases were normalized by converting to lowercase and removing all punctuation.  Then the following terms were searched for in the temporal phrase: "weekend", "weekends".
* *Time Zone:* Time zones were identified using a regular expression to search for one of the following abbreviations representing a time zone: AST, EST, EDT, CST, MST, PST, AKST, HST, UTC-11, UTC+10.  When searching for time zones, the text was not normalized in order to retain the capitilazation.
* *Season of Year:* Temporal phrases were normalized by converting to lowercase and removing all punctuation.  Then the following terms were searched for in the temporal phrase: "summer", "winter", "spring", "fall".
* *TwoDigitYear:* Two digit years were identified looking for specific patterns (regular expressions) in the form date strings such as mm/dd/yy, if a string contained a two-digit year, it would see if there were any number of other temporal entites that could be a subinterval associated with this year. 
* *Year:* Four digit years were identified by looking for specific patterns (regular expressions), specifically mm/dd/yyyy, similar to the TwoDigitYear method mentioned above, if a four digit year was found it would see if there were any number of other temporal entites that could be a subinterval associated with this year. Additionally, lone 4-digit years were identified by evaluating any 4-digit string.  If it was a number between 1800 and 2050 it was classified as a 4-digit year. 
* *Month of Year:*  2 digit months were identified by looking for three specific formats: yyyy/mm/dd, yy/mm/dd, mm/dd/yy.  If one of these conditions were met it would convert the two-digit month into it's proper nomenclature (11 = November)
* *Day of Month:* 2 digit days were identified looking for a specific format: mm/dd/yy. If a pattern was identified, it would create a day of the month entity and look for any other sub-intervals.
* *Hour of Day:*  2 digit hours were identified looking for a specific format: HH:MM:SS.  If a pattern was identified, it would create a day of the month entity and look for any other sub-intervals.
* *Minute of Hour:* 2 digit minutes were identified looking for a specific format: HH:MM:SS.  If a pattern was identified, it would create a hour of day entity and look for any other sub-intervals.
* *Second of Minute:* 2 digit seconds were identified looking for a specific format: HH:MM:SS.  If a pattern was identified, it would create a second of minute entity.
* *24-Hour Time:* Time expressions for 24-hour formatted times (e.g. 1334 refers to 1:34pm) were parsed by identifying all 4-digit numbers.  If the hour and minute digits were within the correct range it was parsed as a HourOfDay and MinuteOfHour set of entities.
* *Periods and Calendar-Intervals:* Terms that are classified as either Calendar-Intervals or Periods are identified using a rule-based system followed by a machine learning approach to fully disambiguate the correct class.  The following terms are identified as a "period" or "calendar -interval" and then sent to the machine learning classifier: "decades", "decade", "yesterday", "day", "week", "month", "year", "daily", "weekly", "monthly", "yearly", "century", "minute", "second", "hour", "hourly", "days", "weeks", "months", "years", "centuries", "minutes", "seconds", "hours". See the section below for more details.

#### Machine Learning Classification
Machine learning was utilized to differentiate between the "calendar-interval" and "period" entities using contextual information.  A "calendar-interval" refers to a discrete interval on a calendar, for example a week that spans Sunday to Saturday, or a year that spans Jan 1st to Dec 30th. A "period" is a unit of time that is expressed frequently in calendar terms.  For example, "I will call you a week from today." indicates the person will call 7 days from the present, whereas "I will call you next week." indicates the person will call at any time in the next Sunday-Saturday calendar interval.  In both of these examples the term "week" is what needs to be classified.  There are too many variations in how these temporal terms can be used to be able to develop a comprehensive rule-based system; thus, machine learning is used to classify these instances. After identifying the entity type it is assumed that any number specification will appear before the entity, so a number (numeric or text) is then searched for in the upstream text.

##### Feature Vectors
All machine learning implementations utilized binary feature vectors that contained the following features:

* *temporal_self:* If the target word itself was temporal this feature was set to "1".
* *temporal_context:* If there was at least one temporal word within a 3-word window up- or down-stream of the target word this feature was set to "1".
* *numeric:* If there was a numeric expression either directly before or after (a 1-word window) the target word this feature was set to "1".
* *context:* All words within a 3-word window are identified as features and set to "1" if that word is present. Prior to identifying these features, all words were lowercased with punctuation removed. The 3-word window includes crossing sentence boundaries before and/or after the target word.

##### Training Data
Prior to training the machine learning classifiers a training data set had to be compiled.  A python script (createMLTrainingMatrix.py) was written to identify all gold standard annotated periods or calendar-intervals from the 78 gold standard anafora XML files provided by the task moderator. The text phrase, start and end spans, and entity type were identified and written to a tab-delimited text file for import by the machine learning algorithms for training.

##### Machine Learning Algorithms
Three different machine learning models were implemented to classify periods versus calendar-intervals using the features described above for training. 

* *Naive Bayes (NB):* The naive bayes algorithm is implemented using NLTK and all default values. It reads in the generated training data and creates a naive bayes model that is passed to the parsing functions.  

* *Neural Network (NN):* The neural network algorithm was written using Keras. It trains a "Deep Neural Network" - three hidden layers all fully connected - on the training data and stores the model<sup>16</sup> that is passed to the parsing functions.  

* *Decision Tree (DT):* The decision tree algorithm was implemented in a similar fashion to NB by utilizing NLTK and all default parameters. It reads in the generated training data and creates a binary decision tree that is passed to the parsing functions taking into account the weights of various inputs.  

The user identifies which of these methods they would like implemented from the command line.  Then the chosen algorithm is trained and the resulting classifier with all feature labels is passed to the T6_to_SUTime.py methods for use by the parsers.  Once a possible "period" or "calendar-interval" is identified, the features are extracted for that observation and run through the classifier to determine which entity type should be added.   


### 3.  Evaluation, Baseline, and Results

#### Evaluation
The AnaforaTools Pythons package was used to calculate the Precision, Recall, and F1 measures using selected XML entities, types, properties, and spans output by our program compared to the provided gold standard.  The gold standard was provided by Bethard and Parker, and was manually annotated using the AnaforaTools annotator with an inter-annotator agreement of F1 = 0.917. The entity types not included in the current evaluation are "After", "Before", "Union", "Event", "Between", "Frequency", "Modifier", and "This". These entity types are currently not being parsed from the SUTime temporal phrases, so were not included in the evaluation.     

#### Baseline
The goal of this SemEval task is to obtain a fine-grained parsing of temporal information from text using the Semantically Compositional Annotation Scheme by Bethard and Parker.  There currently is no published system for parsing temporal information into this scheme for use as a baseline.  Therefore, we decided to naively parse the TIMEX3 temporal phrases identified by HeidelTime into our T6entity structure for comparison. HeidelTime was developed at Heidelberg University and was used as a baseline for SUTime in the task of identifying temporal phrases.  

HeidelTime phrases were converted to T6 entities and evaluated against the gold standard using the AnaforaTools package. Each input file was run with HeidelTime's standalone system and the results were parsed into a HeidelTime list.  Once the HeidelTime List was generated, using similar methods from SUTime_To_T6.py, T6 Entites were generated only for the Year, Month, Day, Hour, Second, and Minute.  This naive parsing omits many relationships such as event-time relations.  HeidelTime was not built for parsing data into such a fine-grainined structure, so it may not be the best choice for base line moving forward.

#### Results

Our rule-based parsing of SUTime temporal phrases achieves higher precision and recall than the baseline (Table 1). The T6 application performs better when only text spans are considered (exact coordinates of temporal entities in the original text). This indicates that T6 is identifying a lot of the correct entities and locations, but is missing some of the properties, or assigning incorrect properties.  Upon further investigation we found that T6 was missing many of the correct sub-intervals when parsing dates and times. Other issues that will need fine tuning include the over-predicting of "Calendar-Interval", "Minute-Of-Hour", "Second-Of-Day", and "Part-Of-Day" entity types.    

| Implementation                   | Precision | Recall |   F1  |
| -------------------------------- | --------- | ------ | ----- |
| T6 - 100% Entity Correct         |  0.269    | 0.253  | 0.260 |
| GUTime - 100% Entity Correct     |  0.088    | 0.020  | 0.033 |
| HeidelTime - 100% Entity Correct |  0.003    | 0.002  | 0.002 |
| -------------------------------- | --------- | ------ | ----- |
| T6 - Corrent Spans               |  0.606    | 0.522  | 0.561 |   
| GUTime - Correct Spans           |  0.735    | 0.136  | 0.230 |
| HeidelTime - Correct Spans       |  0.013    | 0.007  | 0.009 |

Table 1 - T6 and baseline results.

### Add in an Error Analysis here
### 4. Future Work (Updated)
Through the course of implementing the T6 parser, we identified that SUTime does not capture all of the temporal information required to correctly parse it into the "Semantically Compositional Annotation Scheme".  Further identification using machine learning methods could improve some of the less common entities.

Other improvements to our rule-based parsing system would be to capture more sub-intervals from uncommon formats of dates and times. We also aim to adjust the SUTime model implementation to improve the quality of the underlying parser in identifying temporal phrases.  Once we implement these improvements, we will be able to compare our new results to our current results to ensure the modifications are improving the overall result.

### 5.  Conclusion
This annotation scheme has the potential to be very useful by providing high quality temporal data to downstream 
applications.  Improvements in correctly identifying free-text, ambiguous temporal expressions will continue to be a 
challenge.  We believe that advances in machine learning will improve correct identification of temporal expressions 
based on the context in which they are found.  Even the tense of a verb carries temporal information which may or may 
not be relevant thus complicating the task of tagging free-text temporal expressions. 



---
#### References

1. Kuzey, E., Setty, V, Strötgen, J, and Weikum, G. (2016) [As Time Goes By: Comprehensive Tagging of Textual Phrases with Temporal Scopes](https://dl.acm.org/citation.cfm?id=2883055). Proceedings of the 25th International Conference on World Wide Web (WWW '16), Montreal, Canada, 4 2016.

2. Bertram C. Bruce, [A model for temporal references and its application in a question answering program](http://www.sciencedirect.com/science/article/pii/0004370272900409), In Artificial Intelligence, Volume 3, 1972, Pages 1-25, ISSN 0004-3702, https://doi.org/10.1016/0004-3702(72)90040-9.

3. [SemEval-2007 Task List](http://nlp.cs.swarthmore.edu/semeval/tasks/index.php)

4. [TimeBank and AQUAINT Corpora](http://www.timeml.org/timebank/timebank.html)

5. UzZaman, N., Llorens, H., Derczynski, L., Verhagen, M., Allen, J., and Pustejovsky, J., (2013) [SemEval-2013 Task 1: TempEval-3: Evaluating Time Expressions, Events, and Temporal Relations](http://www.aclweb.org/anthology/S/S13/S13-2001.pdf), Second Joint Conference on Lexical and Computational Semantics (*SEM), Volume 2: Seventh International Workshop on Semantic Evaluation (SemEval 2013), pages 1–9, Atlanta, Georgia, June 14-15, 2013

6. Llorens, H., Chambers, N., UzZaman, N., Mostafazadeh, N., Allen, J., and Pustejovsky, J., (2015) [QA TempEval: Evaluating Temporal Information Understanding with QA](http://alt.qcri.org/semeval2015/task5/data/uploads/qatempeval-taskdescription.pdf)

7. [SemEval-2015 Task 6: Clinical TempEval](http://alt.qcri.org/semeval2015/task6/)

8. TimeML Working Group (2009)[Guidelines for Temporal Expression Annotation for English for TempEval 2010](http://www.timeml.org/tempeval2/tempeval2-trial/guidelines/timex3guidelines-072009.pdf)

9. Pustejovsky, J., Castaño, J., Ingria, R., Sauri, R., Gaizauskas, R., Setzer, A., and Katz, G. (2003) [TimeML: Robust Specification of Event and Temporal Expressions in Text](http://www.timeml.org/publications/timeMLpubs/IWCS-v4.pdf), IWCS-5, Fifth International Workshop on Computational Semantics.

10. [TimeX Portal](http://timexportal.wikidot.com/timexmuc6)

11. [Message Understanding Conference - 6](http://www.cs.nyu.edu/cs/faculty/grishman/muc6.html) 1995

12. [Wikipedia: SemEval Areas of Evaluation](https://en.wikipedia.org/wiki/SemEval#Areas_of_evaluation)

13. Bethard, S. and Parker, J. (2016) [A Semantically Compositional Annotation Scheme for Time Normalization](http://www.lrec-conf.org/proceedings/lrec2016/pdf/288_Paper.pdf). Proceedings of the Tenth International Conference on Language Resources and Evaluation (LREC 2016), Paris, France, 5 2016

14. [Python-SUTime](https://github.com/FraBle/python-sutime)

15. Chang, A., and Manning, C. (2012) [SUTime: A Library for Recognizing and Normalizing Time Expressions](http://nlp.stanford.edu/pubs/lrec2012-sutime.pdf), 8th International Conference on Language Resources and Evaluation (LREC 2012)

16. Keras: The Python Deep Learning library https://keras.io/
