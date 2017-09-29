## This is the Task6 main method.  The parsing of a full directory will be done from running this program.
#
# Date: 9/23/17
#
# Programmer Name: Amy Olex

###### Workflow ######
##
## 1) get location of files to parse (DONE)
## 2) get location of output directory/create output directories (DONE)
## 3) Initilize the T6Entity list
## 4) Initilize the globally unique ID counter
## 5) For each FILE:
##      a) parse with stanford parser to get whitespace tokens and associated spans
##      b) import this into a refToken object list
##      c) parse with SUTime and import into a sutimeEntity list
##      d) Compare SUTime spans with the refToken spans to mark which refToken has temporal information.
##      e) EITHER 1) parse all SUTime entities into T6Entities OR parse all temporally tagged refTokens into T6Entities. << not sure which is better at the moment.
## 6) Print out the T6Entity list to an XML file
## 7) Run the evaluation code and print out precision and recall **need to import this code into our package**
##
## To test run:
## python run_task6.py -i /Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_test -o /Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_eval -r /Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/TempEval-2013_test -j /Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/CMSC516-SemEval2018-Task6/task6/jars/ -a /Users/alolex/Desktop/VCU_PhD_Work/CMSC516/project/anaforatools/




import sys
import os
import argparse
from task6 import t6Entities
from task6 import utils
from task6 import sutimeEntity
from task6 import referenceToken
from task6 import sutime_wrapper

debug=False
# @description This is the driver method to run all of task6. 
# @param INDIR The location of the directory with all the files in it.
# @param OUTDIR The location of the directory where you want all the output written.
# @param REFDIR The location of the gold standard XML files for evaluation.
# @output Anafora formatted XML files, one directory per file with one XML file in each directory.
# @output The precision and recall from comparing output results to the gold standard.
if __name__ == "__main__":
    
    ## Parse input arguments
    parser = argparse.ArgumentParser(description='Parse a directory of files to identify and normalize temporal information.')
    parser.add_argument('-i', metavar='inputdir', type=str, help='path to the input directory.', required=True)
    parser.add_argument('-o', metavar='outputdir', type=str, help='path to the output directory.', required=True)
    parser.add_argument('-r', metavar='refdir', type=str, help='path to the gold standard directory.', required=True)
    parser.add_argument('-j', metavar='jardir', type=str, help='path to the directory with all the SUTime required jar files. Default is ./jars', required=False, default="./jars")
    parser.add_argument('-a', metavar='anaforatooldir', type=str, help='path to the top level directory of anaforatools package. Default is ./anaforatools', required=False, default="./anaforatools")
    
    args = parser.parse_args()
    ## Now we can access each argument as args.i, args.o, args.r
    
    ## Get list of folder names in the input directory
    indirs = []
    infiles = []
    outfiles = []
    outdirs = []
    for root, dirs, files in os.walk(args.i, topdown = True):
       for name in dirs:
          indirs.append(os.path.join(root, name))
          infiles.append(os.path.join(root, name,name))
          outfiles.append(os.path.join(args.o,name,name))
          outdirs.append(os.path.join(args.o,name))
          if not os.path.exists(os.path.join(args.o,name)):
              os.makedirs(os.path.join(args.o,name))
    
    ## Init the T6Entity list
    my_t6entities = []
    my_t6IDcounter = 1
    
    ## Loop through each file and parse
    for f in range(0,len(infiles)) :
        ## parse out reference tokens
        text, tokens, spans = utils.getWhitespaceTokens(infiles[f])
        my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, span=spans)
        if(debug) : 
            print("REFERENCE TOKENS:\n")
            for tok in my_refToks : print(tok)
        
        ## parse out SUTime entities
        json_str = sutime_wrapper.callSUTimeParse(infiles[f], args.j)
        suList = sutimeEntity.import_SUTime(sut_json=json_str)
        if(debug) : 
            print("SUTIME ENTITIES:\n")
            for s in suList : print(s)
        
        ## parse out the doctime
        docTime = utils.getDocTime(infiles[f] + ".dct")
        print(docTime)
    
    
        ## Need functions to parse the SUTime data into T6 format with links!
        ## I think we may need to create a class that is a T6List. We are going to 
        ## need to pull out specific entities based on ID to link them to others if 
        ## we are going to do multiple passes of the text.
        
        ########### Parse time data HERE ##############
        
        ##### Manually adding some T6 entities based on the wsj_0152 file #########
        t6list = utils.manualT6AddEntities()
        utils.write_xml(t6list=t6list, outfile=outfiles[f])
    
    
    os.chdir(args.a)
    os.system("python -m anafora.evaluate -r" + args.r + " -p " + args.o)
    
    
    
    
    
    
    
    
    
    
    
    
    