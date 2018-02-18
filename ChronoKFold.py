# From https://stackoverflow.com/questions/41214527/k-fold-cross-validation-using-keras
# Usage: python ChronoKFold.py > kfoldoutput.txt
# use sed '/\*/!d' kfoldoutput.txt to see just scores
# Luke Maffey

import numpy as np
import os
import pandas as pd
import shutil
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# used to copy files according to each fold
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

    # # create subfolders for each class
    # for c in set(list(df['filename'])):
    #     if not os.path.exists(destination_directory + '/' + str(c)):
    #         os.makedirs(destination_directory + '/' + str(c))

    # copy files for this fold from a directory holding all the files
    for i, row in df.iterrows():
        try:
            # this is the path to all of your file kept together in a separate folder
            path_from = "./data/SemEval-Task6-Train/" + row['filename']
            path_to = destination_directory + row['filename']
            gold_from = "./data/SemEval-Task6-TrainGold/" + row['filename']
            gold_to = gold_destination + row['filename']

            # move from folder keeping all files to training, test, or validation folder (the "directory" argument)
            shutil.copytree(path_from, path_to)
            shutil.copytree(gold_from,gold_to)
        except Exception as e:
            print("Error when copying {}: {}".format(row['filename'], str(e)))

# dataframe containing the filenames of the files (e.g., GUID filenames) and the classes
df = pd.read_csv('kfold_files_new.csv', names=['filename','class'])
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

    # take 20% of the training data from this fold for validation during training
    # validation = train.sample(frac = 0.2)

    # make sure validation data does not include training data
    # train = train[~train['filename'].isin(list(validation['filename']))]

    # copy the images according to the fold
    copy_files(train, 'training')
    # copy_files(validation, 'validation')
    copy_files(test, 'test')

    print('**** Running fold '+ str(i))
    createMLTrainingMatrix.createMLTrainingMatrix("./kfold/Training/","./kfold/TrainingGold/",window=5, output="./kfold/kfoldML")
    run_chrono = "python run_chrono.py -i ./kfold/test/ -r ./kfold/TestGold/ -o ./kfold/TestResults -m NN -d ./kfold/kfoldMLdata.csv -c ./kfold/kfoldMLclass.csv"
    eval_chrono = "python -m anafora.evaluate -r ../kfold/TestGold/ -p ../kfold/TestResults/ --exclude Event Modifier"
    import subprocess
    process = subprocess.Popen(run_chrono.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    process = subprocess.Popen(eval_chrono.split(), stdout=subprocess.PIPE, cwd='anaforatools')
    for line in process.stdout: print(line)
    # output, error = process.communicate()
    # print(output)
    # here you call a function to create and train your model, returning validation accuracy and validation loss
#     val_accuracy, val_loss = create_train_model();
#
#     # append validation accuracy and loss for average calculation later on
#     total_val_accuracy.append(val_accuracy)
#     total_val_loss.append(val_loss)
#
#     # here you will call a predict() method that will predict the images on the "test" subfolder
#     # this function returns the actual classes and the predicted classes in the same order
#     actual, predicted = predict()
#
#     # append accuracy from the predictions on the test data
#     total_test_accuracy.append(accuracy_score(actual, predicted))
#
#     # append all of the actual and predicted classes for your final evaluation
#     total_actual = total_actual + actual
#     total_predicted = total_predicted + predicted
#
#     # this is optional, but you can also see the performance on each fold as the process goes on
#     print(classification_report(total_actual, total_predicted))
#     print(confusion_matrix(total_actual, total_predicted))
#
# print(classification_report(total_actual, total_predicted))
# print(confusion_matrix(total_actual, total_predicted))
# print("Validation accuracy on each fold:")
# print(total_val_accuracy)
# print("Mean validation accuracy: {}%".format(np.mean(total_val_accuracy) * 100))
#
# print("Validation loss on each fold:")
# print(total_val_loss)
# print("Mean validation loss: {}".format(np.mean(total_val_loss)))
#
# print("Test accuracy on each fold:")
# print(total_test_accuracy)
# print("Mean test accuracy: {}%".format(np.mean(total_test_accuracy) * 100))