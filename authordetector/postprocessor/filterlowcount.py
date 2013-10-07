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

## @package filterlowcount
#
# Filter out patterns with low count/freq (below a configurable threshold)

from authordetector.postprocessor.basepostprocessor import BasePostProcessor
from authordetector.postprocessor.termfrequency import TermFrequency
from scipy.stats import scoreatpercentile

## FilterLowCount
#
# Filter out patterns with low count/freq (below a configurable threshold)
class FilterLowCount(BasePostProcessor):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BasePostProcessor.__init__(self, config, parent, *args, **kwargs)

    # Filter out patterns with low count/freq (below a configurable threshold)
    # Note: it may happen that more than the specified percentile of the population is filtered, for example when a lot of the population has 1 count and you want to drop 50% of the population. Then, you may end up dropping a lot more, because they also have 1 count.
    # @param Patterns The extracted patterns
    # @return dict A dict containing postprocessed Patterns
    def process(self, Patterns=None, Debug=None, *args, **kwargs):
        threshold = self.config.get("filterlowcount_threshold", 0.5)
        if isinstance(threshold, basestring) and not threshold == 'mean':
            threshold = float(threshold)
        if not isinstance(threshold, basestring) and threshold < 1:
            threshold = threshold * 100

        Patterns = dict(Patterns) # Use this to make sure Patterns is a dictionary

        for attr, P in Patterns.iteritems():
            # Remember the total number of patterns before
            blen = len(P.index)

            # Compute the score (count) under which we will drop patterns
            # either below the mean
            if isinstance(threshold, basestring) and threshold == 'mean':
                limit = P.ix[:,'count'].mean()
            # either below a percentile (0.5 = median)
            else:
                limit = scoreatpercentile(P.ix[:,'count'], per=threshold, axis=0)

            # Drop patterns below or equal to this count
            Patterns[attr] = P.drop(P.ix[P.ix[:,'count'] <= limit].index)

            # Recompute the frequencies in one go + order by frequencies
            Patterns[attr].ix[:,'freq'] = Patterns[attr].ix[:,'freq'] / float(Patterns[attr].ix[:,'freq'].sum())
            Patterns[attr] = Patterns[attr].sort(['freq'], axis=0).ix[::-1]

            # Printing infos
            nlen = len(Patterns[attr].index) # total number of patterns after
            print('Patterns table %s: detected count for threshold %s: %s - dropped %s rows, remaining %s rows' % (attr, threshold, limit, blen - nlen, nlen))

        # Return the resulting variables (in a dict of vars)
        return {'Patterns': Patterns}
