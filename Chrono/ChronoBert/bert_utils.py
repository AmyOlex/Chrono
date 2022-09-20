# Copyright (c) 2022
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



## Provides all helper functions for Chrono methods that involve a bert model.


import torch
import numpy as np
import tokenizations
import numpy
import re
from itertools import count, groupby
from operator import itemgetter
from sklearn.model_selection import StratifiedKFold
import joblib
import pandas as pd
import tensorflow as tf
from tensorflow.python.keras.preprocessing.sequence import pad_sequences
from transformers import BertTokenizer, BertForTokenClassification

def convert_to_sentence_classification(s):
    """

    :param s:
    :return:
    """
    all_sents = []
    all_labels = []

    sentence = []
    labels = []

    for line in s.split('\n'):
        if line == '':
            # #print("sentence:" + ' '.join(sentence))
            # #print("labels:" + str(labels))
            all_sents.append(' '.join(sentence))
            all_labels.append(max(labels))
            sentence = []
            labels = []

        else:
            lab = line.split()[1]
            if lab == 'O':
                labels.append(0)
            else:
                labels.append(1)
            sentence.append(line.split()[0])

    return zip(all_sents, all_labels)


def convert_to_date_duration_locations(s):
    """

    :param s:
    :return:
    """
    all_sents = []
    all_dates = []
    all_durations = []

    sentence = []
    dates = []
    durations = []
    tok_count = 0

    for line in s.split('\n'):
        if line == '':
            # #print("sentence:" + ' '.join(sentence))
            # #print("labels:" + str(labels))
            all_sents.append(' '.join(sentence))
            all_dates.append(dates)
            all_durations.append(durations)
            sentence = []
            dates = []
            durations = []
            tok_count = 0

        else:
            lab = line.split()[1]
            if lab in ["B-DATE", "I-DATE"]:
                dates.append(tok_count)
            elif lab in ["B-DURATION", "I-DURATION"]:
                durations.append(tok_count)

            sentence.append(line.split()[0])
            tok_count += 1

    return zip(all_sents, all_dates, all_durations)

def convert_to_date_duration_locations2(s):
    """
    Convert the seq2seq input format to Date/Dur SVM input format: Sentence\t[[list if phrase indexes]]\t[[list of labels]]
    :param s:
    :return:
    """
    all_sents = []
    all_idx = []
    all_labs = []
    all_patients = []

    sentence = []
    idxs = []
    labels = []
    patient = ''
    tok_count = 0

    for line in s.split('\n'):

        if line == '':
            # #print("sentence:" + ' '.join(sentence))
            # #print("labels:" + str(labels))
            all_sents.append(' '.join(sentence))
            all_patients.append(patient)

            # create groups of consecutive phrases
            idx_groups, lab_groups = get_phrase_groups_with_labels(zip(idxs, labels))
            all_idx.append(idx_groups)
            all_labs.append(lab_groups)

            sentence = []
            idxs = []
            labels = []
            patient = ''
            tok_count = 0

        else:
            lab = line.split()[1]
            patient = line.split()[2]
            if lab in ["B-DATE", "I-DATE", "B-DURATION", "I-DURATION"]:
                idxs.append(tok_count)

            if lab in ["B-DATE", "I-DATE"]:
                labels.append('DATE')
            elif lab in ["B-DURATION", "I-DURATION"]:
                labels.append('DURATION')

            sentence.append(line.split()[0])
            tok_count += 1

    # add last line to file
    all_sents.append(' '.join(sentence))
    all_patients.append(patient)
    # create groups of consecutive phrases
    idx_groups, lab_groups = get_phrase_groups_with_labels(zip(idxs, labels))
    all_idx.append(idx_groups)
    all_labs.append(lab_groups)

    return zip(all_sents, all_idx, all_labs, all_patients)


def get_max_length(sentences, tokenizer):
    """

    :param sentences:
    :param tokenizer:
    :return:
    """
    max_len = 0

    # For every sentence...
    for sent in sentences:
        # Tokenize the text and add `[CLS]` and `[SEP]` tokens.
        input_ids = tokenizer.encode(sent, add_special_tokens=True)

        # Update the maximum sentence length.
        max_len = max(max_len, len(input_ids))

    return max_len


