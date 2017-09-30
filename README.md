# CMSC516 - Advanced Natural Language Processing Fall 2017

### SemEval-2018 Task 6 - Parsing Time Normalizations
### Authors - Amy Olex, Nicholas Morton, Luke Maffey
---
### Usage
To use type:

`python run_task6.py -i {INPUT DIR} -o {OUTPUT DIR} -r {REFERENCE DIR} -j {JAR DIR} -a {ANAFORA DIR}`

---

### 1.  Introduction
Our task was to take text from the AQUINT and TimeBank corpora input and output an xml file for each input file with temporal expressions identified and normalized according to the framework laid out in "A Semantically Compositional Annotation Scheme for Time Normalization"[<sup>1</sup>](#References).  We developed a package using python which uses the SUTime[<sup>2</sup>](#References) tagger to identify and mark temporal expressions in documents for processing.


### 2.  Background
The intent of the this annotation scheme is to capture periods of time that are not well covered by currently existing schemes.  The most common scheme is the TIMEX3[<sup>3</sup>](#References) system used by TimeML[<sup>4</sup>](#References) developed out of the older TIMEX scheme which was created by DARPA in 1995[<sup>5,6</sup>](#References).  Ultimately, the annotations generated in this format can be used by other applications to automatically generate useful information such as a patient's medical timeline from doctor's notes which may not be in chronological order as written.


### 3.  Method
We primarily used SUTime to tag relevant temporal data and then wrote our own methods in python to break those tagged phrases out into entities which were linked together as described by Bethard.  


### 4.  Analysis


### 5.  Conclusion



---
#### References

1. Bethard, S. and Parker, J. (2016) [A Semantically Compositional Annotation Scheme for Time Normalization](http://www.lrec-conf.org/proceedings/lrec2016/pdf/288_Paper.pdf). Proceedings of the Tenth International Conference on Language Resources and Evaluation (LREC 2016), Paris, France, 5 2016

2. <https://nlp.stanford.edu/software/sutime.html>

3. <http://www.timeml.org/tempeval2/tempeval2-trial/guidelines/timex3guidelines-072009.pdf>

4. <http://www.timeml.org/>

5. <http://timexportal.wikidot.com/timexmuc6>

6. <http://www.cs.nyu.edu/cs/faculty/grishman/muc6.html>