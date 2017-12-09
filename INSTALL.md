# SemEval-2018 Task 6 - Parsing Time Normalizations

***New Requirements for Stage 2 are indicated below.***

## Installation

### Pre-Reqs
- Java 8 or later
- Python 3 or later (comes with Anaconda 3 which can be obtained from here <https://www.anaconda.com/download>)
- Git, installation instructions from <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>
- Jpype, installation instructions from <http://jpype.readthedocs.io/en/latest/install.html>
- Maven, installation instructions for Ubuntu from <https://www.mkyong.com/maven/how-to-install-maven-in-ubuntu/>, or for MacOSX from <https://www.mkyong.com/maven/install-maven-on-mac-osx/>
- Pip, installation instructions from <https://www.saltycrane.com/blog/2010/02/how-install-pip-ubuntu/>, or see below.
***New for Stage 2:***
- TensorFlow, installation instructions here: <https://www.tensorflow.org/install/>
- Keras, installation instructions here: <https://keras.io/#installation>

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

#### 2. Download and unzip project.

#### 3. Install pip:
``` bash
>> sudo apt-get install python-pip
```

#### 4. Install additional python modules
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
>> pip install sutime
```

***New for Stage 2:***
Install numpy:
``` bash
>> pip install numpy
```

#### 5. Install SUTime Dependencies
Get python-sutime from Git, cd into the directory, then run maven:
``` bash
>> git clone https://github.com/FraBle/python-sutime.git
>> cd python-sutime
>> mvn dependency:copy-dependencies -DoutputDirectory=./jars
```

While in the "python-sutime" folder:
* Move the "./jars" folder to the top level of "CMSC516-SemEval2018-Task6/".
* Move the "./sutime" folder to "CMSC516-SemEval2018-Task6/Chrono/".

#### 6. Debugging

* If you get a java.lang.RuntimeException: Class edu.stanford.nlp.python.SUTimeWrapper not found error, then jpype is
pointing to the wrong Java JDK library.  Delete all except 1.8 and it should run.
* If you get a Reflections error then you need to try and re-install SUTime as there are some dependencies not linked correctly.
* TensorFlow will give you some warnings but should still work, this is normal