def bert_text_preparation(sentences, tokenizer):
    """Preparing the input for BERT

    Takes a_bert string argument and performs
    pre-processing like adding special tokens,
    tokenization, tokens to ids, and tokens to
    segment ids. All tokens are mapped to seg-
    ment id = 1.

    Args:
        text (str): Text to be converted
        tokenizer_bert (obj): Tokenizer object
            to convert text into BERT-re-
            adable tokens and ids

    Returns:
        list: List of BERT-readable tokens
        obj: Torch tensor with token ids
        obj: Torch tensor segment ids
        obj: Torch tensor attention mask
        :param tokenizer:
        :param sentences:


    """
    #print("Number of input sentences: " + str(len(sentences)))
    # Get maximum length of sentences
    max_length = get_max_length(sentences, tokenizer)

    indexed_tensor = []
    attention_tensor = []
    tokenized_text = []
    segments_tensor = []

    # For every sentence...
    for sent in sentences:
        encoded_dict = tokenizer.encode_plus(
            sent,  # Sentence to encode.
            add_special_tokens=True,  # Add '[CLS]' and '[SEP]'
            max_length=max_length,  # Pad & truncate all sentences.
            pad_to_max_length=True,
            return_attention_mask=True,  # Construct attn. masks.
            return_tensors='pt',  # Return pytorch tensors.
        )

        # Add the encoded sentence to the list.
        indexed_tensor.append(encoded_dict['input_ids'])
        attention_tensor.append(encoded_dict['attention_mask'])
        segments_tensor.append(torch.tensor([[1] * encoded_dict['input_ids'].size()[1]]))
        tokenized_text.append(tokenizer.tokenize(tokenizer.decode(encoded_dict['input_ids'].tolist()[0])))

    # encoded_dict = tokenizer_bert(
    #    sentences.tolist(),  # Sentence to encode.
    #    add_special_tokens=True,  # Add '[CLS]' and '[SEP]'
    #    max_length=max_length,  # Pad & truncate all sentences.
    #    pad_to_max_length=True,
    #    return_attention_mask=True,  # Construct attn. masks.
    #    return_tensors='pt',  # Return pytorch tensors.
    # )
    # encoded_dict.update({'labels': torch.tensor(labels)})

    # #print("Returning the following encoded_dict with size: " + str(len(encoded_dict['input_ids'])))

    return tokenized_text, indexed_tensor, segments_tensor, attention_tensor
    # return encoded_dict


def get_phrase_groups(bert_indexes):
    groups = []
    for k, g in groupby(enumerate(bert_indexes), lambda x: x[0] - x[1]):
        groups.append(list(map(itemgetter(1), g)))
    return groups


def get_phrase_groups_with_labels(bert_indexes_with_labels):
    tuple_groups = []
    idx_groups = []
    lab_groups = []

    for k, g in groupby(enumerate(bert_indexes_with_labels), lambda x: x[0] - x[1][0]):
        tuple_groups.append(list(map(itemgetter(1), g)))

    for m in tuple_groups:
        idx_groups.append([x[0] for x in m])
        lab_groups.append(m[0][1])

    return idx_groups, lab_groups


def pull_date_dur_embeddings(model_sents, orig_sents, model_embedings, orig_duration_idxs, orig_date_idxs,
                             filter=False, merge=False):
    my_text = []
    my_embeddings = []
    my_labels = []

    if len(model_sents) == len(orig_sents) == len(model_embedings) == len(orig_duration_idxs) == len(orig_date_idxs):
        this_data = zip(model_sents, model_embedings, orig_sents, orig_date_idxs, orig_duration_idxs)
    else:
        #print("WARNING: number of this_model and original sentences does not match.")
        exit(1)

    # loop through each sentence
    for i, model_s, model_e, orig_s, orig_s_dates, orig_s_durations in zip(count(), model_sents, model_embedings,
                                                                           orig_sents, orig_date_idxs,
                                                                           orig_duration_idxs):
        # #print("FOR EACH SENTENCE:")
        # Map to BERT tokenization
        tokens_a = orig_s.split()
        tokens_b = model_s
        # #print(tokens_a)
        # #print(tokens_b)
        a2b, b2a = tokenizations.get_alignments(tokens_a, tokens_b)
        # #print(a2b)

        # define tokens to remove:
        to_remove = []
        if filter:
            to_remove = ["at", "of", "the", "a", "on", "which", "this", "then", "that", ".", "/", "-", ":", ";", ",",
                         "#", "&"]

        # get list of converted DATE and DURATION indices for this sentence
        if orig_s_durations:
            # #print("Found DURATION")
            # #print(orig_s_durations)
            my_durs = list(numpy.concatenate([a2b[j] for j in orig_s_durations]))
            # my_durs now contains a single list of indexes related to BERT tokens.
            # process my_durs to extract the embeddings and add data to final lists
            # break my_durs into a list of index lists, one list per phrase (based on consecutive indicies)
            my_dur_phrases = get_phrase_groups(my_durs)

            for phrase in my_dur_phrases:
                # process each token in the phrase.
                this_phrase_text = []
                full_phrase_length = len(phrase)
                sum_embedding = 0  ## sum all of the embeddings for this phrase, then calc average after loop
                # phrase length counter for filtered phrases
                filt_length = 0
                for k in phrase:  ## k is the BERT index for this token in the phrase
                    # #print("K: "+str(k))
                    # #print(model_s[k])
                    # #print(model_tokens[i][k] not in to_remove)
                    # #print(not (re.match("[0-9]*", model_tokens[i][k])))

                    if filter and model_s[k] not in to_remove and not re.match("[0-9]*", model_s[k]).group(0):
                        # #print("Filter is TRUE")
                        filt_length = filt_length + 1
                        if not merge:
                            my_text.append(model_s[k])
                            my_embeddings.append(model_e[k])
                            my_labels.append("DURATION")
                        else:
                            # #print("this should print")
                            this_phrase_text.append(model_s[k])
                            sum_embedding = sum_embedding + model_e[k]

                    elif not filter:  ## else include all the tokens
                        # #print("this should NOT print")
                        if not merge:
                            my_text.append(model_s[k])
                            my_embeddings.append(model_e[k])
                            my_labels.append("DURATION")
                        else:
                            this_phrase_text.append(model_s[k])
                            sum_embedding = sum_embedding + model_e[k]

                # if merging phrase tokens, then append to the global tracking variables
                div_length = filt_length if filter else full_phrase_length
                if merge and div_length > 0:  ## if div_length is zero then the full phrase was removed so don't add anything.
                    #print("Filt_length:" + str(filt_length))
                    #print("Full lenth: " + str(full_phrase_length))
                    my_text.append(" ".join(this_phrase_text))
                    my_embeddings.append(sum_embedding / div_length)
                    my_labels.append("DURATION")

        if orig_s_dates:
            # #print("Found DATE")
            # #print(orig_s_dates)
            my_dates = list(numpy.concatenate([a2b[j] for j in orig_s_dates]))
            # my_dates now contains a single list of indexes related to BERT tokens.
            # process my_dates to extract the embeddings and add data to final lists
            # break my_dates into a list of index lists, one list per phrase (based on consecutive indicies)
            my_date_phrases = get_phrase_groups(my_dates)

            for phrase in my_date_phrases:
                # process each token in the phrase.
                this_phrase_text = []
                full_phrase_length = len(phrase)
                sum_embedding = 0  ## sum all of the embeddings for this phrase, then calc average after loop
                # phrase length counter for filtered phrases
                filt_length = 0
                for k in phrase:  ## k is the BERT index for this token in the phrase
                    # #print("K: " + str(k))
                    # #print(model_s[k])
                    # #print(model_tokens[i][k] not in to_remove)
                    # #print(not (re.match("[0-9]*", model_tokens[i][k])))

                    if filter and model_s[k] not in to_remove and not re.match("[0-9]*", model_s[k]).group(0):
                        filt_length = filt_length + 1
                        if not merge:
                            my_text.append(model_s[k])
                            my_embeddings.append(model_e[k])
                            my_labels.append("DATE")
                        else:
                            this_phrase_text.append(model_s[k])
                            sum_embedding = sum_embedding + model_e[k]

                    elif not filter:  ## else include all the tokens
                        if not merge:
                            my_text.append(model_s[k])
                            my_embeddings.append(model_e[k])
                            my_labels.append("DATE")
                        else:
                            this_phrase_text.append(model_s[k])
                            sum_embedding = sum_embedding + model_e[k]

                # if merging phrase tokens, then append to the global tracking variables
                div_length = filt_length if filter else full_phrase_length
                if merge and div_length > 0:  ## if div_length is zero then the full phrase was removed so don't add anything.
                    #print("Filt_length:" + str(filt_length))
                    #print("Full lenth: " + str(full_phrase_length))
                    my_text.append(" ".join(this_phrase_text))
                    my_embeddings.append(sum_embedding / div_length)
                    my_labels.append("DATE")

    # in end we want to append text, embedding, label

    #print("My Tokens:")
    #print(my_text)
    #print(my_labels)
    # #print(my_embeddings)

    return my_text, my_embeddings, my_labels

