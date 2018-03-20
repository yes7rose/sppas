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

    src.anndata.aio.praat.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Praat - Doing phonetic with computers, is a GPL tool developed by:

        | Paul Boersma and David Weenink
        | Phonetic Sciences, University of Amsterdam
        | Spuistraat 210
        | 1012VT Amsterdam
        | The Netherlands

    See: http://www.fon.hum.uva.nl/praat/

"""
import codecs
import re

import sppas
from sppas.src.utils.makeunicode import u
from sppas.src.utils.makeunicode import sppasUnicode

from ..anndataexc import AioError
from ..anndataexc import AioEncodingError
from ..anndataexc import AioEmptyTierError
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioLineFormatError
from ..anndataexc import AioNoTiersError
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag
from ..annotation import sppasAnnotation

from .aioutils import fill_gaps, merge_overlapping_annotations
from .basetrs import sppasBaseIO

# ----------------------------------------------------------------------------


class sppasBasePraat(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Base class for readers and writers of Praat files.

    Try first to open the file with the default sppas encoding, then UTF-16.

    """
    @staticmethod
    def make_point(midpoint, radius=0.0005):
        """ In Praat, the localization is a time value, so a float.

        :param midpoint: (float, str, int) a time value (in seconds).
        :param radius: (float): vagueness (in seconds)
        :returns: (sppasPoint)

        """
        try:
            midpoint = float(midpoint)
            radius = float(radius)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")

        return sppasPoint(midpoint, radius)

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new Praat instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = False
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = True
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = False
        self._accept_overlaps = False

    # -----------------------------------------------------------------

    @staticmethod
    def _parse_int(line, line_number=0):
        """ Parse an integer value from a line of a Praat formatted file.

        >>> sppasBasePraat._parse_int("intervals: size = 23")
        >>> 23

        :param line: (str) The line to parse and get value
        :param line_number: (int) Number of the given line
        :returns: (int)

        """
        try:
            line = line.strip()
            val = line[line.rfind(' ') + 1:]
            return int(val)
        except:
            raise AioLineFormatError(line_number, line)

    # ----------------------------------------------------------------------------

    @staticmethod
    def _parse_float(line, line_number=0):
        """ Parse a floating point value from a line of a Praat formatted file.

        >>> sppasBasePraat._parse_float("xmin = 11.9485310906")
        >>> 11.9485310906

        :param line: (str) The line to parse and get value
        :param line_number: (int) Number of the given line
        :returns: (float)

        """
        try:
            line = line.strip()
            val = line[line.rfind(' ') + 1:]
            return float(val)
        except:
            raise AioLineFormatError(line_number, line)

    # ----------------------------------------------------------------------------

    @staticmethod
    def _parse_string(text):
        """ Parse a text from one or more lines of a Praat formatted file.

        :param text: (str or list of str)
        :returns: (str)

        """
        text = text.strip()

        if text.endswith('"'):
            text = text[:-1]

        if re.match('^[A-Za-z ]+=[ ]?', text):
            text = text[text.find('=') + 1:]

        text = text.strip()
        if text.startswith('"'):
            text = text[1:]

        # praat double quotes.
        return text.replace('""', '"')

    # -----------------------------------------------------------------------

    @staticmethod
    def load(filename, file_encoding=sppas.encoding):
        """ Load a file into lines.

        :param filename: (str)
        :param file_encoding: (str)
        :returns: list of lines (str)

        """
        try:
            with codecs.open(filename, 'r', file_encoding) as fp:
                lines = fp.readlines()
                fp.close()
        except IOError:
            raise AioError(filename)
        except UnicodeDecodeError:
            raise AioEncodingError(filename, "", file_encoding)

        return lines

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_header(file_class, xmin, xmax):
        """ Serialize the header of a Praat file.

        :param file_class: (str) Objects class in this file
        :param xmin: (float) Start time
        :param xmax: (float) End time
        :returns: (str)

        """
        header = 'File type = "ooTextFile"\n'
        header += 'Object class = "{:s}"\n'.format(file_class)
        header += '\n'
        header += 'xmin = {:.18}\n'.format(xmin)
        header += 'xmax = {:.18}\n'.format(xmax)
        return header

    # -----------------------------------------------------------------

    @staticmethod
    def _serialize_label_text(label):
        """ Convert a label into a string. """

        if label is None:
            text = ""
        elif label.get_best() is None:
            text = ""
        elif label.get_best().is_empty():
            text = ""
        else:
            text = label.get_best().get_content()

        if '"' in text:
            text = re.sub('([^"])["]([^"])', '\\1""\\2', text)
            text = re.sub('([^"])["]([^"])', '\\1""\\2',
                          text)  # miss occurrences if 2 " are separated by only 1 character
            text = re.sub('([^"])["]$', '\\1""', text)  # miss occurrences if " is at the end of the label!
            text = re.sub('^["]([^"])', '""\\1', text)  # miss occurrences if " is at the beginning of the label
            text = re.sub('^""$', '""""', text)
            text = re.sub('^"$', '""', text)

        return '\t\ttext = "{:s}"\n'.format(text)

    # -----------------------------------------------------------------

    @staticmethod
    def _serialize_label_value(label):
        """ Convert a label with a numerical value into a string. """

        if label is None:
            return None
        if label.get_best() is None:
            return None
        if label.get_best().is_empty():
            return None
        text = label.get_best().get_content()
        return "\t\tvalue = {:s}\n".format(text)

