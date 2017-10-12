# SemEval-2018 Task 6 - Parsing Time Normalizations

## Installation

### Pre-Reqs
- Java 8 or later
- Python 3 or later (comes with Anaconda 3 which can be obtained from here <https://www.anaconda.com/download>)
- Git, installation instructions from <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>
- Jpype, installation instructions from <http://jpype.readthedocs.io/en/latest/install.html>
- Maven, installation instructions for Ubuntu from <https://www.mkyong.com/maven/how-to-install-maven-in-ubuntu/>, or for MacOSX from <https://www.mkyong.com/maven/install-maven-on-mac-osx/>
- Pip, installation instructions from <https://www.saltycrane.com/blog/2010/02/how-install-pip-ubuntu/>, or see below.

### Streamlined Steps:

#### 1. Check versions
Java version:
``` bash
>> java -version
```

Python version:
``` bash
>> python
```

#### 3. Download and unzip project.

#### 4. Install pip:
``` bash
>> sudo apt-get install python-pip
```

#### 6. Install additional python modules
Install nltk:
``` bash
>> pip install nltk
```

Install python-dateutil:
``` bash
>> pip install python-dateutil
```

Install word2number:
``` bash
>> pip install word2number
```

Install sutime:
``` bash
>>pip install sutime
```

#### 7. Install SUTime Dependencies
Get python-sutime from Git, cd into the directory, then run maven:
``` bash
>> git clone https://github.com/FraBle/python-sutime.git
>> cd python-sutime
>> mvn dependency:copy-dependencies -DoutputDirectory=./jars
```

While in the "python-sutime" folder:
* Move the "./jars" folder to the top level of "CMSC516-SemEval2018-Task6-master/".
* Move the "./sutime" folder to "CMSC516-SemEval2018-Task6-master/task6/".

#### 8. Debugging

* If you get a java.lang.RuntimeException: Class edu.stanford.nlp.python.SUTimeWrapper not found error, then jpype is
pointing to the wrong Java JDK library.  Delete all except 1.8 and it should run.
* If you get a Reflections error then you need to try and re-install SUTime as there are some dependencies not linked correctly.