def pull_date_dur_embeddings2(model_sents, orig_sents, model_embedings, orig_duration_idxs, orig_date_idxs,
                             filter=False, merge=False):
    my_text = []
    my_embeddings = []
    my_labels = []

    if len(model_sents) == len(orig_sents) == len(model_embedings) == len(orig_duration_idxs) == len(orig_date_idxs):
        this_data = zip(model_sents, model_embedings, orig_sents, orig_date_idxs, orig_duration_idxs)
    else:
        #print("WARNING: number of this_model and original sentences does not match.")
        exit(1)

    # loop through each sentence
    for i, model_s, model_e, orig_s, orig_s_dates, orig_s_durations in zip(count(), model_sents, model_embedings,
                                                                           orig_sents, orig_date_idxs,
                                                                           orig_duration_idxs):
        # #print("FOR EACH SENTENCE:")
        # Map to BERT tokenization
        tokens_a = orig_s.split()
        tokens_b = model_s
        # #print(tokens_a)
        # #print(tokens_b)
        a2b, b2a = tokenizations.get_alignments(tokens_a, tokens_b)
        # #print(a2b)

        # define tokens to remove:
        to_remove = []
        if filter:
            to_remove = ["at", "of", "the", "a", "on", "which", "this", "then", "that", ".", "/", "-", ":", ";", ",",
                         "#", "&"]

        # get list of converted DATE and DURATION indices for this sentence
        if orig_s_durations:
            my_durs = list(numpy.concatenate([a2b[j] for j in orig_s_durations]))
            # my_durs now contains a single list of indexes related to BERT tokens.
            # process my_durs to extract the embeddings and add data to final lists
            # break my_durs into a list of index lists, one list per phrase (based on consecutive indicies)
            my_dur_phrases = get_phrase_groups(my_durs)

            for phrase in my_dur_phrases:
                # process each token in the phrase.
                this_phrase_text = []
                full_phrase_length = len(phrase)
                sum_embedding = 0  ## sum all of the embeddings for this phrase, then calc average after loop
                # phrase length counter for filtered phrases
                filt_length = 0
                for k in phrase:  ## k is the BERT index for this token in the phrase
                    # #print("K: "+str(k))
                    # #print(model_s[k])
                    # #print(model_tokens[i][k] not in to_remove)
                    # #print(not (re.match("[0-9]*", model_tokens[i][k])))

                    if filter and model_s[k] not in to_remove and not re.match("[0-9]*", model_s[k]).group(0):
                        # #print("Filter is TRUE")
                        filt_length = filt_length + 1
                        if not merge:
                            my_text.append(model_s[k])
                            my_embeddings.append(model_e[k])
                            my_labels.append("DURATION")
                        else:
                            # #print("this should print")
                            this_phrase_text.append(model_s[k])
                            sum_embedding = sum_embedding + model_e[k]

                    elif not filter:  ## else include all the tokens
                        # #print("this should NOT print")
                        if not merge:
                            my_text.append(model_s[k])
                            my_embeddings.append(model_e[k])
                            my_labels.append("DURATION")
                        else:
                            this_phrase_text.append(model_s[k])
                            sum_embedding = sum_embedding + model_e[k]

                # if merging phrase tokens, then append to the global tracking variables
                div_length = filt_length if filter else full_phrase_length
                if merge and div_length > 0:  ## if div_length is zero then the full phrase was removed so don't add anything.
                    #print("Filt_length:" + str(filt_length))
                    #print("Full lenth: " + str(full_phrase_length))
                    my_text.append(" ".join(this_phrase_text))
                    my_embeddings.append(sum_embedding / div_length)
                    my_labels.append("DURATION")

        if orig_s_dates:
            # #print("Found DATE")
            # #print(orig_s_dates)
            my_dates = list(numpy.concatenate([a2b[j] for j in orig_s_dates]))
            # my_dates now contains a single list of indexes related to BERT tokens.
            # process my_dates to extract the embeddings and add data to final lists
            # break my_dates into a list of index lists, one list per phrase (based on consecutive indicies)
            my_date_phrases = get_phrase_groups(my_dates)

            for phrase in my_date_phrases:
                # process each token in the phrase.
                this_phrase_text = []
                full_phrase_length = len(phrase)
                sum_embedding = 0  ## sum all of the embeddings for this phrase, then calc average after loop
                # phrase length counter for filtered phrases
                filt_length = 0
                for k in phrase:  ## k is the BERT index for this token in the phrase
                    # #print("K: " + str(k))
                    # #print(model_s[k])
                    # #print(model_tokens[i][k] not in to_remove)
                    # #print(not (re.match("[0-9]*", model_tokens[i][k])))

                    if filter and model_s[k] not in to_remove and not re.match("[0-9]*", model_s[k]).group(0):
                        filt_length = filt_length + 1
                        if not merge:
                            my_text.append(model_s[k])
                            my_embeddings.append(model_e[k])
                            my_labels.append("DATE")
                        else:
                            this_phrase_text.append(model_s[k])
                            sum_embedding = sum_embedding + model_e[k]

                    elif not filter:  ## else include all the tokens
                        if not merge:
                            my_text.append(model_s[k])
                            my_embeddings.append(model_e[k])
                            my_labels.append("DATE")
                        else:
                            this_phrase_text.append(model_s[k])
                            sum_embedding = sum_embedding + model_e[k]

                # if merging phrase tokens, then append to the global tracking variables
                div_length = filt_length if filter else full_phrase_length
                if merge and div_length > 0:  ## if div_length is zero then the full phrase was removed so don't add anything.
                    #print("Filt_length:" + str(filt_length))
                    #print("Full lenth: " + str(full_phrase_length))
                    my_text.append(" ".join(this_phrase_text))
                    my_embeddings.append(sum_embedding / div_length)
                    my_labels.append("DATE")

    # in end we want to append text, embedding, label

    #print("My Tokens:")
    #print(my_text)
    #print(my_labels)
    # #print(my_embeddings)

    return my_text, my_embeddings, my_labels




