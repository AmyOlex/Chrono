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

## This is the main driver program that runs Chrono.  

import argparse
import os
import pickle

from chronoML import DecisionTree as DTree
from chronoML import RF_classifier as RandomForest
from chronoML import NB_nltk_classifier as NBclass, ChronoKeras
from chronoML import SVM_classifier as SVMclass
from Chrono import TimePhrase_to_Chrono
from Chrono import referenceToken
from Chrono import utils
from keras.models import load_model

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
    parser.add_argument('-x', metavar='fileExt', type=str, help='input file extension if exists. Default is and empty string', required=False, default="")
    parser.add_argument('-o', metavar='outputdir', type=str, help='path to the output directory.', required=True)
    parser.add_argument('-m', metavar='MLmethod', type=str, help='The machine learning method to use. Must be one of NN (neural network), DT (decision tree), SVM (support vector machine), NB (naive bayes, default).', required=False, default='NB')
    parser.add_argument('-w', metavar='windowSize', type=str, help='An integer representing the window size for context feature extraction. Default is 3.', required=False, default=3)
    parser.add_argument('-d', metavar='MLTrainData', type=str, help='A string representing the file name that contains the CSV file with the training data matrix.', required=False, default=False)
    parser.add_argument('-c', metavar='MLTrainClass', type=str, help='A string representing the file name that contains the known classes for the training data matrix.', required=False, default=False)
    parser.add_argument('-M', metavar='MLmodel', type=str, help='The path and file name of a pre-build ML model for loading.', required=False, default=None)
    
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
          infiles.append(os.path.join(root,name,name))
          outfiles.append(os.path.join(args.o,name,name))
          outdirs.append(os.path.join(args.o,name))
          if not os.path.exists(os.path.join(args.o,name)):
              os.makedirs(os.path.join(args.o,name))
    
    ## Get training data for ML methods by importing pre-made boolean matrix
    ## Train ML methods on training data
    if(args.m == "DT" and args.M is None):
        ## Train the decision tree classifier and save in the classifier variable
        #print("Got DT")
        classifier, feats = DTree.build_dt_model(args.d, args.c)
        with open('DT_model.pkl', 'wb') as mod:  
            pickle.dump([classifier, feats], mod)

    if(args.m == "RF" and args.M is None):
        ## Train the decision tree classifier and save in the classifier variable
        # print("Got RF")
        classifier, feats = RandomForest.build_model(args.d, args.c)
        with open('RF_model.pkl', 'wb') as mod:
            pickle.dump([classifier, feats], mod)
    
    elif(args.m == "NN" and args.M is None):
        #print("Got NN")
        ## Train the neural network classifier and save in the classifier variable
        classifier = ChronoKeras.build_model(args.d, args.c)
        feats = utils.get_features(args.d)
        classifier.save('NN_model.h5')
            
    elif(args.m == "SVM" and args.M is None):
        #print("Got SVM")
        ## Train the SVM classifier and save in the classifier variable
        classifier, feats = SVMclass.build_model(args.d, args.c)
        with open('SVM_model.pkl', 'wb') as mod:  
            pickle.dump([classifier, feats], mod)
            
    elif(args.M is None):
        #print("Got NB")
        ## Train the naive bayes classifier and save in the classifier variable
        classifier, feats, NB_input = NBclass.build_model(args.d, args.c)
        classifier.show_most_informative_features(20)
        with open('NB_model.pkl', 'wb') as mod:  
            pickle.dump([classifier, feats], mod)
                
    elif(args.M is not None):
        #print("use saved model")
        if args.m == "NB" or args.m == "DT":
            with open(args.M, 'rb') as mod:
                print(args.M)
                classifier, feats = pickle.load(mod)
        elif args.m == "NN":
            classifier = load_model(args.M)
            feats = utils.get_features(args.d)
    
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
        text, tokens, spans, tags, sents = utils.getWhitespaceTokens(infiles[f]+args.x)
        #my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, span=spans, remove_stopwords="./Chrono/stopwords_short2.txt")
        my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, span=spans, pos=tags, sent_boundaries=sents)
        

    
        ## mark all ref tokens if they are numeric or temporal
        chroList = utils.markTemporal(my_refToks)
        
        if(debug) :
            print("REFERENCE TOKENS:\n")
            for tok in chroList : print(tok)
            
        tempPhrases = utils.getTemporalPhrases(chroList, doctime)
    
#        for c in tempPhrases:
#            print(c)
    
        chrono_master_list, my_chrono_ID_counter = TimePhrase_to_Chrono.buildChronoList(tempPhrases, my_chrono_ID_counter, chroList, (classifier, args.m), feats, doctime)
        
        print("Number of Chrono Entities: " + str(len(chrono_master_list)))
        utils.write_xml(chrono_list=chrono_master_list, outfile=outfiles[f])
    
    
