## This is the Task6 Baseline HeidelTime main method.  The parsing of a full directory will be done from running this program.
#
# Date: 10/10/2017
#
# Programmer Name: Amy Olex / Nick Morton

import sys
import os
import argparse
import HeidTime_To_T6 as heid
import t6Entities as t6
import HeidTime_Wrapper as htw

#commands to run in terminal
#python task_6_baseline.py -i ./data/Raw/ -o ./resultsHeidel/ 
#python -m anafora.evaluate -r ./data/SemEval-Task6-Baseline -p ./resultsHeidel
debug=False
if __name__ == "__main__":
    
    ## Parse input arguments
    parser = argparse.ArgumentParser(description='Parse a directory of files to identify and normalize temporal information.')
    parser.add_argument('-i', metavar='inputdir', type=str, help='path to the input directory.', required=True)
    parser.add_argument('-o', metavar='outputdir', type=str, help='path to the output directory.', required=True)
    args = parser.parse_args()
    
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

   
    ## Loop through each file and parse
    for f in range(0,len(infiles)) :
        my_heidcounter = 1 #initialize counter
        heidList = [] #intialize heidelTime List
        doctime=''      
        print("Current File: ", infiles[f])     #Prints the current file to display directory parsing progress   
        heidList = htw.runHeidTime(infiles[f])  #Runs HeidelTime Standalone Jar for selected file        
        t6HeidList, my_heidcounter = heid.buildT6List(heidList,my_heidcounter,doctime) #Build final T6HeidList
        #Write output to output file
        fout = open(outfiles[f] + ".completed.xml", "w")
        fout.write("<data>\n<annotations>\n") 
        for t6 in t6HeidList :
            fout.write(str(t6.print_xml()))
        fout.write("\n</annotations>\n</data>")
        fout.close()    
