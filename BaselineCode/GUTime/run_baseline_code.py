import sys
import os
import argparse
import subprocess
import shlex
import GUTime_To_T6 as gut
import t6Entities as t6
import GUTimeEntity


#commands to run in terminal
#python task_6_baseline.py -i ./data/SemEval-Task6_GUTime-Data -o .data/SemEval-Task6-Baseline-GUTime-Results

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

   

    ## Loop through each file and parse out GUTime
    for f in range(0,len(infiles)) :
        print("Parsing "+ infiles[f] +" ...")
        GU_Counter = 1
        GUList = []  
        
        #Build GUTime List
        infile = open(infiles[f], "r")
        fileText = infile.read()
        fileTextList = fileText.split("\n")
        Timex3List = []
        lexList = []
        
        for fi in fileTextList:
            if "<TIMEX3 begin" in fi:
                Timex3List.append(fi)
            elif "<lex begin" in fi:
                lexList.append(fi)        
        
        for t in Timex3List:
            GU_Counter = GU_Counter+1
            start_span1 = t[t.find('begin="')+7:t.find('" end')]
            end_span1 = t[t.find('end="')+5:t.find('" origin')]
            ltext=""

            for l in lexList:
                lstart = l[l.find('begin="')+7:l.find('" end')]
                lend = l[l.find('end="')+5:l.find('" id')]
                
                if lstart == start_span1 and lend == end_span1:
                    ltext = l[l.find('text="')+6:l.find('" /')]           
                     

            GUList.append(GUTimeEntity.GUTimeEntity(id=GU_Counter, 
            text = ltext, 
            start_span =int(t[t.find('begin="')+7:t.find('" end')]) , 
            end_span = int(t[t.find('end="')+5:t.find('" origin')]) , 
            sutype = t[t.find('type="')+6:t.find('" value')] , 
            suvalue =t[t.find('value="')+7:t.find('" /')],doctime=""))
            
        #Convert to T6 List
        print("Size of GUList: " + str(len(GUList)))
        print(GUList[0])
        GUT6List, GU_Counter = gut.buildT6List(GUList,GU_Counter)
        print("Number of T6 Entities: "+str(len(GUT6List)))
        #Output Results
        fout = open(outfiles[f] + ".completed.xml", "w")
        fout.write("<data>\n<annotations>\n")
        for t6 in GUT6List:
            fout.write(str(t6.print_xml()))
        fout.write("\n</annotations>\n</data>")
        fout.close()
    

                  
        



    

    
       
    
    
    
    
    
    
    
    
    
    
    
    
