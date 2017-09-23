## This is the Task6 main method.  The parsing of a full directory will be done from running this program.
#
# Date: 9/23/17
#
# Programmer Name: Amy Olex

###### Workflow ######
##
## 1) get location of files to parse
## 2) get location of output directory
## 3) Initilize out T6Entity list
## 4) Initilize the globally unique ID counter
## 5) For each FILE:
##      a) parse with stanford parser to get whitespace tokens and associated spans
##      b) import this into a refToken object list
##      c) parse with SUTime and import into a sutimeEntity list
##      d) Compare SUTime spans with the refToken spans to mark which refToken has temporal information.
##      e) EITHER 1) parse all SUTime entities into T6Entities OR parse all temporally tagged refTokens into T6Entities. << not sure which is better at the moment.
## 6) Print out the T6Entity list to an XML file
## 7) Run the evaluation code and print out precision and recall **need to import this code into our package**

import sys
import os
import argparse

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
    args = parser.parse_args()
    ## Now we can access each argument as args.i, args.o, args.r
    
    ## Get list of folder names in the input directory
    indirs = []
    infiles = []
    outfiles = []
    for root, dirs, files in os.walk(args.i, topdown = True):
       for name in dirs:
          indirs.append(os.path.join(root, name))
          infiles.append(os.path.join(root, name,name))
          outfiles.append(name)
    
    ## Now create each output directory
    ## Loop through outfiles and create a directory for each
    ## Then walk the structure to get the full paths to each output file.
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    