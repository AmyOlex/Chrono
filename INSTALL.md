# SemEval-2018 Task 6 - Parsing Time Normalizations

## Installation

### Pre-Reqs
- Java 8 or later
- Python 3
- Git
- jpype, installation instructions from <http://jpype.readthedocs.io/en/latest/install.html>


### Streamlined Steps:

Checked for Java version:
``` bash
>> java -version
```
Had 1.8.0, so ok on that.

Checked python version:
``` bash
>> python
```
Have 2.7.12, so may need to upgrade.  Trying with python 2.7.

Installed pip:
``` bash
>> sudo apt-get install python-pip
```

Installing jpype:
Had to first install python-dev:
``` bash
>> sudo apt-get install python-dev
```

Then needed to download from github:
``` bash
>> git clone https://github.com/originell/jpype.git
```

The run the install script:
``` bash
>> sudo python setup.py install
```

Now install sutime:
``` bash
>>pip install sutime
```

Ok, now install our task6 by unzipping the zip file.

Also need nltk:
``` bash
>> pip install nltk
```

Also needed python-dateutil:
``` bash
>> pip install python-dateutil
```

Had to install word2number:
``` bash
>> pip install word2number
```

Get python-sutime from Git, cd into the directory, then run maven:
``` bash
>> git clone https://github.com/FraBle/python-sutime.git
>> cd python-sutime
>> mvn dependency:copy-dependencies -DoutputDirectory=./jars
```
Then copy the sutime and jars folder into our task6 directory.

If you get a java.lang.RuntimeException: Class edu.stanford.nlp.python.SUTimeWrapper not found error, then jpype is
pointing to the wrong Java JDK library.  Delete all except 1.8 and it should run.
