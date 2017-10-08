#!/bin/bash
# Author: Amy Olex
# 10/7/17
# Description: 	This bash script executes the SemEval 2018 Task6 Time Normalizations project, then evaluates the results.
# 		You must be in the top level of the CMSC516-SemEval2018-Task6 folder to run this project.
#
# Usage: >> source runit.sh

## Run the program and save results in ./results folder
python run_task6.py -i ./data/SemEval-Task6_TestData/ -o ./results/ -j ./jars/

## go to the anaforatools directory
cd anaforatools

## run the evaluation script
python -m anafora.evaluate -r ../data/SemEval-Task6-Baseline -p ../results/ --exclude Event After Before Between Frequency Union Modifier Period This

## change back to main directory
cd ../
