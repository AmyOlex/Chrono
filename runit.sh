#!/bin/bash
# Author: Amy Olex
# 10/7/17
# Description: 	This bash script executes the SemEval 2018 Task6 Time Normalizations project, then evaluates the results.
# 		You must be in the top level of the CMSC516-SemEval2018-Task6 folder to run this project.
#
# Usage: >> source runit.sh [NB | NN | DT]

ML=$1

## Run the program and save results in ./results folder
echo "Running Chrono on input files....."
python run_chrono.py -i ./data/SemEval-Task6-Test/ -r ./data/SemEval-Task6-TestGold/ -o ./resultsTest/ -m $ML

## Run the following if you want to create a new training data matrix
#python run_chrono.py -i ./data/SemEval-Task6-Train/ -r ./data/SemEval-Task6-TrainGold/ -o ./resultsTrain/ -t "my_train_matrix" -w 3 -m $ML 

## go to the anaforatools directory
cd anaforatools

## run the evaluation script
echo "Evaluating Chrono Results..."
python -m anafora.evaluate -r ../data/SemEval-Task6-TestGold/ -p ../resultsTest/ --exclude Event After Before Between Frequency Union Modifier This Intersection NthFromStart

## go to baselinecode Directory
cd ../

## run GUTime Baseline Code
echo "Running GUTime on input files..."
cd BaselineCode/GUTime
python run_baseline_code.py -i ../../data/SemEval-Task6_GUTime-TestData/ -o ../../baseline_resultsTest/

## go to anaforatools directory
cd ../../
cd anaforatools

#echo "Evaluating Baseline Results..."
python -m anafora.evaluate -r ../data/SemEval-Task6-TestGold -p ../baseline_resultsTest/ --exclude Event After Before Between Frequency Union Modifier This Intersection NthFromStart --overlap

## change back to main directory
cd ../
