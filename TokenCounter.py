# Copyright (c) 2018
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
import argparse
from pathlib import Path
from Chrono import utils, referenceToken


def count_total_tokens(filename, outfile):
    text, tokens, spans, tags, sents = utils.getWhitespaceTokens(str(filename))
    with outfile.open('w+') as f:
        f.write("Total number of tokens: " + str(len(tokens)) + "\n")


def count_temporal_tokens(filename, outfile):
    text, tokens, spans, tags, sents = utils.getWhitespaceTokens(str(filename))
    my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, span=spans, pos=tags, sent_boundaries=sents)
    chroList = utils.markTemporal(my_refToks)
    doctime = utils.getDocTime(str(filename) + ".dct")
    tempPhrases = utils.getTemporalPhrases(chroList, doctime)
    temptokens = 0
    with outfile.open('a+') as f:
        f.write("Temporal Phrases: " + str(len(tempPhrases)) + "\n")
        for p in tempPhrases:
            temptokens = temptokens + len(p.getText().split())
            f.write(p.getText() + "\n")
        f.write("Temporal Tokens: " + str(temptokens) + "\n")


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser(
        description='Parse a directory of files to count the number of tokens')
    parser.add_argument('-i', metavar='inputdir', type=str, help='path to the input directory.', required=True)

    args = parser.parse_args()
    utils.initialize(in_mode="SCATE")
    for root, dirs, files in utils.path_walk(Path(args.i), topdown=True):
        for f in files:
            if not any(ext in f.name for ext in [".dct",".ann",".xml",".csv"]):
                print("Processing: ", f)
                count_total_tokens(Path(f), Path("counts/" + f.name + ".count"))
                count_temporal_tokens(Path(f), Path("counts/" + f.name + ".count"))
    print("Completed couting tokens.")