def prep_for_svm(filename, model, tokenizer, fold=5, for_eval=True, saveas='', has_labels=True):
    f = open(filename)
    lines = f.readlines()
    f.close()

    texts = [l.strip().split('\t')[0] for l in lines]
    date_idxs = [eval(l.strip().split('\t')[1]) for l in lines]
    duration_idxs = [eval(l.strip().split('\t')[2]) for l in lines]

    # Convert corpus to embedding space
    tokenized_text, tokens_tensor, segments_tensors, attention_tensors = bert_text_preparation(
        texts, tokenizer)
    sentence_token_embeddings = get_bert_embeddings(tokens_tensor, segments_tensors, model)

    if saveas:
        joblib.dump(tokenized_text, "tokenized_text_" + saveas + ".pkl")
        joblib.dump(tokens_tensor, "tokens_tensor_" + saveas + ".pkl")
        joblib.dump(segments_tensors, "segments_tensors_" + saveas + ".pkl")
        joblib.dump(attention_tensors, "attention_tensors_" + saveas + ".pkl")
        joblib.dump(sentence_token_embeddings, "sentence_token_embeddings_" + saveas + ".pkl")

    # Merge the BERT word pieces << need to add option for different merging strategies>>
    merged_tokens, merged_embeddings = merge_word_pieces(tokenized_text, sentence_token_embeddings)

    ## Summarize embeddings per token or phrase for just the DATE and DURATION phrases.
    my_tokens, my_embeddings, my_labels = pull_date_dur_embeddings(merged_tokens, texts, merged_embeddings,
                                                                   duration_idxs, date_idxs,
                                                                   filter=True, merge=True)

    ## Format for ScyPi SVM learn
    X = torch.stack(my_embeddings).numpy()
    y = numpy.array([1 if x == 'DATE' else 0 for x in my_labels])  ## DATE = 1, DURATION = 0

    if for_eval:
        ## Stratify into train and test
        skf = StratifiedKFold(n_splits=fold, random_state=42, shuffle=True)
        skf.get_n_splits(X, y)
    else:
        skf = ''

    return X, y, skf





