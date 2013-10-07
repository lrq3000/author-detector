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

## @package augmentedtermfrequency
#
# Computes the augmented term frequency instead of the frequency in the 'freq' column

from authordetector.postprocessor.basepostprocessor import BasePostProcessor

## AugmentedTermFrequency
#
# Computes the augmented term frequency instead of the frequency in the 'freq' column
class AugmentedTermFrequency(BasePostProcessor):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BasePostProcessor.__init__(self, config, parent, *args, **kwargs)

    # Computes the augmented term frequency instead of the frequency in the 'freq' column
    # @param Patterns The extracted patterns
    # @return dict A dict containing postprocessed Patterns with column freq = augmented tf, ordered by freq
    def process(self, Patterns=None, Debug=None, *args, **kwargs):

        Patterns = dict(Patterns) # Use this to make sure Patterns is a dictionary

        # For each patterns tables
        for attr, P in Patterns.iteritems():
            # Recompute the frequencies in one go + order by frequencies
            P = AugmentedTermFrequency.augmented_tf(P)

        # Return the resulting variables (in a dict of vars)
        return {'Patterns': Patterns}

    # Compute the augmented term frequency from a patterns table containing a 'count' column
    # Note: the augmented term frequency tries to prevent bias towards longer documents.
    # @param patterns One single patterns table
    # @param nosort sort by freq (descending)?
    # @return patterns The patterns table with column freq = augmented tf, ordered by freq
    @staticmethod
    def augmented_tf(patterns, nosort=False):
        # Compute the raw frequencies
        f = patterns.ix[:,'count'].astype('float') / patterns.ix[:,'count'].sum()

        # Compute the augmented term frequency
        tf = 0.5 + ( (f * 0.5) / f.max() )

        # Assign the augmented tf in the patterns table
        patterns.ix[:,'freq'] = tf

        if not nosort:
            # Sort by frequency
            patterns = patterns.sort(['freq'], axis=0).ix[::-1] # sort by augmented term frequency and reorder by descending value

        return patterns
