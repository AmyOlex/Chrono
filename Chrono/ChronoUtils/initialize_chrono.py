import pickle
from pathlib import Path
import pkg_resources

from Chrono.chronoML import DecisionTree as DTree, RF_classifier as RandomForest, ChronoKeras, \
    SVM_classifier as SVMclass, NB_nltk_classifier as NBclass
from Chrono.config import DICTIONARY
from Chrono.ChronoUtils.filesystem_utils import path_walk
from Chrono.ChronoUtils.ML_utils import get_features
from keras.models import load_model

def setup_ML(ml_input, ml_model, train_data, train_labels):
    ## Get training data for ML methods by importing pre-made boolean matrix
    ## Train ML methods on training data
    if (ml_input == "DT" and ml_model is None):
        ## Train the decision tree classifier and save in the classifier variable
        # print("Got DT")
        classifier, feats = DTree.build_dt_model(train_data, train_labels)
        with open('DT_model.pkl', 'wb') as mod:
            pickle.dump([classifier, feats], mod)

    if (ml_input == "RF" and ml_model is None):
        ## Train the decision tree classifier and save in the classifier variable
        # print("Got RF")
        classifier, feats = RandomForest.build_model(train_data, train_labels)
        with open('RF_model.pkl', 'wb') as mod:
            pickle.dump([classifier, feats], mod)

    elif (ml_input == "NN" and ml_model is None):
        # print("Got NN")
        ## Train the neural network classifier and save in the classifier variable
        classifier = ChronoKeras.build_model(train_data, train_labels)
        feats = get_features(train_data)
        classifier.save('NN_model.h5')

    elif (ml_input == "SVM" and ml_model is None):
        # print("Got SVM")
        ## Train the SVM classifier and save in the classifier variable
        classifier, feats = SVMclass.build_model(train_data, train_labels)
        with open('SVM_model.pkl', 'wb') as mod:
            pickle.dump([classifier, feats], mod)

    elif (ml_model is None):
        # print("Got NB")
        ## Train the naive bayes classifier and save in the classifier variable
        classifier, feats, NB_input = NBclass.build_model(train_data, train_labels)
        classifier.show_most_informative_features(20)
        with open('NB_model.pkl', 'wb') as mod:
            pickle.dump([classifier, feats], mod)

    elif (ml_model is not None):
        # print("use saved model")
        if ml_input == "NB" or ml_input == "DT":
            with open(ml_model, 'rb') as mod:
                print(ml_model)
                classifier, feats = pickle.load(mod)
        elif ml_input == "NN":
            classifier = load_model(ml_model)
            feats = get_features(train_data)
    return classifier, feats


def initialize(in_dictionary="dictionary"):
    dict_path = pkg_resources.resource_filename('Chrono', in_dictionary + '/')
    # Read in the word lists for each entity
    path = Path(dict_path)
    if Path(dict_path).exists():
        for root, dirs, files in path_walk(path, topdown=True):
            for file in files:
                with file.open() as f:
                    key = file.stem
                    for word in f:
                        if key not in DICTIONARY:
                            DICTIONARY[key] = []
                        DICTIONARY[key].append(word.rstrip('\n'))
    else:
        raise ValueError('Dictionary not found: ' + dict_path)