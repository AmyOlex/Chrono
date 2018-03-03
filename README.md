<!---
output:
  html_document: default
  pdf_document: default
--->

# Chrono - Parsing Time Normalizations inti the SCATE Schema

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

Installation has been tested on Mac OSX and Linux platforms.

 - Ensure you have all Pre-Reqs installed, including all required Python modules.
 - Download or clone this git repo to your computer.  If using Git and SSH you can type ">> git clone git@github.com:AmyOlex/Chrono.git" into your terminal.


### Usage

Navigate to the Chrono folder.  For a description of all available options use:

```bash
>> python Chrono -h
```

Prior to running Chrono you must have:

1) The input text files organized into the Anafora XML Directory Structure.
2) A machine learning (ML) training matrix and class information.

The ML matrix files utilized by Chrono in the SemEval 2018 Task 6 challenge are included in the "sample_files" directory provided with this system.  You may use these, or create your own using the "Create ML Matrix" instructions below. 

#### Running Chrono

To run Chrono without evaluation against a gold standard all you need in the input file directory and the two ML training matrix files.  We will assume the use of the provided matrix files in the "sample_files" directory, otherwise change the paths accordingly.  We also assume the input data files are in a local folder named "./data/my_input/", the out put is being saved in "./results/my_output/", and all input files have a ".txt" extension.  The ML training matrix files are named "official_train_MLmatrix_Win5_012618_data.csv" and "official_train_MLmatrix_Win5_012618_class.csv".  

```
>> python Chrono.py -i ./data/my_input -x ".txt" -o ./results/my_output -m SVM -d "./sample_files/official_train_MLmatrix_Win5_012618_data.csv" -c "./sample_files/official_train_MLmatrix_Win5_012618_class.csv"
```

#### Evaluating Chrono with Anafora Tools

To evaluate Chrono performance you must have:

1) The gold standard Anafora Annotations for your input files organized in the Anafora XML Directory Structure with the gold standard XML file being named the same as the input file with an extension formatted as ".\*.completed.\*.xml".  These gold standard files may be located in the same directory as the associated input file (as long as there is only one xml file present), which means your gold standard directory is also your input directory.

2) You must have Anafora Tools installed <https://github.com/bethard/anaforatools>.

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
The Ml methods require 2 files, a data matrix and a class file, in order to be trained.  While we provide a file that searches the context with a window size of 3, you can also create your own training file with different window sizes.  To create your own training file do the following:

> 1) ensure all the gold standard data you want parsed into the training format is in one folder.
> 2) Run the python run_chrono.py script as follows: 
```bash
>> python run_chrono.py -i ./data/SemEval-Task6-Train/ -r ./data/SemEval-Task6-TrainGold/ -o ./resultsTrain/ -m NB -t "my_train_matrix" -w 3 -m NB
```
The *-m* option allows you to choose the Ml algorithm you want to use. The *-t* option should be the file name base you want your training data matrix files to be saved to, and the *-w* option is the context window size, which is 3 by default.
> 3) After your data files have been generated you can run the command again, but this time point to the new data and class files for the ML algorihtm training.
```bash
>> python run_chrono.py -i ./data/SemEval-Task6-Test/ -r ./data/SemEval-Task6-TestGold/ -o ./resultsTest/ -m $ML -d "./data/aquaint_train_data_TrainWin3.csv" -c "./data/aquaint_train_class_TrainWin3.csv"
```
The *-d* option provides the path and file name of the file that the gold standard matrix should be saved.  Finally, *-c* option indicates the file name with the class information in it.


### Anafora XML Directory Structure
In the Anafora XML Directory Structure each input file is in a folder by itself with the folder named the same as the file without an extension.  There is also an additional text file that contains the document time that is named that same as the input file, but has the extension ".dct".  



---
### References

1. Bethard, S. and Parker, J. (2016) [A Semantically Compositional Annotation Scheme for Time Normalization](http://www.lrec-conf.org/proceedings/lrec2016/pdf/288_Paper.pdf). Proceedings of the Tenth International Conference on Language Resources and Evaluation (LREC 2016), Paris, France, 5 2016
