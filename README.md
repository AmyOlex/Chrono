<!---
output:
  html_document: default
  pdf_document: default
--->

# Chrono - Parsing Time Normalizations into the SCATE Schema

### Amy Olex, Luke Maffey, Nicholas Morton, and Bridget McInnes
---

### Overview

Chrono is a hybrid rule-based and machine learning system that identifies temporal expressions in text and normalizes them into the Semantically Compositional Annotations for Temporal Expressions (SCATE) schema developed by Bethard and Parker [1]. After minor parsing logic adjustments, Chrono has emerged as the top performing system for SemEval 2018 Task 6: Parsing Time Normalizations.

Chrono requires input text files to be in the Anafora XML Directory Structure (described below).  All training was done on the SemEval 2013 AQUAINT/TimeML dataset that can be found at (https://github.com/bethard/anafora-annotations).  

### Requirements

- Python 3 or later (comes with Anaconda 3 which can be obtained from here <https://www.anaconda.com/download>)
- TensorFlow <https://www.tensorflow.org>
- Keras <https://keras.io/#installation>
- AnaforaTools (for evaluation) <https://github.com/bethard/anaforatools>

#### Python Modules Required

 - nltk
 - python-dateutil
 - numpy
 - sklearn

### Installation

Installation has been tested on Mac OSX, Linux, and Windows 10 platforms.

 - Download or clone this git repo to your computer.  If using Git and SSH you can type ">> git clone git@github.com:AmyOlex/Chrono.git" into your terminal.

 - Run
```bash
>> python setup.py install
```

 or

 - Ensure you have all Pre-Reqs installed, including all required Python modules.


### Usage

Navigate to the Chrono folder.  For a description of all available options use:

```bash
>> python Chrono -h
```

Prior to running Chrono you must have:

> 1) The input text files organized into the Anafora XML Directory Structure.

> 2) A machine learning (ML) training matrix and class information.

The ML matrix files utilized by Chrono in the SemEval 2018 Task 6 challenge are included in the "sample_files" directory provided with this system.  You may use these, or create your own using the "Create ML Matrix" instructions below. 

#### Running Chrono

To run Chrono without evaluation against a gold standard all you need in the input file directory and the two ML training matrix files.  We will assume the use of the provided matrix files in the "sample_files" directory, otherwise change the paths accordingly.  We also assume the input data files are in a local folder named "./data/my_input/", the out put is being saved in "./results/my_output/", and all input files have a ".txt" extension.  The ML training matrix files are named "official_train_MLmatrix_Win5_012618_data.csv" and "official_train_MLmatrix_Win5_012618_class.csv".  

```
>> python Chrono.py -i ./data/my_input -x ".txt" -o ./results/my_output -m SVM -d "./sample_files/official_train_MLmatrix_Win5_012618_data.csv" -c "./sample_files/official_train_MLmatrix_Win5_012618_class.csv"
```

#### Evaluating Chrono with Anafora Tools

To evaluate Chrono performance you must have:

> 1) The gold standard Anafora Annotations for your input files organized in the Anafora XML Directory Structure with the gold standard XML file being named the same as the input file with an extension formatted as ".\*.completed.\*.xml".  These gold standard files may be located in the same directory as the associated input file (as long as there is only one xml file present), which means your gold standard directory is also your input directory.

> 2) You must have Anafora Tools installed <https://github.com/bethard/anaforatools>.

The following assumes your gold standard xml files are stored in the same directory as your input files.  If otherwise, adjust the paths as needed.  It also assumes AnaforaTools is installed locally in the directory "./anaforatools".  Change paths as needed if this is not the case.

```bash
>> cd ./anaforatools
>> python -m anafora.evaluate -r ../data/my_input -p ../results/my_output
```

The evaluation can be customized to focus on specific entities. Read the AnaforaTools documentation and/or review the help documentation for details.

```bash
>> python -m anafora.evaluate -h
```

#### Training Data Matrix Generation

The machine learning methods require two files to operate: a data matrix and a class file.  We provide a file that utilizes a window size of 5 in the "sample_files" directory, you can also create your own training file with different window sizes and on different subsets of training data.  To create your own training file do the following:

> 1) Ensure all the gold standard data you want to utilize for training is in a separate directory structure than your testing data.

> 2) Run the python script Chrono_createMLTrainingMatrix.py script as follows (assuming your input text files and the gold standard XML files are in the same directory named "./data/my_input"): 

```bash
>> python Chrono_createMLTrainingMatrix.py -i ./data/my_input/ -g ./data/my_input/ -o MLTrainingMatrix_Win5 -w 5
```

The *-o* option should be the file name base you want your training data matrix files to be saved to, and the *-w* option is the context window size, which is 3 by default.  The output from this script are two ".csv" files that can be used as input into Chrono. 

#### K-Fold Cross-Validation
In order to thouroughly test the perfomance of a machine learning method, modify ChronoKFold.py to use the appropriate -m option and then run:
```bash
>> python ChronoKFold.py > kfoldoutput.txt
```
### Anafora XML Directory Structure
In the Anafora XML Directory Structure each input file is in a folder by itself with the folder named the same as the file without an extension.  There is also an additional text file that contains the document time that is named that same as the input file, but has the extension ".dct".  This DCT file only contains the document date. The Anafora XML Directory Structure can contain the raw input file as well as the Anafora Annotation XML file that is used as a gold standard.  It should NOT contain the result XML files generated by Chrono.  Results should be saved in a separate directory.


---
### References

1. Bethard, S. and Parker, J. (2016) [A Semantically Compositional Annotation Scheme for Time Normalization](http://www.lrec-conf.org/proceedings/lrec2016/pdf/288_Paper.pdf). Proceedings of the Tenth International Conference on Language Resources and Evaluation (LREC 2016), Paris, France, 5 2016
