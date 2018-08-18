# Copyright (c) 2018 
# Amy L. Olex, Virginia Commonwealth University
# alolex at vcu.edu
#
# Luke Maffey, Virginia Commonwealth University
# maffeyl at vcu.edu
#
# Nicholas Morton,  Virginia Commonwealth University 
# nmorton at vcu.edu
#
# Bridget T. McInnes, Virginia Commonwealth University
# btmcinnes at vcu.edu
#
# This file is part of Chrono
#
# Chrono is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Chrono is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Chrono; if not, write to 
#
# The Free Software Foundation, Inc., 
# 59 Temple Place - Suite 330, 
# Boston, MA  02111-1307, USA.

## This program extracts the specified context around each SCATE Entity of a certain type.  
## Example Usage:  python xml2ann.py -x data/SemEval-OfficialTrain -i results/newswire.list -t data/SemEval-OfficialTrain -o results/entities.ann -f gold 

import argparse
from xml.dom import minidom
import os.path

if __name__ == "__main__":
    
    ## Parse input arguments
    parser = argparse.ArgumentParser(description='Extract entity information from AnaforaXML Annotation files and the raw text, and convert to ANN formatted files. Note this method only converts the entities and currently does not handle relation extraction.')
    parser.add_argument('-x', metavar='xmldir', type=str, help='path to the input directory that holds the annotated XML files (must be named using file ID).', required=True)
    parser.add_argument('-i', metavar='filelist', type=str, help='List of document IDs to parse.', required=True)
    parser.add_argument('-t', metavar='textfiledir', type=str, help='Path to directory holding the raw text files (must be named using file id).', required=True)
    parser.add_argument('-E', metavar='textfileext', type=str, help='Extension of the raw text files.  Default is blank for no extension. All text files must have the same extension.', required=False, default="")
    parser.add_argument('-o', metavar='outdir', type=str, help='Name of the output file directory to save results to. If blank, will save .ann files to same directory as input files.', required=False, default="")
    parser.add_argument('-f', metavar='flag', type=str, help='Must be one of (gold, chrono) to identify correct xml file extension.', required=True)
    
    args = parser.parse_args()
    ## Now we can access each argument as args.i, args.o, args.r
    
    def getTargetSpansXML(xmlfile):
        xmldoc = minidom.parse(xmlfile)
        itemlist = xmldoc.getElementsByTagName('entity')
        entitylist = []
        for item in itemlist:
            eid = item.getElementsByTagName('id')[0].firstChild.data
            espan = item.getElementsByTagName('span')[0].firstChild.data
            etype = item.getElementsByTagName('type')[0].firstChild.data
            eproperties = item.getElementsByTagName('properties')
            
            if(len(eproperties[0].getElementsByTagName('Number')) == 1):
                tmp = eproperties[0].getElementsByTagName('Number')[0].firstChild
                if tmp is not None:
                    enumber = eproperties[0].getElementsByTagName('Number')[0].firstChild.data
                else:
                    enumber = "None"
            else:
                enumber = ""
            
            start, end = espan.split(",")
            entitylist.append([eid, etype, int(start), int(end), enumber])
        return(entitylist)   
    
    def writeTargetSpansXML(infile, entitylist, outfile):
        linestring = open(infile, 'r').read()
        term_set = set()
        
        count = 1
        for entity in entitylist:
            start = int(entity[2])
            end = int(entity[3])
            
            outfile.write("\nT" + str(count) + "\t" + entity[1] + " " + str(entity[2]) + " " + str(entity[3]) + "\t" + linestring[entity[2]:entity[3]])
            count = count+1
 
        
############### Start Main Method ######################        
           
    
    ## Loop over each file in the file list and parse it
    #out = open(args.o, 'w')
    inputfiles = open(args.i, 'r').read().split("\n")
    terms = set()
    
    
    for f in inputfiles:
        
        if args.o == "":
            outfile = args.x + "/" + f + "/" + f + ".ann"
        else:
            outfile = args.o + "_" + f + ".ann"
        
        out = open(outfile, 'w')
        
        ## Open the XML file and parse it
        if args.f == "gold":
            path = args.x + "/" + f + "/" + f + ".TimeNorm.gold.completed.xml"
        else:
            path = args.x + "/" + f + "/" + f + ".completed.xml"
    
        if(os.path.isfile(path)):
            myElist = getTargetSpansXML(path)
    
            ## Pass this information to extract the text segments and write to file
            path2 = args.t + "/" + f + "/" + f
            if(os.path.isfile(path2)):            
                writeTargetSpansXML(path2, myElist, out)

        else:
            print("Error, can't find file: " + f)    
    
        out.close()
    
    
    
    print("Completed!")
    
    
    
    
    
    
    
    
    
