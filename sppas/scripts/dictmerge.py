#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    scripts.dictmerge.py
    ~~~~~~~~~~~~~~~~~~~~

    ... a script to merge dictionaries.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.resources.dictpron import DictPron

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to merge pronunciation dictionaries.")

parser.add_argument("-i",
                    metavar="file",
                    action='append',
                    required=True,
                    help='Input dictionary file name (as many as wanted)')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output dictionary file name')

parser.add_argument("--no_variant_numbers",
                    action='store_true',
                    help="Do not save the variant number")

parser.add_argument("--no_filled_brackets",
                    action='store_true',
                    help="Do not save with filled brackets")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
with_variant_nb = True
with_filled_brackets = True
if args.no_variant_numbers:
    with_variant_nb = False
if args.no_filled_brackets:
    with_filled_brackets = False
merge_dict = None

# ----------------------------------------------------------------------------

args = parser.parse_args()
for dict_file in args.i:

    if not args.quiet:
        print("Read input dictionary file: ")
    pron_dict = DictPron(dict_file, nodump=True)
    if not args.quiet:
        print(" [  OK  ]")
    if merge_dict is None:
        merge_dict = pron_dict
    else:
        for entry in pron_dict.get_keys():
            prons = pron_dict.get_pron(entry)
            for pron in prons.split(DictPron.VARIANTS_SEPARATOR):
                merge_dict.add_pron(entry, pron)

merge_dict.save_as_ascii(args.o, with_variant_nb, with_filled_brackets)