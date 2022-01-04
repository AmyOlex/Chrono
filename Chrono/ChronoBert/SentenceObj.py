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

import tokenizations
import torch
import numpy as np
from Chrono.ChronoBert import bert_utils as utils
from Chrono.ChronoBert import PhraseObj



class SentenceObj(object):

    # init method or constructor
    def __init__(self, text, sentence_num, global_sent_char_start_coord, global_sentence_start_coord, phrase_idxs,
                 max_length, bert_model, bert_tokenizer, context_window, gold_labels, filt):
        self.text = text
        self.sentence_num = sentence_num
        self.global_sent_char_start_coord = global_sent_char_start_coord
        self.global_sentence_start_coord = global_sentence_start_coord
        self.whitespace_tokenized_sentence, \
            self.bert_tokenized_sentence, \
            self.tokens_tensor, \
            self.segments_mask, \
            self.attention_mask, \
            self.idx_map_white2bert = self.tokenizeSentence(bert_tokenizer, max_length)
        self.bert_embeddings, self.bert_attentions = self.getSentEmbeddings(bert_model)
        self.datedur_phrases = self.extractPhrases(phrase_idxs, context_window, gold_labels, filt)

        self.max_phrase_length = self.calc_max_phrase_length()

    def tokenizeSentence(self, bert_tokenizer, max_length):
        #print("Tokenizing sentence: Max Sentence Length: " + str(max_length))
        local_whitespace_tokenized_sentence = self.text.split()
        local_bert_tokenized_sentence, local_tokens_tensor, local_segments_mask, local_attention_mask = \
            self.bert_text_prep(self.text, bert_tokenizer, max_length)

        a2b, b2a = tokenizations.get_alignments(local_whitespace_tokenized_sentence, local_bert_tokenized_sentence)
        local_idx_map_white2bert = a2b

        return local_whitespace_tokenized_sentence, local_bert_tokenized_sentence, local_tokens_tensor, \
            local_segments_mask, local_attention_mask, local_idx_map_white2bert

    def getSentEmbeddings(self, bert_model):

        with torch.no_grad():
            outputs = bert_model(self.tokens_tensor, self.segments_mask)
            # Removing the first hidden state
            # The first state is the input state
            hidden_states = outputs[2][1:]
            attentions = outputs[-1]

        # Reformat the embedding matrix
        token_embeddings = torch.stack(hidden_states, dim=0)  # Concatenate the tensors for all layers. We use
        # `stack` here to create a_bert new dimension in the tensor.
        token_embeddings = torch.squeeze(token_embeddings, dim=1)  # Remove dimension 1, the "batches".
        token_embeddings = token_embeddings.permute(1, 0, 2)  # Swap dimensions 0 and 1.

        local_bert_embeddings = utils.concat_last_4(token_embeddings)

        return local_bert_embeddings, attentions

    def extractPhrases(self, phrase_idxs, context_window, gold_labels, filt):
        ## input: [[2,3,4],[8,9]]
        ## input: ['DATE','DURATION'] or ''
        print("My phrase idxs: " + str(phrase_idxs) + " Type: " + str(type(phrase_idxs)))

        local_datedur_phrases = []
        if gold_labels:
            # get phrase groups with labels
            #print("Phrase idxs: " + str(phrase_idxs))
            #print("Gold Labels: " + str(gold_labels))
            #idxs, labs = utils.get_phrase_groups_with_labels(zip(phrase_idxs, gold_labels))
            #print("Type of phrase_idxs: " + str(type))
            for p, g in zip(phrase_idxs, gold_labels):
                #print("p is: " + str(p))
                #print("g is: " + str(g))

                phrase_start = p if isinstance(p, int) else p[0]  ## get first in list
                phrase_end = p if isinstance(p, int) else p[-1]  ## get last in list

                ptext = self.whitespace_tokenized_sentence[phrase_start:phrase_end + 1]
                #print("ptext: " + str(ptext))
                pcoords = (phrase_start, phrase_end)

                #now get character coords
                # sentence start to phrase_start, plus one character (for the missing space) is the char start:
                #print("-----PARSING PHRASE---------")
                #print("Sentence Fragment to START: " + str(' '.join(self.whitespace_tokenized_sentence[0:max(0,phrase_start)])))
                #print("Sentence Fragment to START LENGTH: " + str(len(' '.join(self.whitespace_tokenized_sentence[0:max(0,phrase_start)]) )))
                #print("Sentence Fragment to END: " + str(' '.join(self.whitespace_tokenized_sentence[0:max(0,phrase_end + 1)] )))
                #print("Sentence Fragment to END LENGTH: " + str(len(' '.join(self.whitespace_tokenized_sentence[0:max(0,phrase_end + 1)] ) ) ) )

                phrase_char_start = len(' '.join(self.whitespace_tokenized_sentence[0:max(0,phrase_start)]) ) + 1
                phrase_char_end = len(' '.join(self.whitespace_tokenized_sentence[0:max(0,phrase_end + 1)] ) )
                char_pcoords = (phrase_char_start, phrase_char_end)


                local_datedur_phrases.append(
                    PhraseObj.PhraseObj(ptext, self.bert_tokenized_sentence, pcoords, char_pcoords, self.idx_map_white2bert,
                                        self.bert_embeddings, self.bert_attentions, context_window, g, filt))
        else:
            for p in phrase_idxs:
                phrase_start = p if isinstance(p, int) else p[0]
                phrase_end = p if isinstance(p, int) else p[-1]
                ptext = self.whitespace_tokenized_sentence[phrase_start:phrase_end + 1]
                pcoords = (phrase_start, phrase_end)
                print("PROCESSING p: " + str(p))
                print("Phrase p start,end: " + str(phrase_start) + "," + str(phrase_end))
                print("self.text: " + str(self.text))
                print("self.whitespace_tokenized_sentence: " + str(self.whitespace_tokenized_sentence))
                print("Phrase text: " + str(ptext))
                # now get character coords
                # sentence start to phrase_start token, plus one character (for the missing space) is the char start:
                phrase_char_start = len(' '.join(self.whitespace_tokenized_sentence[0:max(0, phrase_start)])) + 1
                phrase_char_end = len(' '.join(self.whitespace_tokenized_sentence[0:max(0, phrase_end + 1)]))
                char_pcoords = (phrase_char_start, phrase_char_end)

                local_datedur_phrases.append(
                    PhraseObj.PhraseObj(text=ptext, bert_sent=self.bert_tokenized_sentence, coords=pcoords,
                                        char_coords=char_pcoords, a2b=self.idx_map_white2bert,
                                        sent_embeddings=self.bert_embeddings, attentions=self.bert_attentions,
                                        context_window=context_window, gold_label='', filt=filt))
        return local_datedur_phrases

    def getFlatListPhraseEmbeddings(self, phrase_types, include_context, include_attention):
        phrase_list = []
        gold_label_list = []
        for phrase in self.datedur_phrases:
            if phrase.getGoldLabel() in phrase_types:
                phrase_list.append(phrase.getSummarizedEmbedding(include_context, include_attention))
                gold_label_list.append(phrase.getGoldLabel())
        return phrase_list, gold_label_list

    def getMtxListPhraseEmbeddings(self, phrase_types, pad_to, include_context, include_attention):
        phrase_list = []
        gold_label_list = []
        for phrase in self.datedur_phrases:
            if phrase.getGoldLabel() in phrase_types:
                phrase_list.append(phrase.getMtxFormattedPhrase(pad_to, include_context, include_attention))  ## this should return a numpy 2d array
                gold_label_list.append(phrase.getGoldLabel())
        return phrase_list, gold_label_list

    def calc_max_phrase_length(self):
        max_len = 0
        for p in self.datedur_phrases:
            if p.bert_length > max_len:
                max_len = p.bert_length
        return max_len

    def getText(self):
        return self.text

    def getPhrases(self):
        return self.datedur_phrases

    def getMaxPhraseLength(self):
        return self.max_phrase_length

    def getSentIdx(self):
        return self.sentence_num

    def getWhiteTokSent(self):
        return self.whitespace_tokenized_sentence

    def getBertTokSent(self):
        return self.bert_tokenized_sentence

    def getBertEmbeddings(self):
        return self.bert_embeddings

    def getGlobalStartCoord(self):
        return self.global_sentence_start_coord

    def bert_text_prep(self, sentence, tokenizer, max_length):

        encoded_dict = tokenizer.encode_plus(sentence,
                                             add_special_tokens=True,  # Add '[CLS]' and '[SEP]'
                                             max_length=max_length,  # Pad & truncate all sentences.
                                             pad_to_max_length=True,
                                             return_attention_mask=True,  # Construct attn. masks.
                                             return_tensors='pt',  # Return pytorch tensors.
                                             )
        # Add the encoded sentence to the list.
        indexed_tensor = encoded_dict['input_ids']
        attention_mask = encoded_dict['attention_mask']
        segments_mask = torch.tensor([[1] * encoded_dict['input_ids'].size()[1]])
        tokenized_text = tokenizer.tokenize(tokenizer.decode(encoded_dict['input_ids'].tolist()[0]))

        return tokenized_text, indexed_tensor, segments_mask, attention_mask#, attention_tensor

    def SVMPredict(self, model_svm, include_context, include_attention, label_dict=''):
        for phrase in self.datedur_phrases:
            if phrase:
                #print("Including Context:")
                #print(phrase.getSummarizedEmbedding(include_context).shape)
                pred = model_svm.predict(np.reshape(phrase.getSummarizedEmbedding(include_context, include_attention).numpy(), (1,-1)))
                phrase.setPredictedLabel(label_dict[pred[0]])

    def CNNPredict(self, model_cnn, pad_to, include_context, include_attention, label_dict=''):
        for phrase in self.datedur_phrases:
            if phrase:
                #print("running CNN prediction")
                pred = model_cnn.predict(np.expand_dims(phrase.getMtxFormattedPhrase(pad_to, include_context, include_attention), 0)).tolist()[0]
                #print("\nPrediction is: " + str(pred) + "  With label: " + str(label_dict[ int(round(pred[0])) ]))
                phrase.setPredictedLabel( label_dict[ int(round(pred[0])) ] )

    def getContextWhiteSpace(self, start, end, window):
        return(' '.join(self.whitespace_tokenized_sentence[max(start-window, 0):min(end+window, len(self.whitespace_tokenized_sentence))]))

    def getContextBertTok(self, start, end, window):
        return (' '.join(self.bert_tokenized_sentence[
                         max(start - window, 0):min(end + window, len(self.bert_tokenized_sentence))]))

    def printANN(self, f, record_num):
        for phrase in self.datedur_phrases:
            new_record = ("T" + str(record_num) + "\t" + phrase.getPredictedLabel() + " " +
                          str(phrase.getStartCoord()+self.global_sentence_start_coord) + " " +
                          str(phrase.getEndCoord()+self.global_sentence_start_coord+1) + "\t" +
                          self.getContextWhiteSpace(phrase.getStartCoord(), phrase.getEndCoord(), 0) + "\t" +
                          self.getContextWhiteSpace(phrase.getStartCoord(), phrase.getEndCoord(), 3) + "\n")
            f.write(new_record)
            record_num = record_num+1
        return record_num

    def printTSV(self, f, record_num):
        for phrase in self.datedur_phrases:
            new_record = ("T" + str(record_num) + "\t" + phrase.getPredictedLabel() + "\t" +
                          str(phrase.getStartCoord()+self.global_sentence_start_coord) + "\t" +
                          str(phrase.getEndCoord()+self.global_sentence_start_coord+1) + "\t" +
                          self.getContextWhiteSpace(phrase.getStartCoord(), phrase.getEndCoord()+1, 0) + "\t" +
                          self.getContextWhiteSpace(phrase.getStartCoord(), phrase.getEndCoord()+1, 3) + "\t" +
                          str(phrase.getAttendedTokens()) + "\t" + str(phrase.getAttendedText()) + "\n")
            f.write(new_record)
            record_num = record_num+1
        return record_num

    def print_i2b2(self, f, record_num):
        for phrase in self.datedur_phrases:
            new_record = phrase.i2b2format(record_num, self.global_sent_char_start_coord)
            f.write(new_record)
            record_num = record_num+1
        return record_num


