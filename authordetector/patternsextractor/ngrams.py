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

## @package ngrams
#
# This contains the words ngrams patterns extractor

from authordetector.patternsextractor.basepatternsextractor import BasePatternsExtractor
import pandas as pd
import hashlib
import numbers
import itertools

## NGrams
#
# Words NGrams patterns extractor
# Will return the list of all ngrams (couples, triplets, etc...) of words (not letters, with words we analyze the relationship between words) along with their frequencies/probabilities (computed by counting)
class NGrams(BasePatternsExtractor):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BasePatternsExtractor.__init__(self, config, parent, *args, **kwargs)

    ## Extract NGrams from a set of texts
    # Note: this will return a list of ngrams for each text
    # @param X The extracted features
    # @return dict A dict containing Patterns, the ngrams per text (eg: Patterns[0] for the n-grams table of 1st text)
    def extract(self, X=None, Mode=None, *args, **kwargs):

        #== Loading config params
        n = int(self.config.get("ngrams_number", 1)) # number of words to put in each gram
        tosort = self.config.get("ngrams_sort", False) # sort the ngrams (words ordering in a ngram doesn't matter anymore, reduce the number of combinations)
        wildcards = self.config.get("ngrams_wildcards") # if we want to use ngrams with wildcards
        if Mode == 'Learning':
            wildcards_mode = self.config.get("ngrams_wildcards_mode_learning", 'insert') # wildcards mode when dynamical (insert or replace)
        else:
            wildcards_mode = self.config.get("ngrams_wildcards_mode_detection", 'replace')
        wildcard_placeholder = self.config.get("ngrams_wildcards_placeholder", '*') # only for dynamic wildcards

        static_wildcards = None
        dynamic_wildcards = None

        # Check that wildcards is valid
        if wildcards is not None:
            # Static wildcards list
            if isinstance(wildcards, list):
                if not len(wildcards) == n:
                    print('WARNING: len(wildcards) != n. Length of the wildcards list does not match number n of ngrams. wildcards will be disabled.')
                else:
                    static_wildcards = wildcards
            # Dynamic wildcards (all possible permutation)
            elif isinstance(wildcards, numbers.Number):
                if wildcards >= n or wildcards <= 0:
                    print('WARNING: number of wildcards >= n. Number of wildcards must be between ]0, n[. wildcards will be disabled.')
                else:
                    dynamic_wildcards = wildcards
            # Else error
            else:
                print('WARNING: Unrecognized format for ngram_wildcards. wildcards will be disabled.')
            # In any case, we remove the temporary wildcards variables
            wildcards = None

        #== Computing list of ngrams + counting their occurrences at the same time
        patterns = dict() # for consistency with the merger, we use a dict instead of a list
        totalcount = 0

        # Precompute all wildcards permutations if dynamic ngrams is enabled
        if dynamic_wildcards:
            # Compute the wildcards mask (binary mask where 1 is a wildcard, )
            w = [1] * dynamic_wildcards + [0] * (n-dynamic_wildcards)
            # Compute all permutations of this mask (all possible unique positions of all wildcards)
            wmasks = set(itertools.permutations(w))

        # In insert mode, n represent the final length of the ngrams (with wildcards inserted)
        if dynamic_wildcards and wildcards_mode == 'insert':
            n = n - dynamic_wildcards

        # For each Text
        # Note: idx = id text, idn = id ngram
        for idx, Text in enumerate(X):
            patterns.update({idx: dict()}) # init the dict of ngrams for this text
            #patterns.insert(idx, zip(*[Text[i:-n+i] for i in xrange(n)]) ) # one-liner to generate n-grams but without frequencies. It is sort of computationally vectorised, meaning that it first produces n copies of the original list, but shifted (first list is not shifted, second list is by 1, third by 2, etc.), and then one item per list is coupled with the others (thus you end up with a list of couples of n words).

            # For each n-gram
            # Note: we place a moving start cursor (placed on the first word of each ngram)
            for i in xrange(len(Text)-n):

                # -- Prepare the ngram(s)

                # Get the ngram (a simple list slice from cursor i to i+n)
                ngram = Text[i:i+n]

                # Sort alphabetically the ngrams if we chose to (thus we lower the number of ngrams by removing permutations, eg: [c, a, b] will be the same as [a, b, c])
                if tosort: ngram = sorted(ngram, key=str.lower)

                # If dynamic wildcards enabled, duplicate the ngram and generate all combinations with wildcards in different positions
                if dynamic_wildcards:
                    #ngrams = [ngram[:] for x in xrange(len(wmasks))]
                    ngrams = []
                    for w in wmasks:
                        # Replace mode
                        if wildcards_mode == 'replace':
                            g = [item if not w[i] else wildcard_placeholder for i,item in enumerate(ngram)]
                        # Insert mode
                        else:
                            g = []
                            i = 0
                            for wi in w:
                                if wi:
                                    g.append(wildcard_placeholder)
                                else:
                                    g.append(ngram[i])
                                    i += 1
                        ngrams.append(g)
                    del g

                # Else we just use this ngram without computing all wildcards combinations
                else:
                    ngrams = [ngram] # put this in a list so that we can use the same for loop

                # -- Appending the ngram(s) in the patterns table
                for ngram in ngrams:
                    # Filter wildcards if enabled
                    if static_wildcards:
                        ngram = [item for i, item in enumerate(ngram) if static_wildcards[i]]

                    # IMPORTANT: Computation of a unique index (id) for each n-gram
                    # New method: compute the md5 hash of the concatenated stringified n-gram
                    idn = str(' '.join(ngram)).lower() # stringify the n-gram by concatenating with spaces, and lowercase
                    idn = hashlib.md5( idn ).hexdigest() # compute the md5 hash (this is our id)
                    # Deprecated method: Compute the unique id (convert to the ASCII code representation, with fixed 3 zeros padding to avoid collisions)
                    #idn = ''.join(['%03d' % ord(c) for c in ' '.join(ngram)])

                    # If the ngram was already encountered in this text, we increment the count
                    if patterns[idx].get(idn, None) is not None:
                        patterns[idx][idn]['count'] += 1
                    # Else we create a new ngram entry
                    else:
                        patterns[idx][idn] = {'ngram': ngram, 'count': 1, 'freq': 0}
                    # Compute the total count by the way
                    totalcount += 1

        # Compute the frequencies
        for pt in patterns.itervalues(): # pt = patterns per text
            for key in pt.iterkeys():
                pt[key]['freq'] = float(float(pt[key]['count']) / totalcount)

        # Convert to Pandas DataFrames instead of dict
        for idx,pt in patterns.iteritems():
            patterns[idx] = pd.DataFrame([v for v in pt.itervalues()], index=[k for k in pt.iterkeys()], columns=['ngram', 'count', 'freq']) # convert to a Pandas DataFrame
            patterns[idx] = patterns[idx].sort(['freq'], axis=0).ix[::-1] # sort by frequency and reorder by descending value
            patterns[idx].ix[:,'freq'] = patterns[idx].ix[:,'freq'].astype('float64')
            patterns[idx].ix[:,'count'] = patterns[idx].ix[:,'count'].astype('int32')

        # Return the resulting variables (in a dict of vars)
        return {'Patterns': patterns}
