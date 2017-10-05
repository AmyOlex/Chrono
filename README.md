# SemEval-2018 Task 6 - Parsing Time Normalizations

### Amy Olex, Nicholas Morton, Luke Maffey
### CMSC516 - Advanced Natural Language Processing Fall 2017
---
### Installation
Make sure you have python and Java installed.

Download our tool:
```bash
>> git clone https://github.com/AmyOlex/CMSC516-SemEval2018-Task6.git
```

Install SUTime (used for some back end tagging):
```bash
>> sudo apt-get install -y python3-pip
>> sudo apt-get install python3-jpype 
>> sudo apt-get instll python3-dev
>> pip install sutime
  ```
Install jar files required for SUTime (uses [maven](https://www.vultr.com/docs/how-to-install-apache-maven-on-ubuntu-16-04)):
```bash
>> mvn dependency:copy-dependencies -DoutputDirectory=./jars
```

Download the Stanford parser:
<http://projects.csail.mit.edu/spatial/Stanford_Parser>

Download anafora tools (used for some text processing and evaluation of results):
```bash
>> git clone https://github.com/bethard/anaforatools.git
```

Download trial data:
<https://github.com/bethard/anafora-annotations/releases/tag/semeval2018-trial>


### Usage
To use type:

```bash
>> python run_task6.py -i {INPUT DIR} -o {OUTPUT DIR} -r {REFERENCE DIR} -j {JAR DIR}(default is ./jars) -a {ANAFORA DIR}(default is ./anaforatools)
```

---

### 1.  Introduction
Our task was to take text from the AQUINT and TimeBank corpora input and output an xml file for each input file with temporal expressions identified and normalized according to the framework laid out in "A Semantically Compositional Annotation Scheme for Time Normalization"[<sup>1</sup>](#references).  We developed a package using python which uses the SUTime[<sup>2</sup>](#references) tagger to identify and mark temporal expressions in documents for processing.


### 2.  Background
The intent of the this annotation scheme is to capture periods of time that are not well covered by currently existing schemes.  The most common scheme is the TIMEX3[<sup>3</sup>](#references) system used by TimeML[<sup>4</sup>](#references) developed out of the older TIMEX scheme which was created by DARPA in 1995[<sup>5,6</sup>](#references).  Ultimately, the annotations generated in this format can be used by other applications to automatically generate useful information, such as a patient's medical timeline from doctor's notes. 


### 3.  Method
We primarily used SUTime to tag relevant temporal data and then wrote our own methods in python to break those tagged phrases out into entities which were linked together as described by Bethard.  Kuzey et al identified four types of expressions that need to be parsed[<sup>7</sup>](#references):
> 1. _Explicit temporal expressions_ denote a precise time point or period...
> 2. _Relative temporal expressions_ refer to dates that can be interpreted with respect to a reference date...
> 3. _Implicit temporal expressions_ refer to special kinds of named events...
> 4. _Free-text temporal expressions_ refer to arbitrary kinds of named events or facts with temporal scopes that are merely given by a text phrase but have unique interpretations given the context and background knowledge...

Each type of temporal expression presents unique challenges in handling.

### 4.  Analysis


### 5.  Conclusion
This annotation scheme has the potential to be very useful by providing high quality temporal data to downstream applications.  Improvements in correctly identifying free-text, ambiguous temporal expressions will continue to be a challenge.  We believe that advances in machine learning will improve correct identification of temporal expressions based on the context in which they are found.  Even the tense of a verb carries temporal information which may or may not be relevant thus complicating the task of tagging free-text temporal expressions. 

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