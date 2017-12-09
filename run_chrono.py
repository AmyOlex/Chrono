## This is the Task6 main method.  The parsing of a full directory will be done from running this program.
#
# Date: 9/23/17
#
# Programmer Name: Amy Olex

###### Workflow ######
##
## 1) get location of files to parse (DONE)
## 2) get location of output directory/create output directories (DONE)
## 3) Initilize the ChronoEntity list
## 4) Initilize the globally unique ID counter
## 5) For each FILE:
##      a) parse with stanford parser to get whitespace tokens and associated spans
##      b) import this into a refToken object list
##      c) parse with SUTime and import into a sutimeEntity list
##      d) Compare SUTime spans with the refToken spans to mark which refToken has temporal information.
##      e) EITHER 1) parse all SUTime entities into T6Entities OR parse all temporally tagged refTokens into T6Entities. << not sure which is better at the moment.
## 6) Print out the ChronoEntity list to an XML file
## 7) Run the evaluation code and print out precision and recall **need to import this code into our package**
##
## To test run:
## python run_chrono.py -i /Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_test -o /Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_eval -r /Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_test -j /Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/CMSC516-SemEval2018-Task6/Chrono/jars/ -a /Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/anaforatools/




import argparse
import os

from chronoML import DecisionTree as DTree
from chronoML import NB_nltk_classifier as NBclass, ChronoKeras
from Chrono import SUTime_To_Chrono
from Chrono import createMLTrainingMatrix
from Chrono import referenceToken
from Chrono import sutimeEntity
from Chrono import sutime_wrapper
from Chrono import utils