# ----------------------------------------------------------------------------


class sppasTextGrid(sppasBasePraat):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS TextGrid reader and writer.

    TextGrid supports multiple tiers in a file.
    TextGrid does not support empty files (file with no tiers).
    TextGrid does not support alternatives labels nor locations. Only the ones
    with the best score are saved.
    TextGrid does not support controlled vocabularies.
    TextGrid does not support hierarchy.
    TextGrid does not support metadata.
    TextGrid does not support media assignment.
    TextGrid supports points and intervals. It does not support disjoint intervals.
    TextGrid does not support alternative tags (here called "text").
    TextGrid does not support radius.

    Both "short TextGrid" and "long TextGrid" file formats are supported.

    """
    @staticmethod
    def _detect(fp):
        line = fp.readline()
        file_type = sppasBasePraat._parse_string(line)
        line = fp.readline()
        object_class = sppasBasePraat._parse_string(line)
        return file_type == "ooTextFile" and object_class == "TextGrid"

    @staticmethod
    def detect(filename):
        """ Check whether a file is of TextGrid format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        detected = False
        try:
            with codecs.open(filename, 'r', sppas.encoding) as fp:
                detected = sppasTextGrid._detect(fp)
                fp.close()
        except UnicodeDecodeError:
            with codecs.open(filename, 'r', 'UTF-16') as fp:
                detected = sppasTextGrid._detect(fp)
                fp.close()
        except IOError:
            pass

        return detected

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasTextGrid instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBasePraat.__init__(self, name)
        self.default_extension = "TextGrid"

        self._accept_point = True
        self._accept_interval = True

    # -----------------------------------------------------------------

    def read(self, filename):
        """ Read a TextGrid file.

        :param filename: is the input file name, ending by ".TextGrid"

        """
        # get the content of the file

        try:
            lines = sppasBasePraat.load(filename, sppas.encoding)
        except AioEncodingError:
            try:
                lines = sppasBasePraat.load(filename, "UTF-16")
            except AioEncodingError:
                raise AioEncodingError(filename, "", sppas.encoding+"/UTF-16")

        # parse the header of the file

        # if the size isn't named, it is a short TextGrid file
        is_long = not lines[6].strip().isdigit()

        last_line = len(lines) - 1
        cur_line = 7
        if is_long is True:
            # Ignore the line 'item []:'
            cur_line += 1

        # parse all lines of the file

        while cur_line < last_line:
            # Ignore the line: 'item [1]:'
            # with the tier number between the brackets
            if is_long is True:
                cur_line += 1
            cur_line = self._parse_tier(lines, cur_line, is_long)

    # -----------------------------------------------------------------

    def _parse_tier(self, lines, start_line, is_long):
        """ Parse a tier from the content of a TextGrid file.

        :param lines: the contents of the file.
        :param start_line: index in lines when the tier content starts.
        :param is_long: A boolean which is false if the TextGrid is in short form.
        :returns: (int) Number of lines of this tier

        """
        # Parse the header of the tier

        tier_type = sppasBasePraat._parse_string(lines[start_line])
        tier_name = sppasBasePraat._parse_string(lines[start_line+1])
        tier_size = sppasBasePraat._parse_int(lines[start_line+4])
        tier = self.create_tier(tier_name)

        if tier_type == "IntervalTier":
            is_interval = True
        elif tier_type == "TextTier":
            is_interval = False
        else:
            raise AioLineFormatError(start_line+1, lines[start_line])

        # Parse the content of the tier
        start_line += 5
        end = len(lines) - 1

        while start_line < end and len(tier) < tier_size:
            # Ignore the line: 'intervals [1]:'
            # with the interval number between the brackets
            if is_long is True:
                start_line += 1
            ann, start_line = self._parse_annotation(lines, start_line, is_interval)
            tier.add(ann)

        return start_line

    # -----------------------------------------------------------------

    @staticmethod
    def _parse_annotation(lines, start_line, is_interval):
        """ Read an annotation from an IntervalTier in the contents of a TextGrid file.

        :param lines: (list) the contents of the file.
        :param start_line: (int) index in lines when the tier content starts.
        :param is_interval: (bool)
        :returns: number of lines for this annotation in the file

        """
        # Parse the localization
        localization, start_line = \
            sppasTextGrid._parse_localization(lines, start_line, is_interval)
        if start_line >= len(lines):
            raise AioLineFormatError(start_line - 1, lines[-1])

        # Parse the tag
        tag, start_line = \
            sppasTextGrid._parse_text(lines, start_line)

        ann = sppasAnnotation(sppasLocation(localization),
                              sppasLabel(tag))

        return ann, start_line

    # -----------------------------------------------------------------

    @staticmethod
    def _parse_localization(lines, start_line, is_interval):
        """ Parse the localization (point or interval).  """

        midpoint = sppasBasePraat._parse_float(lines[start_line], start_line+1)
        start_line += 1
        if is_interval is True:
            if start_line >= len(lines):
                raise AioLineFormatError(start_line-1, lines[-1])
            end = sppasBasePraat._parse_float(lines[start_line], start_line+1)
            start_line += 1
            localization = sppasInterval(sppasBasePraat.make_point(midpoint),
                                         sppasBasePraat.make_point(end))
        else:
            localization = sppasBasePraat.make_point(midpoint)

        return localization, start_line

    # -----------------------------------------------------------------

    @staticmethod
    def _parse_text(lines, start_line):
        """ Parse the text entry. Returns a sppasTag(). """

        line = lines[start_line].strip()
        text = sppasBasePraat._parse_string(line)
        start_line += 1

        # text can be on several lines.
        while line.endswith('"') is False:

            line = lines[start_line].strip()
            text += " "
            text += sppasBasePraat._parse_string(line)
            start_line += 1

            if start_line >= len(lines):
                raise AioLineFormatError(start_line-1, lines[-1])

        return sppasTag(text), start_line

    # ------------------------------------------------------------------------
    # Writer
    # ------------------------------------------------------------------------

    def write(self, filename):
        """ Write a TextGrid file.

        :param filename: (str)

        """
        if self.is_empty():
            raise AioNoTiersError("TextGrid")

        min_time_point = self.get_min_loc()
        max_time_point = self.get_max_loc()
        if min_time_point is None or max_time_point is None:
            # only empty tiers in the transcription
            raise AioNoTiersError("TextGrid")

        with codecs.open(filename, 'w', sppas.encoding, buffering=8096) as fp:

            # Write the header
            fp.write(sppasTextGrid._serialize_textgrid_header(min_time_point.get_midpoint(),
                                                              max_time_point.get_midpoint(),
                                                              len(self)))

            # Write each tier
            for i, tier in enumerate(self):

                if tier.is_disjoint() is True:
                    continue

                # Write the header of the tier
                try:
                    fp.write(sppasTextGrid._serialize_tier_header(tier, i+1))
                except:
                    fp.close()
                    raise

                # intervals of annotations must be in a continuum
                if tier.is_interval() is True:
                    tier = fill_gaps(tier, min_time_point, max_time_point)
                    tier = merge_overlapping_annotations(tier)

                # Write annotations of the tier
                is_point = tier.is_point()
                for a, annotation in enumerate(tier):
                    if is_point is True:
                        fp.write(sppasTextGrid._serialize_point_annotation(annotation, a+1))
                    else:
                        fp.write(sppasTextGrid._serialize_interval_annotation(annotation, a+1))

            fp.close()

    # ------------------------------------------------------------------------

    @staticmethod
    def _serialize_textgrid_header(xmin, xmax, size):
        """ Create a string with the header of the textgrid. """

        content = sppasBasePraat._serialize_header("TextGrid", xmin, xmax)
        content += 'tiers? <exists>\n'
        content += 'size = {:d}\n'.format(size)
        content += 'item []:\n'
        return content

    # ------------------------------------------------------------------------

    @staticmethod
    def _serialize_tier_header(tier, tier_number):
        """ Create the string with the header for a new tier. """

        if len(tier) == 0:
            raise AioEmptyTierError("TextGrid", tier.get_name())

        content = '\titem [{:d}]:\n'.format(tier_number)
        content += '\t\tclass = "{:s}"\n'.format('IntervalTier' if tier.is_interval() else 'TextTier')
        content += '\t\tname = "{:s}"\n'.format(tier.get_name())
        content += '\t\txmin = {:.18}\n'.format(tier.get_first_point().get_midpoint())
        content += '\t\txmax = {:.18}\n'.format(tier.get_last_point().get_midpoint())
        content += '\t\tintervals: size = {:d}\n'.format(len(tier))
        return content

    # ------------------------------------------------------------------------

    @staticmethod
    def _serialize_interval_annotation(annotation, number):
        """ Converts an annotation consisting of intervals to the TextGrid format.

        A time value can be written with a maximum of 18 digits, like in Praat.

        :param annotation: (sppasAnnotation)
        :param number: (int) the index of the annotation in the tier + 1.
        :returns: (unicode)

        """
        content = '\t\tintervals [{:d}]:\n'.format(number)
        content += '\t\txmin = {:.18}\n'.format(annotation.get_lowest_localization().get_midpoint())
        content += '\t\txmax = {:.18}\n'.format(annotation.get_highest_localization().get_midpoint())
        content += sppasBasePraat._serialize_label_text(annotation.get_label())
        return u(content)

    # ------------------------------------------------------------------------

    @staticmethod
    def _serialize_point_annotation(annotation, number):
        """ Converts an annotation consisting of points to the TextGrid format.

        :param annotation: (sppasAnnotation)
        :param number: (int) the index of the annotation in the tier + 1.
        :returns: (unicode)

        """
        text = sppasBasePraat._serialize_label_text(annotation.get_label())
        text = text.replace("text =", "mark =")

        content = '\t\tpoints [{:d}]:\n'.format(number)
        content += '\t\ttime = {:.18}\n'.format(annotation.get_lowest_localization().get_midpoint())
        content += text
        return u(content)