def concat_last_4(token_embeddings):
    """Combine embeddings to get one vector per token

    Args:
        token_embeddings (obj): Torch tensor size [n_tokens][m_layers][i_hidden_states]

    Returns:
        list: List of list of floats of size
            [n_tokens, n_embedding_dimensions]
            containing embeddings for each token

    """
    # concatenate the last 4 layers:
    # Stores the token vectors, with shape [n_tokens x (4 x i_hidden_states)]
    token_vecs_cat = []

    # For each token in the sentence...
    for token in token_embeddings:
        # `token` is a_bert [m_layers x i_hidden_states] tensor

        # Concatenate the vectors (that is, append them together) from the last
        # four layers.
        # Each layer vector is 768 values, so `cat_vec` is length 3,072.
        cat_vec = torch.cat((token[-1], token[-2], token[-3], token[-4]), dim=0)

        # Use `cat_vec` to represent `token`.
        token_vecs_cat.append(cat_vec)

    return token_vecs_cat

def summarizeEmbeddingAvg(bert_sent, sent_embeddings, this_coords, this_filter, this_merge):

    to_remove = []
    if this_filter:
        to_remove = ["at", "of", "the", "a", "on", "which", "this", "then", "that", "to", ".", "/", "-", ":", ";", ",",
                     "#", "&"]

    sum_embedding = 0  ## sum all of the embeddings for this phrase, then calc average after loop

    # phrase length counter for filtered phrases
    filt_length = 0
    full_phrase_length = len(bert_sent[this_coords[0]:this_coords[1]+1])

    embedding_list = []
    start_coord = max(0,this_coords[0])
    end_coord = min(this_coords[1]+1, len(bert_sent))

    ## k is the BERT index for this token in the phrase
    ## for each BERT token in the phrase filter out or extract the embedding
    for k in range(start_coord, end_coord):
        if this_filter and bert_sent[k] not in to_remove: #and not re.match("[0-9]*", bert_sent[k]).group(0):

            filt_length = filt_length + 1
            if this_merge:
                sum_embedding = sum_embedding + sent_embeddings[k]
            else:
                embedding_list.append(sent_embeddings[k])

        elif not this_filter:  ## else if self.filter is False then include all the tokens
            if this_merge:
                sum_embedding = sum_embedding + sent_embeddings[k]
            else:
                embedding_list.append(sent_embeddings[k])

    # if merging phrase tokens, then append to the global tracking variables
    div_length = filt_length if this_filter else full_phrase_length
    if this_merge and div_length > 0:  ## if div_length is zero then the full phrase was removed so don't add anything.
        embedding_list.append(sum_embedding / div_length)
    else:
        embedding_list.append('')

    if len(embedding_list) == 1:
        return embedding_list[0]
    else:
        return embedding_list


def summarizeEmbeddingAvgDisconnected(bert_sent, sent_embeddings, this_tokens, this_filter, this_merge):

    to_remove = []
    if this_filter:
        to_remove = ["at", "of", "the", "a", "on", "which", "this", "then", "that", "to", ".", "/", "-", ":", ";", ",",
                     "#", "&"]

    sum_embedding = torch.tensor(0)  ## sum all of the embeddings for this phrase, then calc average after loop

    # phrase length counter for filtered phrases
    filt_length = 0
    full_phrase_length = len(this_tokens)

    embedding_list = []

    ## k is the BERT index for this token in the phrase
    ## for each BERT token in the phrase filter out or extract the embedding
    for k in this_tokens:

        if this_filter and bert_sent[k] not in to_remove: #and not re.match("[0-9]*", bert_sent[k]).group(0):

            filt_length = filt_length + 1
            if this_merge:
                sum_embedding = sum_embedding + sent_embeddings[k]
            else:
                embedding_list.append(sent_embeddings[k])

        elif not this_filter:  ## else if self.filter is False then include all the tokens
            if this_merge:
                sum_embedding = sum_embedding + sent_embeddings[k]
            else:
                embedding_list.append(sent_embeddings[k])

    # if merging phrase tokens, then append to the global tracking variables
    div_length = filt_length if this_filter else full_phrase_length
    if this_merge and div_length > 0:  ## if div_length is zero then the full phrase was removed so don't add anything.
        embedding_list.append(sum_embedding / div_length)
    else:
        embedding_list.append('')

    if len(embedding_list) == 1:
        return embedding_list[0]
    else:
        return embedding_list

def getEmbeddingMtxDisconnected(bert_sent, sent_embeddings, token_idx_list, this_filter):
    """Extracts token embeddings for a list of tokens

    Args:
        bert_sent: sentence text tokenized by BERT
        sent_embeddings: BERT token embeddings
        token_idx_list: list of bert token indexes
        this_filter: TRUE or FALSE depending on if stop words and punctuation should be removed.

    Returns:
        list: List of torch tensors for phrase.

    """
    to_remove = []
    if this_filter:
        ##print("filtering...")
        to_remove = ["at", "of", "the", "a", "on", "which", "this", "then", "that", "to", ".", "/", "-", ":", ";", ",",
                     "#", "&"]

    embedding_list = []

    ## k is the BERT index for this token in the phrase
    ## for each BERT token in the phrase filter out or extract the embedding
    ##print("getting matrix for tokens: " + str(token_idx_list))
    for k in token_idx_list:

        if this_filter and bert_sent[k] not in to_remove: #and not re.match("[0-9]*", bert_sent[k]).group(0):
            embedding_list.append(sent_embeddings[k])

        elif not this_filter:  ## else if self.filter is False then include all the tokens
            ##print(bert_sent[k])
            embedding_list.append(sent_embeddings[k])

    return embedding_list

