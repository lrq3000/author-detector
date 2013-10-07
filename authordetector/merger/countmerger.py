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

## @package countmerger
#
# Merge patterns by their count and then recompute the frequencies. Very accurate computation (a lot more than using the mean).

from authordetector.merger.basemerger import BaseMerger
from authordetector.postprocessor.termfrequency import TermFrequency
import pandas as pd

## CountMerge
#
# Merge patterns by their count and then recompute the frequencies. Very accurate computation (a lot more than using the mean).
# This will first merge all patterns tables associated with texts sharing the same desired attribute, and then if there are collisions, it will add the counts and then at the end recompute the frequencies of all the patterns.
class CountMerger(BaseMerger):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BaseMerger.__init__(self, config, parent, *args, **kwargs)

    # Merge patterns by their count and then recompute the frequencies.
    # Very accurate computation (a lot more than using the mean).
    # @param Patterns The extracted patterns
    # @return dict A dict containing Patterns tables per attribute, and per attribute type (eg: Patterns['author']['Machiavel']), the patterns matched to the desired attribute(s)
    def merge(self, Patterns=None, *args, **kwargs):
        mattr = self.config.get("merger_attribute", 'author') # Type of attribute to match the patterns to. This MUST be implemented in all subclasses

        # Convert to a list of attributes if it's a string
        #if isinstance(merger_attribute, basestring): # removed, too complex to interop with other modules
            #merger_attribute = [merger_attribute]

        # Init a dict of Patterns tables for this type of attributes (this is the var that will be returned)
        P2 = dict()
        # for each text
        for idx in xrange(len(self.parent.reader)):
            # get all text attributes
            allattr = self.parent.reader.get_params(idx)
            # fetch the one of the type we want
            attr = allattr[mattr]

            # If the current Patterns table is empty, we just copy over the Patterns table of the text (we will complete it further later with tables of other texts matching the same attribute)
            if P2.get(attr) is None:
                P2[attr] = Patterns[idx]
            # Else we already have a Patterns table from a previous text, then we complete it with the data from the Patterns table of this text
            else:
                # for each index and row of this Patterns table
                for idn2, s in Patterns[idx].iterrows():
                    # If there is a collision (the pattern already exists in the current table), then we add both counts
                    if idn2 in P2[attr].index:
                        P2[attr].ix[idn2, 'count'] += s['count']
                    #else: # Else no collision, the n-gram is new, we append it to the Patterns table - UNEFFICIENT!!!
                        #P2[attr] = P2[attr].append(s, ignore_index=False) # UNEFFICIENT!!! Infinite time! Workaround below

                # Append in one go all the new patterns where there's no collision (the patterns exist in the table2, but not in table1)
                P2[attr] = P2[attr].append(Patterns[idx].ix[~Patterns[idx].index.isin(P2[attr].index)]) # TODO: verifier pas trompe de sens dans le isin() ici

                # Recompute the frequencies in one go + order by frequencies
                P2[attr] = TermFrequency.tf(P2[attr])


        # Return the resulting variables (in a dict of vars)
        return {'Patterns': P2}
