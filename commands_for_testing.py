from Chrono import utils
from Chrono import referenceToken
from Chrono import TimePhraseEntity

raw_text, text, tokens, spans, tags, sents, sent_text, sent_membership = utils.getWhitespaceTokens2("i2b2_train/1.xml.txt")

my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, span=spans, pos=tags, sent_boundaries=sents, sent_membership=sent_membership)

chroList = utils.markTemporal(my_refToks, include_relative=True)

doctime = utils.getDocTime("i2b2_train/1.xml.txt", i2b2=True)

tempPhrases = utils.getTemporalPhrases(chroList, sent_text, doctime)