def padMtx(vec_list, pad_to):
    """Adds or crops a list of torch tensors to pad_tp length.

    Args:
        vec_list: list of torch tensors
        pad_to: integer with pad length.

    Returns:
        list: List of torch tensors with length set to pad_to.

    """
    ##print("length of incoming list: " + str(vec_list))
    ##print("padding: " + str(pad_to))

    if len(vec_list) < pad_to:
        to_add = pad_to - len(vec_list)
        dim = vec_list[0].size()[0]
        #print("Adding padding: " + str(to_add) + " With dim: " + str(dim))

        for m in list(range(0, to_add)):
            vec_list.extend([torch.zeros(dim, dtype=int)])
            ##print("For m=" + str(m) + " vec list length = " + str(len(vec_list)) + " vec content: " + str(vec_list))
        return vec_list
    elif len(vec_list) > pad_to:
        ##print("removing padding")
        to_rm = (len(vec_list) - pad_to)*-1
        #print("removing padding: " + str(to_rm))
        return vec_list[0:pad_to]
    else:
        #print("returning as-is")
        return vec_list



def get_bert_embeddings(tokens_tensor, segments_tensors, model):
    """Get embeddings from an embedding model_bert

    Args:
        tokens_tensor (obj): Torch tensor size [n_tokens]
            with token ids for each token in text
        segments_tensors (obj): Torch tensor size [n_tokens]
            with segment ids for each token in text
        model (obj): Embedding model_bert to generate embeddings
            from token and segment ids

    Returns:
        list: List of list of floats of size
            [n_tokens, n_embedding_dimensions]
            containing embeddings for each token

    """
    list_token_embeddings = []
    #print(tokens_tensor.size())

    for t, s in zip(tokens_tensor, segments_tensors):
        # Gradient calculation id disabled
        # Model is in inference mode
        with torch.no_grad():
            outputs = model(t, s)
            # Removing the first hidden state
            # The first state is the input state
            hidden_states = outputs[2][1:]

        # Reformat the embedding matrix
        token_embeddings = torch.stack(hidden_states, dim=0)  # Concatenate the tensors for all layers. We use
        # `stack` here to create a_bert new dimension in the tensor.
        token_embeddings = torch.squeeze(token_embeddings, dim=1)  # Remove dimension 1, the "batches".
        token_embeddings = token_embeddings.permute(1, 0, 2)  # Swap dimensions 0 and 1.

        list_token_embeddings.append(concat_last_4(token_embeddings))

    return list_token_embeddings


def merge_word_pieces(tokenized_text, sentence_token_embeddings, uselast=True):
    """Merge word pieces back together and keep only the last word piece embedding for the entire word.

    Args:
        tokenized_text (list): A list of tokenized sentences
        sentence_token_embeddings (list): A list of of list of Torch tensors that are word embeddings for the tokenized sentences
        uselast (boolean):

    Returns:
        merged_tokenized_text: A list of tokenized sentences with the hash tokens merged
        merged_sentence_token_embeddings: a_bert list of of list of tensors that are word embeddings for each token
    """
    merged_tokenized_text = []
    merged_sentence_token_embeddings = []

    # #print("My tokens:")
    # #print(tokenized_text_bert)

    for sent, embed in zip(tokenized_text, sentence_token_embeddings):
        merged_text_tmp = []
        merged_embeddings_tmp = []

        prev_text = sent[0]
        prev_embed = embed[0]
        for index, (t, s) in enumerate(zip(sent, embed)):
            if index > 0:
                if t.startswith("##"):
                    prev_text = prev_text + t
                    prev_embed = s
                else:
                    merged_text_tmp.append(prev_text)
                    merged_embeddings_tmp.append(prev_embed)
                    prev_text = t
                    prev_embed = s

        # add the last token in, which will never have a_bert hash mark
        merged_text_tmp.append(t)
        merged_embeddings_tmp.append(s)

        # add the full merged sentence and embedding to the main list
        merged_tokenized_text.append(merged_text_tmp)
        merged_sentence_token_embeddings.append(merged_embeddings_tmp)

    return merged_tokenized_text, merged_sentence_token_embeddings