# ----------------------------------------------------------------------------


class sppasBaseNumericalTier(sppasBasePraat):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS PitchTier, IntensityTier, etc reader and writer.

    Support of Praat file formats with only one tier of numerical values like
    pitch, intensity, etc.

    """
    def __init__(self, name=None):
        """ Initialize a new sppasBaseNumericalTier instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBasePraat.__init__(self, name)

        self._accept_multi_tiers = False
        self._accept_no_tiers = False
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = False
        self._accept_overlaps = False

# ----------------------------------------------------------------------------


class sppasPitchTier(sppasBaseNumericalTier):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS PitchTier reader and writer.

    """
    @staticmethod
    def detect(filename):
        """ Check whether a file is of PitchTier format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', sppas.encoding) as it:
                file_type = sppasBasePraat._parse_string(it)
                object_class = sppasBasePraat._parse_string(it)
                return file_type == "ooTextFile" and object_class == "PitchTier"
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasPitchTier instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseNumericalTier.__init__(self, name)

# ----------------------------------------------------------------------------


class sppasIntensityTier(sppasPitchTier):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS IntensityTier reader and writer.

    """
    @staticmethod
    def detect(filename):
        """ Check whether a file is of IntensityTier format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', sppas.encoding) as it:
                file_type = sppasBasePraat._parse_string(it)
                object_class = sppasBasePraat._parse_string(it)
                return file_type == "ooTextFile" and object_class == "IntensityTier"
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasIntensityTier instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseNumericalTier.__init__(self, name)

    # -----------------------------------------------------------------

