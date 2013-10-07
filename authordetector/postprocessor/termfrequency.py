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

## @package termfrequency
#
# Recomputes the term frequency in the 'freq' column using raw frequencies

from authordetector.postprocessor.basepostprocessor import BasePostProcessor

## TermFrequency
#
# Recomputes the term frequency in the 'freq' column using raw frequencies
class TermFrequency(BasePostProcessor):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BasePostProcessor.__init__(self, config, parent, *args, **kwargs)

    # Recomputes the term frequency in the 'freq' column using raw frequencies
    # @param Patterns The extracted patterns
    # @return dict A dict containing postprocessed Patterns with column freq = updated frequencies, ordered by frequencies
    def process(self, Patterns=None, Debug=None, *args, **kwargs):

        Patterns = dict(Patterns) # Use this to make sure Patterns is a dictionary

        # For each patterns tables
        for attr, P in Patterns.iteritems():
            # Recompute the frequencies in one go + order by frequencies
            P = TermFrequency.tf(P)

        # Return the resulting variables (in a dict of vars)
        return {'Patterns': Patterns}

    # Compute the term frequency from a patterns table containing a 'count' column using raw frequencies
    # @param patterns One single patterns table
    # @return patterns The patterns table with column freq = updated frequencies, ordered by frequencies
    @staticmethod
    def tf(patterns, *args, **kwargs):
        # Recompute the frequencies in one go
        patterns.ix[:,'freq'] = patterns.ix[:,'count'].astype('float') / patterns.ix[:,'count'].sum()

        # Sort by frequency
        patterns = patterns.sort(['freq'], axis=0).ix[::-1] # sort by frequency and reorder by descending value

        return patterns
