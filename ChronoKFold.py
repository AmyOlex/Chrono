# From https://stackoverflow.com/questions/41214527/k-fold-cross-validation-using-keras
# Usage: python ChronoKFold.py > kfoldoutput.txt
# use sed '/\*/!d' kfoldoutput.txt to see just scores
# Luke Maffey

import numpy as np
import os
import pandas as pd
import shutil
from sklearn.model_selection import StratifiedKFold

from Chrono import createMLTrainingMatrix


def copy_files(df, directory):
    destination_directory = "./kfold/" + directory +"/"
    gold_destination = "./kfold/" + directory + "Gold/"

    print("copying {} files to {}...".format(directory, destination_directory))

    # remove all files from previous fold
    if os.path.exists(destination_directory):
        shutil.rmtree(destination_directory)
    if os.path.exists(gold_destination):
        shutil.rmtree(gold_destination)

    # create folder for files from this fold
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # copy files for this fold from a directory holding all the files
    for i, row in df.iterrows():
        try:
            # this is the path to all of your file kept together in a separate folder
            path_from = "./data/SemEval-OfficialTrain/" + row['filename']
            path_to = destination_directory + row['filename']

            gold_from = "./data/SemEval-OfficialTrain/" + row['filename']
            gold_to = gold_destination + row['filename']

            # move from folder keeping all files to training, test, or validation folder (the "directory" argument)
            shutil.copytree(path_from, path_to)
            shutil.copytree(gold_from,gold_to)
        except Exception as e:
            print("Error when copying {}: {}".format(row['filename'], str(e)))

# dataframe containing the filenames of the files (e.g., GUID filenames) and the classes
df = pd.read_csv('kfold_files_new_official.csv', names=['filename','class'])
df_y = df['class']
df_x = df
del df_x['class']

skf = StratifiedKFold(n_splits = 5)
total_actual = []
total_predicted = []
total_val_accuracy = []
total_val_loss = []
total_test_accuracy = []

for i, (train_index, test_index) in enumerate(skf.split(df_x, df_y)):
    x_train, x_test = df_x.iloc[train_index], df_x.iloc[test_index]
    y_train, y_test = df_y.iloc[train_index], df_y.iloc[test_index]

    train = pd.concat([x_train, y_train], axis=1)
    test = pd.concat([x_test, y_test], axis = 1)

    copy_files(train, 'training')
    copy_files(test, 'test')

    print('**** Running fold '+ str(i))
    mltrain = []
    for x in train['filename'].values.tolist():
        mltrain.append("./kfold/training/" + x + "/" + x)

    createMLTrainingMatrix.createMLTrainingMatrix(mltrain,"./kfold/trainingGold/",window=5, output="./kfold/kfoldML")
    run_chrono = "python run_chrono.py -i ./kfold/test/ -r ./kfold/testGold/ -o ./kfold/TestResults -m SVM -d ./kfold/kfoldML_data.csv -c ./kfold/kfoldML_class.csv"
    eval_chrono = "python -m anafora.evaluate -r ../kfold/testGold/ -p ../kfold/TestResults/ --exclude Event Modifier"

    import subprocess
    process = subprocess.Popen(run_chrono.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    process = subprocess.Popen(eval_chrono.split(), stdout=subprocess.PIPE, cwd='anaforatools')
    for line in process.stdout: print(line)