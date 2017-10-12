# SemEval-2018 Task 6 - Parsing Time Normalizations

## Installation

### Pre-Reqs
- Java 8 or later
- Python 2.7 or 3
- Git
- jpype, installation instructions from <http://jpype.readthedocs.io/en/latest/install.html>
- Maven, installation instructions for Ubuntu from <https://www.mkyong.com/maven/how-to-install-maven-in-ubuntu/>
- Maven, installation for MacOSX from <https://www.mkyong.com/maven/install-maven-on-mac-osx/>


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

#### 3. Download and unzip project zip file.

#### 4. Install pip:
``` bash
>> sudo apt-get install python-pip
```

#### 5. Install jpype:
Have to first install python-dev:
``` bash
>> sudo apt-get install python-dev
```

Download jpype from github:
``` bash
>> git clone https://github.com/originell/jpype.git
```

The run the install script:
``` bash
>> cd jpype
>> sudo python setup.py install
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

#### 7. Install SUTime
Get python-sutime from Git, cd into the directory, then run maven:
``` bash
>> git clone https://github.com/FraBle/python-sutime.git
>> cd python-sutime
>> mvn dependency:copy-dependencies -DoutputDirectory=./jars
```
Then copy the sutime and jars folder into the top level project directory.

Install sutime via pip as well:
``` bash
>>pip install sutime
```

#### 8. Debugging

* If you get a java.lang.RuntimeException: Class edu.stanford.nlp.python.SUTimeWrapper not found error, then jpype is
pointing to the wrong Java JDK library.  Delete all except 1.8 and it should run.

