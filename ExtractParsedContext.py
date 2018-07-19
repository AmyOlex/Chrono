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
## Example Usage:  python ExtractParsedContext.py -x data/SemEval-OfficialTrain -i results/newswire.list -t data/SemEval-OfficialTrain -o results/output1-Gold-MinuteOfHour.txt -e Minute-Of-Hour -f gold -c 25

import argparse
from xml.dom import minidom
import os.path

if __name__ == "__main__":
    
    ## Parse input arguments
    parser = argparse.ArgumentParser(description='Extract entity context information from text using the AnaforaXML Annotation files.')
    parser.add_argument('-x', metavar='xmldir', type=str, help='path to the input xml directory that holds the annotated files.', required=True)
    parser.add_argument('-i', metavar='filelist', type=str, help='File with list of documents to parse.', required=True)
    parser.add_argument('-t', metavar='textfiledir', type=str, help='Path to directory holding the raw text files.', required=True)
    parser.add_argument('-o', metavar='outputfile', type=str, help='Name of the output file to save results to.', required=True)
    parser.add_argument('-e', metavar='entity', type=str, help='The name of the entity we want to extract.', required=True)
    parser.add_argument('-f', metavar='flag', type=str, help='gold or chrono', required=True)
    parser.add_argument('-c', metavar='context', type=str, help='The number of characters before and after for context.', required=False, default=20)

    args = parser.parse_args()
    ## Now we can access each argument as args.i, args.o, args.r
    
    def getTargetSpans(xmlfile, entity):
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
            
            if etype == entity:
                start, end = espan.split(",")
                entitylist.append([eid, etype, int(start), int(end), enumber])
        return(entitylist)
    
    
    def writeTargetSpans(infile, entitylist, context, outfile):
        linestring = open(infile, 'r').read()
        term_set = set()
        
        for entity in entitylist:
            start = max(0,int(entity[2])-context)
            end = min(len(linestring), int(entity[3])+context)
            
            if context > 0:
                outfile.write("\n\nID: " + entity[0] + ", Type: " + entity[1] + ", Span: (" + str(entity[2]) + "," + str(entity[3]) + "), Value: " + linestring[entity[2]:entity[3]] + ", Number: " + entity[4])
                outfile.write("\n" + linestring[start:end])
        
            else:
                term_set = term_set.union({linestring[start:end].lower()})
        
        return(term_set)
    
    
    
    ## Loop over each file in the file list and parse it
    out = open(args.o, 'w')
    inputfiles = open(args.i, 'r').read().split("\n")
    terms = set()
    
    for f in inputfiles:
        
        ## Open the XML file and parse it
        if args.f == "gold":
            path = args.x + "/" + f + "/" + f + ".TimeNorm.gold.completed.xml"
        else:
            path = args.x + "/" + f + "/" + f + ".completed.xml"
        
        if(os.path.isfile(path)):
            myElist = getTargetSpans(path, args.e)
        
            ## Pass this information to extract the text segments and write to file
            path2 = args.t + "/" + f + "/" + f
            if(os.path.isfile(path2)):
                if int(args.c) > 0:
                    out.write("\n\n*****\nFile: " + f)
                
                tmp_terms = writeTargetSpans(path2, myElist, int(args.c), out)
                #print("my tmp_terms: " + str(tmp_terms))
                
                terms = terms.union(tmp_terms)
                #print("my terms: " + str(terms))
        else:
            if int(args.c) > 0:
                out.write("\n\n*****\nSkipping File: " + f)
    
    if int(args.c) == 0:
        for t in sorted(terms):
            out.write("\n" + t)
    
    out.close()
    print("Completed!")
    
    
    
    
    
    
    
    
    
