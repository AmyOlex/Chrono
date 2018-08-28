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


import Chrono.ChronoUtils.filesystem_utils
import Chrono.ChronoUtils.initialize_chrono
import Chrono.ChronoUtils.parse_text
from Chrono import referenceToken
import xml.etree.ElementTree as ET


def count_temporal_tokens(filename, outfile):
    text, tokens, spans, tags, sents = Chrono.ChronoUtils.parse_text.getWhitespaceTokens(str(filename))
    my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, span=spans, pos=tags, sent_boundaries=sents)
    chroList = Chrono.ChronoUtils.parse_text.markTemporal(my_refToks)
    doctime = Chrono.ChronoUtils.parse_text.getDocTime(str(filename) + ".dct")
    tempPhrases = Chrono.ChronoUtils.parse_text.getTemporalPhrases(chroList, doctime)
    with outfile.open('a+') as f:
        for p in tempPhrases:
            temptokens = len(p.getText().split())
            f.write(filename.name + "\t" + str(len(tokens)) + "\t" + p.getText() + "\t" + str(temptokens) + "\n")


def count_xml_tokens(filename, outfile):
    tree = ET.parse(str(filename))
    root = tree.getroot()
    temptokens = 0
    for item in root.findall('./annotations/entity'):
        temptokens = temptokens + 1

    with outfile.open('a+') as f:
        f.write(filename.name + "\t" + str(temptokens) + "\n")


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser(
        description='Parse a directory of files to count the number of tokens')
    parser.add_argument('-i', metavar='inputdir', type=str, help='path to the input directory.', required=True)
    parser.add_argument('-o', metavar='outputfile', type=str, help='path to the output file.', required=True)
    parser.add_argument('--xml', action='store_true')

    args = parser.parse_args()
    Chrono.ChronoUtils.initialize_chrono.initialize()

    skip_me = [".dct",".ann",".csv",".DS_Store"]

    outfile = Path(args.o)
    if args.xml:
        with outfile.open('w+') as f:
            f.write("File" + "\t" + "Entity Count" + "\n")
    else:
        with outfile.open('w+') as f:
            f.write("File" + "\t" + "Total" + "\t" + "Phrase" + "\t" + "Phrase Length" + "\n")

    for root, dirs, files in Chrono.ChronoUtils.filesystem_utils.path_walk(Path(args.i), topdown=True):
        for f in files:
            if args.xml:
                if not any(ext in f.name for ext in skip_me):
                    print("Processing: ", f)
                    count_xml_tokens(Path(f), outfile)
            else:
                skip_me.append(".xml")
                if not any(ext in f.name for ext in skip_me):
                    print("Processing: ", f)
                    count_temporal_tokens(Path(f), outfile)
    print("Completed couting tokens.")

