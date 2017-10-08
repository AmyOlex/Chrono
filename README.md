# SemEval-2018 Task 6 - Parsing Time Normalizations

### Amy Olex, Nicholas Morton, Luke Maffey

### CMSC516 - Advanced Natural Language Processing Fall 2017

---

### Usage
To use type:

```bash
>> source runit.sh
```

### Roles and Contributions
 - *Amy Olex:* Team lead, workflow development lead, framework implementation, run_task6.py author, sutimeEntity.py 
 author, SUTime_To-T6.py method contributer, utils.py author, referenceToken.py author, presentation preperation, 
 README co-author, installation co-author and tester, literature review.
 - *Luke Maffey:* Doxygen code documentation lead, t6Entities.py author, stopword identification/editing and method 
 implementation, presentation preparation, README co-author, installation co-author and tester, literature review, GUTime testing.
 - *Nicholas Morton:* SUTime installation and implementation lead, workflow development, SUTime_To-T6.py author, 
 README co-author, installation co-author and tester, literature review, HeidelTime testing. 

---

### 1.  Introduction
Understanding and processing temporal information is vital for navigating life.  Humans are continually processing temporal information in their daily lives, including in written text. It is not possible to have a cohesive conversation, or write a coherent document without the use of temporal information.  For example, "I had a drink" versus "I have a drink" differ by only one word, but infer two different timelines of events.  The first phrase implies you have already ingested a drink prior to the statement, whereas the second implies you currently posses a drink, but it is not known whether or not you have ingested some of it already. The human mind processes this subtle temporal information instantly and effortlessly; however, it is difficult for computers to identify, process, and utilize this information in an automated fashion because it requires knowledge and understanding of syntax, semantics, and context to link to time information to the correct events to order them on a timeline. For instance, Kuzey et al identified four types of temporal expressions, each of which presents a unique challenge for computers[<sup>7</sup>](#references):
> 1. _Explicit temporal expressions_ denote a precise time point or period...
> 2. _Relative temporal expressions_ refer to dates that can be interpreted with respect to a reference date...
> 3. _Implicit temporal expressions_ refer to special kinds of named events...
> 4. _Free-text temporal expressions_ refer to arbitrary kinds of named events or facts with temporal scopes that are 
merely given by a text phrase but have unique interpretations given the context and background knowledge...

Over the past few decades, the automated identification and extraction of temporal information from text has been an active field of study [<sup>8</sup>](#references).  Applications range from information extraction, automated question answering, and in the clinical field the identification of a patient's medical timeline from clinical texts. Since 2007, the SemEval tasks have included a temporal challege task [<sup>?</sup>](#references). In 2013, the TempEval3 challenge utilized the TimeBank/AQUAINT[<sup>?</sup>](#references) newswire corpus and focused on three tasks: A) time expression extraction and evaluation,  B) event identification, and c) identifying realtionships between the time expressions and their associated events [<sup>?</sup>](#references).  Since then the challenges have incorporated extrinsic evaluations by utilizing temporal annotations in a QA application [<sup>?</sup>](#references), and have moved from the news article domain to the clinical domain [<sup>?</sup>](#references). 

The TIMEX3[<sup>3</sup>](#references) scheme is used by TimeML[<sup>4</sup>](#references) and was developed out of the older TIMEX scheme created by DARPA in 1995[<sup>5,6</sup>](#references). TimeML annotates temporal information as a phrase and a normalized value that the phrase represents. For example, the phrase "The accident was on July 8, 2017 at 5pm" would map to the temporal phrase "July 8, 2017 at 5am" and the value "2017-07-08T05:00:00". All SemEval challenges thus far, and most temporal annotation tools, have utilized the TimeML/TIMEX3 [<sup>?</sup>](#references) standard for annotating temporal information.  While TIMEX3 can capture a lot of information, it has trouble representing times that are not discrete calendar units (i.e. day, week, etc), for example "the next two winters".  Additionally, TimeML does not allow events to be the anchor for temporal expressions, for example, "three weeks after diagnosis", which can limit its use for applications that require ordering events on a timeline.  Finally, Bethard and Parker argue that just annotating an entire phrase looses a lot of semantic information that can be used to reconstruct a timeline of events [<sup>?</sup>](#references).

The SemEval 2018 Task 6 revolves around parsing out fine-grained temporal information and relationships into a "Semantically Compositional Annotation Scheme" developed by Bethard and Parker [<sup>?</sup>](#references).  This scheme is able to represent a wider variety of temporal phrases, allows for events to act as anchors, and uses mathematical operations over a timeline to define the semantics of each annotation. For example, the phrase "three weeks after diagnosis" would annotate "diagnosis" as the anchor event, and then define a "period" containing "weeks" with the number 3.  The intent of the this annotation scheme is to capture periods of time that are not well covered by currently existing schemes. Ultimately, the annotations generated in this format can be used by other applications to automatically generate useful information, such as a patient's medical timeline from doctor's notes. The availiable corpora for Task 6 is the TimeBank/AQUAINT corpus of annotated newswire text, and the THYME colon cancer clinical notes corpus; however, as the THYME corpus is currently unavailiable we utilized the TimeBank/AQUAINT corpus for all evaluations.  To address this challenge we developed T6, a rule-based Python package that normalizes temporal expressions from the the TimeBank/AQUAINT corpus into the Semantically Compositional Annotation Scheme of Bethard and Parker.

### 3.  Method
Our approach is to utilize an already proven temporal annotator to identify the majority of temporal phrases in the text, then build from there to incorporate more complex temporal relations.  We chose SUTime for initial phrase tagging, and while written in java, has a python wrapper written by XXXXX [<sup>2</sup>](#references).  SUTime [<sup>2</sup>](#references) is a rule-based temporal annotator that was the top scoring for recall and F1 in the TempEval3 challenge utilizing the TimeBank/AQUAINT corpus. SUTime outputs its parsed temporal phrases and their normalized values as a json string.  These json strings are then parsed into Bethard's scheme and output into the required Anafora XML format for evaluation (see Bethard and Parker[<sup>2</sup>](#references) for a detailed description of the annotation scheme).

#### T6 Program Structure
Our program has 4 main components: "run_T6.py" is the drive script that imports the data files and controls the the main program flow; "sutimeEntity.py" is the class file that defines a SUTime enetity object; "t6entity.py" is the class file that defines all possible annotation types described by Bethard and Parker; and "SUTime_To_T6.py" is the primary method and list of functions that parse a SUTime entity object to the appropriate set of T6 entities.

__run_T6.py:__ This is the main method for the T6 program.  It handles all input arguments, identifies the list of files to be annotated, loops through each file to 1) run SUTime on it, 2) convert the returned json string to SUTime entities, 3) call SUTime_To_T6 to convert the SUTime entities to T6 entities, and 4) writes the T6 entities to an XML file.

__sutimeEntities.py:__ This file defines the "sutimeEntity" object. SUTime parses raw text files and returns the following as a JSON string: the parsed temporal phrase, the beginning and end spans of the parsed phrase, the type of temporal entity (DATE, TIME, DURATION, SET), and finally the normalized temporal value. The sutimeEntities.py file contains a method to import SUTime's JSON string into the sutimeEntity object.  The SUTime entities are then stored in a Python List structure in the run_T6.py main method.

__t6entity.py:__ This file defines the t6entity class that stores all of the information for each annotation type. For example, the phrase "May 20, 2017" would be represented as the following three t6entities: Year, MonthOfYear, and DayOfMonth. Each entity has several properties that must be identified and set correctly, including the type or value, span indicies, and a sub-interval. In the given example "year" would have the value "2017" and would point to its sub-interval MonthOfYear. MonthOfYear would be of the type "May" and have a sub-interval that points to DayOfMonth. DayOfMonth would have the value 20 and would not point to any sub-interval. Each object would also have it's span specified, which is the original coordinates of the phrase in the input text file. There are 29 types of entities with 5 parent types described by Bethard and Parker that we have included in our program. The t6entity class also has several methods to perform operations on each object.  This includes a method to print each entity in the required Anafora XML format and a method to compare 2 entities by their location in the text and type of entity.    

__SUTime_To_T6.py:__ This file contains all methods needed to convert a list of SUTime entities to a set of T6 Entities. For example, the raw string "11/02/89" has three T6 Entities: a T6 twoDigitYear, '89'; a T6 MonthOfYear 'November', where November is a sub-interval of the twoDigitYear entity, and a DayOfMonth, '02', which is a sub-interval of the MonthOfYear entity. SUTime does noramlize all of it's parse phrases; however, this normalization can be flawed depending on the phrase.  For example, a phrase without a year such as "Nov. 6" is automatically given a the current year.  This is not correct according to the new annotation scheme.  Therefore, all of our methods parse the identified text of the SUTime entity and not the normalized value. Parsing out the temporal patterns is done using rule-based logic and regular expressions.  Prior to any parsing the temporal phrase is normalized by converting everything to lowercase and removing all punctuation (except for a few specific cases as mentioned below).  

Here is a list of T6Entity types and our parsing strategy:

* DayOfWeek: Days of the week were identified by looking for specific sub-strings such as "monday" or "mon". All puntuation was removed prior to parsing out these strings.
* Calendar Interval: These are defined as days, weeks, months, or years that align to a calendar interval such a Sunday to Saturday, or the 1st of the month to the 31st. These intervals were identified by searching for the strings "day", "week", "month", and "year", and their plural forms. Some calendar intervals have a number specifying the amount, such as "3 weeks". After identifying the interval it was assumed the number would come before, so a number (numeric or text) was searched for in the upstream text. 
* Text MonthOfYear: A similar strategy as above was implemented for identifying a spelled out month, except only comma were removed.  Thus the text search for would be "november" or "nov.". Periods were kept here because that period need to be included in the reported span. Once a month was identified it was assumed any associated day would be mentioned downstream of the month mention.

For example, hen identifying T6 entities of the type DayOfWeek we simply search for The parsing methods in this file are all rule-based, and parse the SUTime entity's stringThere are several base methods that look for typical temporal expressions like 11/02/89.  There are also several methods which look for atypical temporal expressions like a specific day of the week ('Tuesday' for example) or if the SUTime entity contains a Calendar interval.  As each T6 Entity is found it is appended to a master T6 list, also a specific T6 id is assigned to each found T6 Entity.  Finally, once all of the SUTime objects have been parsed into their respective T6 entities, the master list is passed back to the main function for further processing.

### 4.  Evaluation and Results


### 5.  Conclusion
This annotation scheme has the potential to be very useful by providing high quality temporal data to downstream 
applications.  Improvements in correctly identifying free-text, ambiguous temporal expressions will continue to be a 
challenge.  We believe that advances in machine learning will improve correct identification of temporal expressions 
based on the context in which they are found.  Even the tense of a verb carries temporal information which may or may 
not be relevant thus complicating the task of tagging free-text temporal expressions. 

### 6. Future Work

---
#### References

1. Bethard, S. and Parker, J. (2016) [A Semantically Compositional Annotation Scheme for Time Normalization](http://www.lrec-conf.org/proceedings/lrec2016/pdf/288_Paper.pdf). Proceedings of the Tenth International Conference on Language Resources and Evaluation (LREC 2016), Paris, France, 5 2016

2. <https://nlp.stanford.edu/software/sutime.html>

3. <http://www.timeml.org/tempeval2/tempeval2-trial/guidelines/timex3guidelines-072009.pdf>

4. <http://www.timeml.org/>

5. <http://timexportal.wikidot.com/timexmuc6>

6. <http://www.cs.nyu.edu/cs/faculty/grishman/muc6.html>

7. Kuzey, E., Setty, V, Strötgen, J, and Weikum, G. (2016) [As Time Goes By: Comprehensive Tagging of Textual Phrases with Temporal Scopes](https://dl.acm.org/citation.cfm?id=2883055). Proceedings of the 25th International Conference on World Wide Web (WWW '16), Montreal, Canada, 4 2016.

8. Bertram C. Bruce, A model for temporal references and its application in a question answering program, In Artificial Intelligence, Volume 3, 1972, Pages 1-25, ISSN 0004-3702, https://doi.org/10.1016/0004-3702(72)90040-9.
(http://www.sciencedirect.com/science/article/pii/0004370272900409)

9. 
