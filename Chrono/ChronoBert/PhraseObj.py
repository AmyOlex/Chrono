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

import numpy
from Chrono.ChronoBert import bert_utils as utils
import torch


class PhraseObj(object):

    # init method or constructor
    def __init__(self, text, bert_sent, coords, char_coords, a2b, sent_embeddings, attentions, context_window,
                 gold_label, filt):
        #print("\n-----\nNew Entry\n-----\n")
        self.text = text
        self.coords = coords
        self.char_coords = char_coords
        self.gold_label = gold_label
        self.predicted_label = ''
        self.filter = filt
        self.merge = True
        self.context_window = context_window
        self.value = ''
        self.mod = ''
        self.useSelfContext = True

        self.coords_bert = self.setCoordsBert(a2b)
        self.bert_length = self.coords_bert[-1] - self.coords_bert[0]
        self.bert_text = bert_sent[self.coords_bert[0]:self.coords_bert[-1] + 1]
        self.summarized_embedding = utils.summarizeEmbeddingAvg(bert_sent, sent_embeddings, self.coords_bert,
                                                                self.filter,
                                                                self.merge)  ## will want to develop different options for this method

        self.context_text_before, self.context_coords_before, self.summarized_context_embedding_before = \
            self.getContextEmbeddings(bert_sent, sent_embeddings, context_window * -1)
        #print("Context Coords BEFORE: " + str(self.context_coords_before))

        self.context_text_after, self.context_coords_after, self.summarized_context_embedding_after = \
            self.getContextEmbeddings(bert_sent, sent_embeddings, context_window)
        #print("Context Coords AFTER: " + str(self.context_coords_after))

        self.attendsToTokens, self.attendsToText, self.summarized_attention_embedding = self.getAttentionEmbedding(
            attentions, bert_sent, sent_embeddings, context_window)

        ## Need to add methods to obtain the following for CNN:
        #print("\nGETTING PHRASE MATRIX\n")
        #print(self.coords_bert)
        #print(list(range(self.coords_bert[0],self.coords_bert[1]+1)))
        self.phrase_embedding_matrix = utils.getEmbeddingMtxDisconnected(bert_sent, sent_embeddings, list(range(self.coords_bert[0],self.coords_bert[1]+1)), self.filter)
        #print("\nGETTING BEFORE CONTEXT MATRIX\n")
        #print("Context Text BEFORE: " + str(self.context_text_before) + " Coords: " + str(self.context_coords_before))
        self.context_before_matrix = utils.getEmbeddingMtxDisconnected(bert_sent, sent_embeddings,
                                                                       list(range(self.context_coords_before[0],
                                                                                  self.context_coords_before[1]+1)), self.filter)
        #print("\nGETTING AFTER CONTEXT MATRIX\n")
        self.context_after_matrix = utils.getEmbeddingMtxDisconnected(bert_sent, sent_embeddings,
                                                                      list(range(self.context_coords_after[0],
                                                                                 self.context_coords_after[1]+1)), self.filter)

        attn_before = [i for i in self.attendsToTokens if i < self.coords_bert[0]]
        attn_after = [i for i in self.attendsToTokens if i > self.coords_bert[-1]]
        #print("ATTN Before: " + str(attn_before))
        #print("ATTN After: " + str(attn_after))

        #print("\nGETTING BEFORE ATTN MATRIX\n")
        self.attention_before_matrix = utils.getEmbeddingMtxDisconnected(bert_sent, sent_embeddings, attn_before, self.filter)
        #print("\nGETTING AFTER ATTN MATRIX\n")
        self.attention_after_matrix = utils.getEmbeddingMtxDisconnected(bert_sent, sent_embeddings, attn_after, self.filter)


    def getMtxFormattedPhrase(self, pad_to, include_context = False, include_attention = False):

        if include_context:
            print("\nReturning CONTEXT with phrase matrix")
            #print("Length of context before: " + str(len(self.context_before_matrix)))
            embed_mtx = self.context_before_matrix[:]
            embed_mtx.extend(self.phrase_embedding_matrix)
            embed_mtx.extend(self.context_after_matrix)
            pad_mtx = utils.padMtx(embed_mtx, pad_to)
            if(len(pad_mtx) != 15):
                print("ERROR")
                print("length of embed_mtx before padding: " + str(len(embed_mtx)))
                print("length of embed_mtx after padding: " + str(len(pad_mtx)))
            return torch.stack(pad_mtx).numpy()

        elif include_attention:
            #print("\nReturning ATTENTION with phrase matrix")
            #print("Length of attn before: " + str(len(self.attention_before_matrix)))
            embed_mtx = self.attention_before_matrix[:]
            embed_mtx.extend(self.phrase_embedding_matrix)
            embed_mtx.extend(self.attention_after_matrix)
            #print("length of embed_mtx: " + str(len(embed_mtx)))
            return torch.stack(utils.padMtx(embed_mtx, pad_to)).numpy()
        else:
            #print("\nReturning just phrase matrix")
            embed_mtx = utils.padMtx(self.phrase_embedding_matrix, pad_to)
            #print("Shape: " + str(len(embed_mtx)))
            return torch.stack(embed_mtx).numpy()



    ## if you want to do the context before you need to put a negative window.  After is a positive window.
    def getContextEmbeddings(self, bert_sent, sent_embeddings, context_window):
        #print("\nDefining context coords based on: " + str(self.coords_bert))
        if context_window < 0:
            #print("getting context before: Start: " + str(max(self.coords_bert[0] + context_window, 0)) + " End: " + str(
            #    self.coords_bert[0] - 1 ))
            contextCoords = (max(self.coords_bert[0] + context_window, 0), self.coords_bert[0] - 1)
        else:
            #print("getting context after: Start: " + str(self.coords_bert[1] + 1) + " End: " + str(min(self.coords_bert[1] + context_window, len(bert_sent))) )
            contextCoords = (self.coords_bert[1] + 1, min(self.coords_bert[1] + context_window, len(bert_sent)) )

        if (contextCoords[1] - contextCoords[0]) > 0:
            #print("getting context embedding...")
            context_embedding = utils.summarizeEmbeddingAvg(bert_sent, sent_embeddings, contextCoords, self.filter, self.merge)
            context_text = bert_sent[contextCoords[0]:contextCoords[1] + 1]
        elif context_window < 0:
            if self.useSelfContext:
                #print("using phrase embedding for context.")
                # set to phrase embedding
                contextCoords = self.coords_bert
                context_embedding = self.summarized_embedding
                context_text = bert_sent[contextCoords[0]:contextCoords[1] + 1]
            else: ##currently this is never executed
                # set to CLS token
                context_embedding = sent_embeddings[0]
                context_text = bert_sent[0]
        else:
            if self.useSelfContext:
                #print("using phrase embedding for context2.")
                # set to phrase embedding
                contextCoords = self.coords_bert
                context_embedding = self.summarized_embedding
                context_text = bert_sent[contextCoords[0]:contextCoords[1] + 1]
            else:  ##currently this is never executed.  I don't think it is coded correctly either.
                # set to SEP token
                context_embedding = sent_embeddings[-1]
                context_text = bert_sent[-1]

        return context_text, contextCoords, context_embedding

    def getAttentionEmbedding(self, attention, bert_sent, sent_embeddings, k):
        # Format Attentions
        formatted_attentions = utils.format_attention(attention,
                                                      layers=list(range(utils.num_attention_layers(attention))),
                                                      heads=list(range(utils.num_attention_heads(attention))))

        #### Summarizing attentions for phrases
        phrase_start = self.coords_bert[0]
        phrase_end = self.coords_bert[1] + 1

        #print("\nBert Sentence: " + str(bert_sent))
        #print("\nCurrent Phrase Start: " + str(phrase_start) + " End: " + str(phrase_end))
        #print("\nPhrase: " + str(bert_sent[phrase_start:phrase_end]))

        layer_attention = torch.tensor(0)

        for layer in range(0, utils.num_attention_layers(attention)):
            # print("\nLayer " + str(layer))
            head_attention = torch.tensor(0)

            for head in range(0, utils.num_attention_heads(attention)):

                phrase_attention = formatted_attentions[layer][head][phrase_start]
                for n in range(phrase_start + 1, phrase_end):
                    phrase_attention = torch.max(phrase_attention, formatted_attentions[layer][head][n])

                head_attention = head_attention + phrase_attention

            head_attention[phrase_start:phrase_end] = 0
            head_attention[0] = 0
            head_attention[bert_sent.index('[SEP]')] = 0
            if '.' in bert_sent:
                indices = [i for i, x in enumerate(bert_sent) if x == "."]
                head_attention[indices] = 0
            if ',' in bert_sent:
                indices = [i for i, x in enumerate(bert_sent) if x == ","]
                head_attention[indices] = 0
            # if '[PAD]' in bert_sent:
            #    indices = [i for i, x in enumerate(bert_sent) if x == '[PAD]']
            #    print(indices)
            #    head_attention[indices] = 0

            # print(head_attention)
            tmp = head_attention / sum(head_attention)

            layer_attention = layer_attention + tmp

        m = layer_attention / sum(layer_attention)
        token_attn = m.numpy() * 100
        attends_to = numpy.sort(numpy.flip(numpy.argsort(token_attn))[0:k])
        attends_to_text = [bert_sent[x] for x in attends_to]

        #print("\nAttends to token numbers: " + str(attends_to) + "  Which are tokens: " + str(attends_to_text))

        return attends_to, attends_to_text, utils.summarizeEmbeddingAvgDisconnected(bert_sent, sent_embeddings,
                                                                                    attends_to, self.filter, self.merge)

    def setCoordsBert(self, a2b):
        print(a2b)
        print(self.coords[0])
        print(self.coords[1])
        return a2b[self.coords[0]][0], a2b[self.coords[1]][-1]

    def setGoldLabel(self, lab):
        self.gold_label = lab

    def setPredictedLabel(self, lab):
        self.predicted_label = lab

    def getText(self):
        return self.text

    def getGoldLabel(self):
        return self.gold_label

    def getPredictedLabel(self):
        return self.predicted_label

    def getNumToks(self):
        return len(self.bert_text)

    def getSummarizedEmbedding(self, include_context, include_attention):
        if include_context and include_attention:
            return torch.cat([self.summarized_context_embedding_before, self.summarized_embedding,
                              self.summarized_context_embedding_after, self.summarized_attention_embedding], 0)
        elif include_context:
            return torch.cat([self.summarized_context_embedding_before, self.summarized_embedding,
                              self.summarized_context_embedding_after], 0)
        elif include_attention:
            return torch.cat([self.summarized_embedding,
                              self.summarized_attention_embedding], 0)
        else:
            return self.summarized_embedding

    def getAttendedTokens(self):
        return self.attendsToTokens

    def getAttendedText(self):
        return self.attendsToText

    def getStartCoord(self):
        return self.coords[0]

    def getEndCoord(self):
        return self.coords[1]

    def getStartCharCoord(self):
        return self.char_coords[0]

    def getEndCharCoord(self):
        return self.char_coords[1]

    def getBertStartCoord(self):
        return self.coords_bert[0]

    def getBertEndCoord(self):
        return self.coords_bert[1]

    def setValue(self, val):
        self.value = val

    def getValue(self):
        return self.value

    def setModifier(self, mod):
        self.mod = mod

    def getModifier(self):
        return self.mod

    ## Print i2b2 format
    def i2b2format(self, id, global_sentence_start_coord):
        # <TIMEX3 id="T0" start="18" end="26" text="10/17/95" type="DATE" val="1995-10-17" mod="NA" />
        return ("<TIMEX3 id=\"T" + str(id) + "\" start=\"" + str(
            self.getStartCharCoord() + global_sentence_start_coord + 1) + "\" end=\"" + str(
            self.getEndCharCoord() + global_sentence_start_coord + 1) + "\" text=\"" + str(
            ' '.join(self.text)) + "\" type=\"" + str(self.predicted_label) + "\" val=\"" + str(
            self.value) + "\" mod=\"" + str(self.mod) + "\" />\n")
