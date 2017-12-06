#!/bin/bash
# Author: Amy Olex
# 10/7/17
# Description: 	This bash script executes the SemEval 2018 Task6 Time Normalizations project, then evaluates the results.
# 		You must be in the top level of the CMSC516-SemEval2018-Task6 folder to run this project.
#
# Usage: >> source runit.sh [NB | NN | DT]

ML=$1

## Run the program and save results in ./results folder
echo "Running T6 on input files....."
#python run_task6.py -i ./testdata/train/ -r ./testdata/gold/ -o ./testresults/ -t 0 -m NB
python run_task6.py -i ./data/SemEval-Task6-Test/ -r ./data/SemEval-Task6-TestGold/ -o ./resultsTest/ -t 0 -m $ML
## go to the anaforatools directory
cd anaforatools

## run the evaluation script
echo "Evaluating T6 Results..."
python -m anafora.evaluate -r ../data/SemEval-Task6-TestGold/ -p ../resultsTest/ --exclude Event After Before Between Frequency Union Modifier This Intersection NthFromStart

## go to baselinecode Directory
#cd ../

## run GUTime Baseline Code
#echo "Running GUTime on input files..."
#cd BaselineCode/GUTime
#python run_baseline_code.py -i ../../data/SemEval-Task6_GUTime-Data/ -o ../../data/SemEval-Task6-GUTime-Results/

## go to anaforatools directory
#cd ../../
#cd anaforatools

#echo "Evaluating Baseline Results..."
#python -m anafora.evaluate -r ../data/SemEval-Task6-Gold -p ../data/SemEval-Task6-GUTime-Results/ --exclude Event After Before Between Frequency Union Modifier Period This --overlap

## change back to main directory
#cd ../