def merge_label_pieces(orig_sentences, tokenized_texts, tokenized_labels):
    """Merge label pieces from the seq2seq prediction back together so we can test on the token level and not broken up dates.

    Args:
        orig_sentences (list): A list of sentences tokenized by white space
        tokenized_texts (list): A list of of list of BERT tokenized sentences
        tokenized_labels (list): A list of labels that matches the BERT tokenized text **before** converted to tensors

    Returns:
        converted_labels: A list of labels merged to match the whitespace tokenized sentences.
    """
    #print(len(orig_sentences))
    #print(len(tokenized_texts))
    #print("Length of tokenized_labels: " + str(len(tokenized_labels)))
    ##print("Tokenized_labels: " + str(tokenized_labels))

    index_conversion = []

    for sent, tok in zip(orig_sentences, tokenized_texts):
        a2b, b2a = tokenizations.get_alignments(sent, tok)
        index_conversion.append(a2b)

    ##print("Length of converted indexes: " + str(len(index_conversion)))
    #there are 22 sentences
    #each sentence is a list of lists where each sub list is a lsit of
    # token ids that map to that lists position in the true sentence
    converted_labels = []

    for sent_idx, sent in enumerate(index_conversion):
        ##print("sent_idx: "+str(sent_idx))
        ##print("sent"+str(sent))

        merged_sent_labels = []

        for tok_idx, tok in enumerate(sent):
            ##print("tok_idx: "+str(tok_idx))
            ##print("tok: "+str(tok))
            ##print(tokenized_labels[sent_idx])
            ##print(len(tokenized_labels[sent_idx]))
            labs = [tokenized_labels[sent_idx][m] for m in tok]

            if len(set(labs)) > 1:
                this_set = list(set(labs))  # get unique values
                if 'O' in this_set: this_set.remove('O')  # remove O and PAD
                if 'PAD' in this_set: this_set.remove('PAD')
                if this_set:  # if the set is not empty, find the max, else assign as O
                    this_set_count = [labs.count(x) for x in this_set]
                    lab2add = this_set[this_set_count.index(max(this_set_count))]
                    merged_sent_labels.append(lab2add)
                else:
                    merged_sent_labels.append('O')
            else:
                merged_sent_labels.append(labs[0])

        converted_labels.append(merged_sent_labels)

    return converted_labels

def writeAnnFile(filename, sentences, labels):
    """Flatten sentences and labels and write out a .ann formatted file.

    Args:
        filename (String): The path and name of the file to write results to.
        sentences (list): A list of lists of tokenized sentences
        labels (list): A list of labels that matches the input sentence tokenization.

    Returns:
        writes out a .ann formatted file using the specified input filename
    """
    labels_flat = np.concatenate(labels, axis=0)
    sents_flat = np.concatenate(sentences, axis=0)

    f = open(filename+".ann", "w")
    c = open(filename+".tsv", "w")

    if len(sents_flat) == len(labels_flat):
        timex_count = 1
        for i, lab in enumerate(labels_flat):
            ##print("i="+str(i))
            ##print(lab)
            ##print(sents_flat[i])
            if lab not in ['O', 'PAD']:
                f.write("T" + str(timex_count) + "\t" + lab + " " + str(i) + " " + str(i + 1) + "\t" + sents_flat[i] + "\n")
                c.write("T" + str(timex_count) + "\t" + lab + "\t" + str(i) + "\t" + str(i + 1) + "\t" + sents_flat[i] + "\n")
                timex_count = timex_count + 1

    f.close()
    c.close()

def merge_phrase_pieces(labeled_tokens):
    """Merge tokens in same phrase from the seq2seq prediction back together so we can test on the phrase level and not broken up phrases.

    Args:
        labeled_tokens (dataframe): A dataframe containing all the labeled tokens in a document.

    Returns:
        converted_phrases: A dataframe of tokens merged to contain the whole phrase.
    """

    #print("Length of df: " + str(len(labeled_tokens)))
    #["id", "label", "start", "end", "text"]

    id = 1
    phrase_list = []
    current_phrase = pd.Series()
    current_label_list = []

    for i, row in labeled_tokens.iterrows():
        if not current_phrase.empty:
            ## if we have a current phrase test to see if this row is part of it.
            if (current_phrase['end']) == row['start']:
                ##print("the phrase continues")
                current_phrase['end'] = row['end']
                current_phrase['text'] = current_phrase['text'] + ' ' + row['text']
                current_label_list.append(row['label'])
            else:
                ##print("the phrase ended")
                ## submit current phrase to phrase_df
                ## first resolve the label issue
                fdist = dict(zip(*numpy.unique(current_label_list, return_counts=True)))
                current_phrase['label'] = list(fdist)[-1]

                phrase_list.append(current_phrase)
                current_phrase = row
                current_phrase['id'] = id
                id = id + 1
                current_label_list = []
                current_label_list.append(current_phrase['label'])

        else:
            current_phrase = row
            current_phrase['id'] = id
            id = id+1
            current_label_list.append(current_phrase['label'])

    phrase_df = pd.DataFrame(phrase_list)



    return phrase_df




def tokenize_and_preserve_labels(sentence, text_labels, tokenizer):
    tokenized_sentence = []
    labels = []

    for word, label in zip(sentence, text_labels):
        # Tokenize the word and count # of subwords the word is broken into
        tokenized_word = tokenizer.tokenize(word)
        n_subwords = len(tokenized_word)

        # Add the tokenized word to the final tokenized word list
        tokenized_sentence.extend(tokenized_word)

        # Add the same label to the new list of labels `n_subwords` times
        labels.extend([label] * n_subwords)

    return tokenized_sentence, labels


def tokenize_words(sentence, tokenizer):
    tokenized_sentence = []

    for word in sentence:
        # Tokenize the word and count # of subwords the word is broken into
        tokenized_word = tokenizer.tokenize(word)

        # Add the tokenized word to the final tokenized word list
        tokenized_sentence.extend(tokenized_word)

    return tokenized_sentence


def load_bert(filepath):
    """
    Initializes and loads the BERT pre-trained model tokenizer.
    :param filepath: The path and file name of the pretrained BERT model to use.
    :return mod: Returns the pre-trained BERT model.
    :return tok: Returns a tokenizer object.
    """

    tok = BertTokenizer.from_pretrained(filepath, do_lower_case=True)
    mod = BertForTokenClassification.from_pretrained(
        filepath,
        output_attentions=True,
        output_hidden_states=True,
        local_files_only=True
    )

    return mod, tok


