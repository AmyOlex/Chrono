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
    parser.add_argument('-x', metavar='annodir', type=str, help='path to the input directory that holds the annotated files.', required=True)
    parser.add_argument('-F', metavar='annotype', type=str, help='the format of the annotation files. Can be xml or ann. Default is xml.', required=False, default="xml")
    parser.add_argument('-i', metavar='filelist', type=str, help='File with list of documents to parse.', required=True)
    parser.add_argument('-t', metavar='textfiledir', type=str, help='Path to directory holding the raw text files.', required=True)
    parser.add_argument('-E', metavar='textfileext', type=str, help='Extension of the raw text files.  Default is blank for no extension. All text files must have the same extension.', required=False, default="")
    parser.add_argument('-o', metavar='outputfile', type=str, help='Name of the output file to save results to.', required=True)
    parser.add_argument('-e', metavar='entity', type=str, help='The name of the entity we want to extract.', required=True)
    parser.add_argument('-f', metavar='flag', type=str, help='gold or chrono', required=True)
    parser.add_argument('-c', metavar='context', type=str, help='The number of characters before and after for context.', required=False, default=20)

    args = parser.parse_args()
    ## Now we can access each argument as args.i, args.o, args.r
    
    def getTargetSpansXML(xmlfile, entity):
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
    
    def writeTargetSpansXML(infile, entitylist, context, outfile):
        linestring = open(infile, 'r').read()
        term_set = set()
        
        for entity in entitylist:
            start = max(0,int(entity[2])-context)
            end = min(len(linestring), int(entity[3])+context)
            
            if context > 0:
                outfile.write("\n\nID: " + entity[0] + ", Type: " + entity[1] + ", Span: (" + str(entity[2]) + "," + str(entity[3]) + "), Raw Token: " + linestring[entity[2]:entity[3]] + ", Number: " + entity[4])
                outfile.write("\n" + linestring[start:end])
        
            else:
                term_set = term_set.union({linestring[start:end].lower()})
        
        return(term_set)
    
 
 
    def getTargetSpansANN(annfile, entity):
        
        with open(annfile) as file:
            content = file.readlines()
        
        content = [x.strip() for x in content]
        
        entitylist = []
        for line in content:
            fields = line.split()
            print(fields)
            
            if len(fields) >= 5:
                eid = fields[0]
                etype = fields[1]
                estart = fields[2]
                eend = fields[3]
                etoken = ' '.join(fields[4:len(fields)])
            elif len(fields) == 4:
                eid = fields[0]
                etype = fields[1]
                estart = fields[2]
                eend = fields[3]
                etoken = ""
            else:
                print("Error: uknown field length.")
                return(0)
                
            
            if etype == entity:
                entitylist.append([eid, etype, int(estart), int(eend), etoken])
        return(entitylist)
        
    def writeTargetSpansANN(infile, entitylist, context, outfile):
        linestring = open(infile, 'r').read()
        term_set = set()
        
        for entity in entitylist:
            start = max(0,int(entity[2])-context)
            end = min(len(linestring), int(entity[3])+context)
            
            if context > 0:
                outfile.write("\n\nID: " + entity[0] + ", Type: " + entity[1] + ", Span: (" + str(entity[2]) + "," + str(entity[3]) + "), Raw Token: " + linestring[entity[2]:entity[3]] + ", Listed Token: " + entity[4])
                outfile.write("\n" + linestring[start:end])
        
            else:
                term_set = term_set.union({linestring[start:end].lower()})
        
        return(term_set)    
        
############### Start Main Method ######################        
           
    
    ## Loop over each file in the file list and parse it
    out = open(args.o, 'w')
    inputfiles = open(args.i, 'r').read().split("\n")
    terms = set()
    
    
    if args.F == "xml":
    
        for f in inputfiles:
        
            ## Open the XML file and parse it
            if args.f == "gold":
                path = args.x + "/" + f + "/" + f + ".TimeNorm.gold.completed.xml"
            else:
                path = args.x + "/" + f + "/" + f + ".completed.xml"
        
            if(os.path.isfile(path)):
                myElist = getTargetSpansXML(path, args.e)
        
                ## Pass this information to extract the text segments and write to file
                path2 = args.t + "/" + f + "/" + f
                if(os.path.isfile(path2)):
                    if int(args.c) > 0:
                        out.write("\n\n*****\nFile: " + f)
                
                    tmp_terms = writeTargetSpansXML(path2, myElist, int(args.c), out)
                    #print("my tmp_terms: " + str(tmp_terms))
                
                    terms = terms.union(tmp_terms)
                    #print("my terms: " + str(terms))
            else:
                if int(args.c) > 0:
                    out.write("\n\n*****\nSkipping File: " + f)
    
        if int(args.c) == 0:
            for t in sorted(terms):
                out.write("\n" + t)
    
    elif args.F == "ann":
        for f in inputfiles:
        
            ## Open the XML file and parse it
            if args.f == "gold":
                path = args.x + "/" + f + ".ann"
            else:
                path = args.x + "/" + f + ".ann"
        
            if(os.path.isfile(path)):
                myElist = getTargetSpansANN(path, args.e)
        
                ## Pass this information to extract the text segments and write to file
                path2 = args.t + "/" + f + args.E
                if(os.path.isfile(path2)):
                    if int(args.c) > 0:
                        out.write("\n\n*****\nFile: " + f)
                
                    tmp_terms = writeTargetSpansANN(path2, myElist, int(args.c), out)
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
    
    
    
    
    
    
    
    
    