debug=False
## This is the driver method to run all of Chrono.
# @param INDIR The location of the directory with all the files in it.
# @param OUTDIR The location of the directory where you want all the output written.
# @param REFDIR The location of the gold standard XML files for evaluation.
# @return Anafora formatted XML files, one directory per file with one XML file in each directory.
# @return The precision and recall from comparing output results to the gold standard.
if __name__ == "__main__":
    
    ## Parse input arguments
    parser = argparse.ArgumentParser(description='Parse a directory of files to identify and normalize temporal information.')
    parser.add_argument('-i', metavar='inputdir', type=str, help='path to the input directory.', required=True)
    parser.add_argument('-o', metavar='outputdir', type=str, help='path to the output directory.', required=True)
    parser.add_argument('-r', metavar='refdir', type=str, help='path to the gold standard directory.', required=True)
    parser.add_argument('-t', metavar='trainML', type=str, help='A string representing the file name that triggers the training data file to be generated using the input data set in the -i option.', required=False, default=False)
    parser.add_argument('-m', metavar='MLmethod', type=str, help='The machine learning method to use. Must be one of NN (neural network), DT (decision tree), NB (naive bayes, default). If option is not provided, or is not NN or DT, the default is NB is used.', required=False, default='NB')
    parser.add_argument('-j', metavar='jardir', type=str, help='path to the directory with all the SUTime required jar files. Default is ./jars', required=False, default="./jars")
    parser.add_argument('-a', metavar='anaforatooldir', type=str, help='path to the top level directory of anaforatools package. Default is ./anaforatools', required=False, default="./anaforatools")
    parser.add_argument('-w', metavar='windowSize', type=str, help='An integer representing the window size for context feature extraction. Default is 3.', required=False, default=3)
    
    args = parser.parse_args()
    ## Now we can access each argument as args.i, args.o, args.r
    
    ## Get list of folder names in the input directory
    indirs = []
    infiles = []
    outfiles = []
    outdirs = []
    goldfiles = []
    for root, dirs, files in os.walk(args.i, topdown = True):
       for name in dirs:
          indirs.append(os.path.join(root, name))
          infiles.append(os.path.join(root, name,name))
          outfiles.append(os.path.join(args.o,name,name))
          outdirs.append(os.path.join(args.o,name))
          goldfiles.append(os.path.join(args.r,name,"period-interval.gold.csv"))
          if not os.path.exists(os.path.join(args.o,name)):
              os.makedirs(os.path.join(args.o,name))
    
    ## Create the training data matrix and write to a file
    if(args.t):
        train_data, train_class = createMLTrainingMatrix.createMLTrainingMatrix(infiles, args.r, args.j, False, args.t, int(args.w))
    ## Get training data for ML methods by importing pre-made boolean matrix
   
    ## Train ML methods on training data
    if(args.m == "DT"):
        ## Train the decision tree classifier and save in the classifier variable
        classifier, feats = DTree.build_dt_model("./data/aquaint_train_data_TrainWin3.csv", "./data/aquaint_train_class_TrainWin3.csv")

    elif(args.m == "NN"):
        ## Train the neural network classifier and save in the classifier variable
        classifier = ChronoKeras.build_model("./data/aquaint_train_data_TrainWin3.csv", "./data/aquaint_train_class_TrainWin3.csv")
        feats = utils.get_features("./data/aquaint_train_data_TrainWin3.csv")
    else:
        ## Train the naive bayes classifier and save in the classifier variable
        classifier, feats, NB_input = NBclass.build_model("./data/aquaint_train_data_TrainWin3.csv", "./data/aquaint_train_class_TrainWin3.csv")
        classifier.show_most_informative_features(20)
        
    ## Pass the ML classifier through to the parse SUTime entities method.
  
    ## Loop through each file and parse
    for f in range(0,len(infiles)) :
        print("Parsing "+ infiles[f] +" ...")
        ## Init the ChronoEntity list
        my_chronoentities = []
        my_chrono_ID_counter = 1
        
        ## parse out the doctime
        doctime = utils.getDocTime(infiles[f] + ".dct")
        if(debug) : print(doctime)
        
        ## parse out reference tokens
        text, tokens, spans = utils.getWhitespaceTokens(infiles[f])
        my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, span=spans, remove_stopwords="./Chrono/stopwords_short2.txt")
        if(debug) :
            print("REFERENCE TOKENS:\n")
            for tok in my_refToks : print(tok)
        
        
        ## parse out SUTime entities
        #print(infiles[0])
        json_str = sutime_wrapper.callSUTimeParse(infiles[f], args.j)
        suList = sutimeEntity.import_SUTime(sut_json=json_str, doctime=doctime)
        if(debug) : 
            print("SUTIME ENTITIES:\n")
            for s in suList : print(s)
        
        ## mark all reference tokens that overlap with the sutime spans
        my_refToks = utils.markTemporalRefToks(my_refToks, suList)
        if(debug) : 
            for tok in my_refToks : print(tok)
        
        try :
            tmpList, tmpCounter = SUTime_To_Chrono.buildChronoList(suList, my_chrono_ID_counter, my_refToks, (classifier, args.m), feats, doctime)
        except ValueError:
            print("Value ERROR on "+infiles[f])
        else :
            chrono_master_list = tmpList
            my_chrono_ID_counter = tmpCounter
        ## Need functions to parse the SUTime data into T6 format with links!
        ## I think we may need to create a class that is a T6List. We are going to 
        ## need to pull out specific entities based on ID to link them to others if 
        ## we are going to do multiple passes of the text.
        
        ########### Parse time data HERE ##############
        
        ##### Manually adding some T6 entities based on the wsj_0152 file #########
        #t6list = utils.manualT6AddEntities(my_chronoentities)
        #utils.write_xml(t6list=my_chronoentities, outfile=outfiles[f])
        print("Number of Chrono Entities: " + str(len(chrono_master_list)))
        utils.write_xml(chrono_list=chrono_master_list, outfile=outfiles[f])
    
    
    #os.chdir(args.a)
    #os.system("python -m anafora.evaluate -r" + args.r + " -p " + args.o + " --exclude Event After Before Between Frequency Union Modifier Period This")

 
    
    
    
    
    
    
    
    
    
    
