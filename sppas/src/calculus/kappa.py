#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: kappa.py
# ----------------------------------------------------------------------------

from __future__ import division
from geometry.distances import squared_euclidian as sq

# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

class Kappa:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Inter-observer variation estimation.

    Inter-observer variation can be measured in any situation in which
    two or more independent observers are evaluating the same thing.
    The Kappa statistic seems the most commonly used measure of inter-rater
    agreement in Computational Linguistics.

    Kappa is intended to give the reader a quantitative measure of the
    magnitude of agreement between observers.
    The calculation is based on the difference between how much agreement is
    actually present (“observed” agreement) compared to how much agreement
    would be expected to be present by chance alone (“expected” agreement).

    >>> p = [ (1.0,0.0) , (0.0,1.0) , (0.0,1.0) , (1.0,0.0) , (1.0,0.0) ]
    >>> q = [ (1.0,0.0) , (0.0,1.0) , (1.0,0.0) , (1.0,0.0) , (1.0,0.0) ]
    >>> kappa = Kappa(p,q)
    >>> print p, "is ok? (expect true):", kappa.check_vector(p)
    >>> print q, "is ok? (expect true):", kappa.check_vector(q)
    >>> print "Kappa value:",kappa.evaluate()

    """

    def __init__(self, p, q):
        """
        Create a Kappa instance with two lists of tuples p and q.

        Example: p=[ (1.0,0.0), (1.0,0.0), (0.8,0.2) ]

        @param p is a vector of tuples of float values
        @param q is a vector of tuples of float values

        """
        self.p = p
        self.q = q

    # -----------------------------------------------------------------------

    def sqv(self):
        """
        Estimates the Euclidian distance between two vectors.

        @param p is a vector of tuples of float values
        @param q is a vector of tuples of float values
        @return v

        """

        if len(self.p) != len(self.q):
            raise Exception('Both vectors p and q must have the same length (got respectively %d and %d).'%(len(self.p),len(self.q)))

        return sum([sq(x,y) for (x,y) in zip(self.p,self.q)])

    # -----------------------------------------------------------------------

    def sqm(self):
        """
        Estimates the Euclidian distance between two vectors.

        @return row and col

        """

        if len(self.p) != len(self.q):
            raise Exception('Both vectors p and q must have the same length (got respectively %d and %d).'%(len(self.p),len(self.q)))

        row = list()
        for x in self.p:
            row.append( sum( sq(x,y) for y in self.q) )

        col = list()
        for y in self.q:
            col.append( sum( sq(y,x) for x in self.p) )

        return row,col

    # -----------------------------------------------------------------------

    def check_vector(self, v):
        """
        Check if the vector is correct to be used.

        @param v is a vector of tuples of probabilities.

        """
        # Must contain data!
        if v is None or len(v)==0:
            return False

        for t in v:
            # Must contain tuples only.
            if not type(t) is tuple:
                return False
            # All tuples have the same size (more than 1).
            if len(t) != len(v[0]) or len(t) < 2:
                return False
            # Tuple values are probabilities.
            s = 0
            for p in t:
                if p<0.0 or p>1.0:
                    return False
                s += p
            if s != 1.0: return False


        return True

    # -----------------------------------------------------------------------

    def check(self):
        """
        Check if the given p and q vectors are correct to be used.

        @return boolean

        """
        return self.check_vector(self.p) and self.check_vector(self.q)

    # -----------------------------------------------------------------------

    def evaluate(self):
        """
        Estimates the Cohen's Kappa between two lists of tuples p and q.

        The tuple size corresponds to the number of categories, each value is
        the score assigned to each category for a given sample.

        @return float value

        """
        v = self.sqv() / float(len(self.p))
        row,col = self.sqm()
        if sum(row) != sum(col):
            raise Exception('Hum... error while estimating euclidian distances.')
        r = sum(row) / float(len(self.p)**2)
        if r == 0.:
            return 1.

        return 1.0 - v/r

    # -----------------------------------------------------------------------

# ----------------------------------------------------------------------------
