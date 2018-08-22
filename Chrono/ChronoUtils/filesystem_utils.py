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


def write_out(chrono_list, outfile, mode=["SCATE"]):

    if "SCATE" in mode:
        print("Printing SCATE: " + outfile + ".completed.xml")
        fout = open(outfile + ".completed.xml", "w")
        fout.write("<data>\n<annotations>\n")
        for c in chrono_list :
            fout.write(str(c.print_SCATE()))
        fout.write("\n</annotations>\n</data>")
        fout.close()

    if "ANN" in mode:
        print("Printing ANN: " + outfile + ".completed.ann")
        fout = open(outfile + ".completed.ann", "w")
        for c in chrono_list:
            fout.write(str(c.print_ANN()))
        fout.close()


def path_walk(top, topdown=False, followlinks=False):
    """
         See Python docs for os.walk, exact same behavior but it yields Path() instances instead
    """
    names = list(top.iterdir())

    dirs = (node for node in names if node.is_dir() is True)
    nondirs = (node for node in names if node.is_dir() is False)

    if topdown:
        yield top, dirs, nondirs

    for name in dirs:
        if followlinks or name.is_symlink() is False:
            for x in path_walk(name, topdown, followlinks):
                yield x

    if topdown is not True:
        yield top, dirs, nondirs