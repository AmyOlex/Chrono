from Chrono import utils
from Chrono import referenceToken
from Chrono import BuildEntities
from chronoML import NB_nltk_classifier as NBclass
from transformers import BertModel, BertTokenizer

raw_text, text, tokens, abs_text_spans, rel_text_spans, tags, sents, sent_text, sent_membership = utils.getWhitespaceTokens2("i2b2_train/1.xml.txt")

my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, abs_span=abs_text_spans, rel_span=rel_text_spans,
                                               pos=tags, sent_boundaries=sents, sent_membership=sent_membership)

chroList = utils.markTemporal(my_refToks, include_relative=True)

doctime = utils.getDocTime("i2b2_train/1.xml.txt", i2b2=True)

tempPhrases = utils.getTemporalPhrases(chroList, sent_text, doctime)

my_chronoentities = []
my_chrono_ID_counter = 1
classifier, feats, NB_input = NBclass.build_model("/Users/alolex/Desktop/CCTR_Git_Repos/Chrono/sample_files/Newswire-THYMEColon_train_Win5_data.csv", "/Users/alolex/Desktop/CCTR_Git_Repos/Chrono/sample_files/Newswire-THYMEColon_train_Win5_class.csv")
# load in BERT model
bert_model = BertModel.from_pretrained("/Users/alolex/Desktop/CCTR_Git_Repos/PycharmProjects/ChronoBERT/models/bert-base-uncased-local", output_hidden_states=True, use_cache=True, output_attentions=True)
bert_tokenizer = BertTokenizer.from_pretrained("/Users/alolex/Desktop/CCTR_Git_Repos/PycharmProjects/ChronoBERT/models/bert-base-uncased-local")

chrono_master_list, my_chrono_ID_counter, timex_phrases = BuildEntities.buildChronoList(tempPhrases,
                                                                                                my_chrono_ID_counter,
                                                                                                chroList,
                                                                                                (classifier, "NB"),
                                                                                                feats, bert_model,
                                                                                                bert_tokenizer, doctime)


