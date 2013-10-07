#!/usr/bin/env python
# encoding: utf-8
#
# AuthorDetector
# Copyright (C) 2013 Larroque Stephen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

## @package tfidf
#
# Computes the term frequency - inverse document frequency (TF-IDF) instead of the frequency in the 'freq' column

from authordetector.postprocessor.basepostprocessor import BasePostProcessor
from authordetector.postprocessor.augmentedtermfrequency import AugmentedTermFrequency
import pandas as pd
import numpy as np

## TFIDF
#
# Computes the term frequency - inverse document frequency (TF-IDF) instead of the frequency in the 'freq' column
# Note: we compute the augmented tf instead of raw tf, which means that we in fact compute the augmented tf-idf
class TFIDF(BasePostProcessor):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BasePostProcessor.__init__(self, config, parent, *args, **kwargs)

    # Computes the term frequency - inverse document frequency (TF-IDF) instead of the frequency in the 'freq' column
    # Note: we compute the augmented tf instead of raw tf, which means that we in fact compute the augmented tf-idf
    # @param Patterns The extracted patterns
    # @return dict A dict containing postprocessed Patterns with freq = tf-idf
    def process(self, Patterns=None, Debug=None, *args, **kwargs):

        Patterns = dict(Patterns) # Use this to make sure Patterns is a dictionary
        #if L_Patterns is not None: L_Patterns = dict(L_Patterns)

        # Precompute the inverse document frequencies
        idf = TFIDF.idf(Patterns)

        # For each patterns tables
        for attr, P in Patterns.iteritems():
            # Recompute the frequencies in one go + order by frequencies
            P = AugmentedTermFrequency.augmented_tf(P, nosort=True)

            # Filter idf so that we get only the ones that are in P (so P can have more ngrams than idf, but idf may only share ngrams with P - this is to ensure that when we multiply, fill_value will only fill for idf, but not for P which would completely foil the calculation)
            pidf = idf[idf.index.isin(P.index)]

            # Compute the augmented tf-idf
            P.ix[:,'freq'] = P.ix[:,'freq'].mul(pidf, fill_value=1)

            # Sort by frequency
            P = P.sort(['freq'], axis=0).ix[::-1] # sort by augmented term frequency and reorder by descending value

            # Update the Patterns table (because P is only local in the loop scope)
            Patterns[attr] = P

        # Return the resulting variables (in a dict of vars)
        return {'Patterns': Patterns}

    # Compute the irverse document frequency, from all the Patterns tables (both learning and detection if possible)
    # @param Patterns All the patterns tables
    # @return idf A vector (pandas Series) of idf scores
    @staticmethod
    def idf(Patterns, *args, **kwargs):
        idf = pd.Series()
        for attr, P in Patterns.iteritems():
            p = pd.Series(1, index=P.index)
            idf = idf.add(p, fill_value=0)

        #if L_Patterns is not None:
        #    for attr, LP in L_Patterns.iteritems():
        #        p = pd.Series(1, index=LP.index)
        #        idf = idf.add(p, fill_value=0)

        p = p.astype('float64')

        nbdocs = len(Patterns)
        #if L_Patterns is not None:
        #    nbdocs += len(L_Patterns)

        idf = np.log(nbdocs / idf)

        return idf