def seq2seq_text_prep(test_sentences, tokenizer, tag2idx, max_length, test_labels=""):
    """
        Loads seq2seq data from files with 1 sentence per line and possible labels.  Tokenizes
        the text and returns labels if present.
        :param max_length:
        :param filepath: The path and file name to the data.
        :return sents: Returns tokenized sentences for seq2seq prediction or training.
        :return labs: Returns labels for training use.
    """

    if test_labels:
        # Tokenize and format into 2 lists of lists.
        test_tokenized_texts_and_labels = [tokenize_and_preserve_labels(sent, labs, tokenizer)
                                           for sent, labs in zip(test_sentences, test_labels)]

        test_tokenized_texts = [token_label_pair[0] for token_label_pair in test_tokenized_texts_and_labels]
        test_labels = [token_label_pair[1] for token_label_pair in test_tokenized_texts_and_labels]

        test_labels = torch.tensor(pad_sequences([[tag2idx.get(l) for l in lab] for lab in test_labels],
                                                 maxlen=max_length, value=tag2idx["PAD"], padding="post",
                                                 dtype="long", truncating="post"))
    else:
        test_tokenized_texts = [tokenize_words(sent, tokenizer) for sent in test_sentences]

    # Pad sentences
    test_inputs = torch.tensor(
        pad_sequences([tokenizer.convert_tokens_to_ids(txt) for txt in test_tokenized_texts],
                      maxlen=max_length, dtype="long", value=0.0,
                      truncating="post", padding="post"))

    # create attention masks
    test_masks = torch.tensor([[float(i != 0.0) for i in ii] for ii in test_inputs])

    return test_tokenized_texts, test_inputs, test_masks, test_labels

def mergeLenient(gold, pred):
    """
        Merges predicted results and gold results using lenient span matching.
        :param gold: the gold data frame
        :param pred: the predicted data frame of results.
        :return df: a pandas dataframe with matched predicted data.
    """

    ## Input dataframe structure: "id", "label", "start", "end", "text", "context", "coords"
    #df = pd.DataFrame(columns=["gold_id", "gold_label", "gold_start", "gold_end", "gold_text", "gold_context", "gold_coords",
    #                           "pred_id", "pred_label", "pred_start", "pred_end", "pred_text", "pred_context", "pred_coords", "pred_used"])
    df = []
    ## Add flag column to predicted
    pred["used"] = 0
    blank_row = ["na","na","na","na","na","na","na"]

    ## Loop through gold one item at a time.  for each item, loop through all of predicted.
    # If a predicted is matched, then add gold and pred to new df, then mark pred as used.
    for g,grow in gold.iterrows():
        gused = False
        for p, prow in pred.iterrows():
            if prow.start <= grow.start <= prow.end:
                ## we have overlap
                ##print("Pred Start: " + str(prow.start) + "\nPred End: " + str(prow.end) + "\nGold Start: " +
                #     str(grow.start) + "\nPredicted Row: " + str(prow) + "\n Gold Row: " + str(grow))
                gused = True
                pred["used"][p] = 1

                df.append(grow.tolist() + prow.tolist())
            elif prow.start <= grow.end <= prow.end:
                ##print("Pred Start: " + str(prow.start) + "\nPred End: " + str(prow.end) + "\nGold End: " +
                #      str(grow.end) + "\nPredicted Row: " + str(prow) + "\n Gold Row: " + str(grow))
                ## we have overlap
                gused = True
                pred["used"][p] = 1
                df.append(grow.tolist() + prow.tolist())

        if not gused:
            #add grow to df with blank pred row
            df.append(grow.tolist() + blank_row)

    pred_not_used = pred[pred["used"] == 0]

    for n,pnu in pred_not_used.iterrows():
        df.append(blank_row + pnu.tolist())

    #pd.DataFrame(df, columns=['Name', 'Age'])

    return pd.DataFrame(df, columns=["id_x", "label_x", "start_x", "end_x", "text_x", "context_x", "coords_x",
                                     "id_y", "label_y", "start_y", "end_y", "text_y", "context_y", "coords_y", "used_y"])

    #print("done merging!")

def format_attention(attention, layers=None, heads=None):
    if layers:
        attention = [attention[layer_index] for layer_index in layers]
    squeezed = []
    for layer_attention in attention:
        # 1 x num_heads x seq_len x seq_len
        if len(layer_attention.shape) != 4:
            raise ValueError(
                "The attention tensor does not have the correct number of dimensions. Make sure you set "
                "output_attentions=True when initializing your model.")
        layer_attention = layer_attention.squeeze(0)
        if heads:
            layer_attention = layer_attention[heads]
        squeezed.append(layer_attention)
    # num_layers x num_heads x seq_len x seq_len
    return torch.stack(squeezed)


def num_attention_layers(attention):
    return len(attention)


def num_attention_heads(attention):
    return attention[0][0].size(0)


def create_cnn_model(num_filters, kernel_size1, kernel_size2, pool_size, stride, dropout, input_dim):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Conv1D(num_filters, kernel_size1, activation='relu', input_shape = input_dim, padding="valid"))
    model.add(tf.keras.layers.MaxPooling1D(pool_size=pool_size, strides=stride, padding="valid"))
    model.add(tf.keras.layers.Conv1D(num_filters, kernel_size2, activation='relu'))
    model.add(tf.keras.layers.Dropout(rate=dropout))
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(10, activation='relu'))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model





