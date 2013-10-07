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

## @package cosinesimilarity
#
# Compare learned patterns tables with the unlabeled patterns table using Cosine Similarity

from authordetector.detector.basedetector import BaseDetector
#from authordetector.lib.debug import debug
import numpy as np
import pandas as pd

## CosineSimilarity
#
# Compare learned patterns tables with the unlabeled patterns table using Cosine Similarity
class CosineSimilarity(BaseDetector):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BaseDetector.__init__(self, config, parent, *args, **kwargs)

    ## Compare learned patterns tables with the unlabeled patterns table using Cosine Similarity
    # @param L_Patterns The extracted and attributes-merged patterns from the learning corpus of texts
    # @param Patterns The extracted but not merged patterns from the text(s) to detect
    # @return dict A dict containing Result, the attribute(s) found
    #@debug.profile_linebyline #uncomment to debug speed perf line-by-line
    def detect(self, L_Patterns=None, Patterns=None, *args, **kwargs):

        Result = dict()
        Proba = dict()
        for idx, P in Patterns.iteritems(): # Patterns from the unlabeled data to detect (detection patterns)
            Proba[idx] = dict()
            for attr, LP in L_Patterns.iteritems(): # Patterns from the labeled data (learned patterns)

                # Compute the cosine similarity score
                A = P.ix[:,'freq']
                B = LP.ix[:,'freq']
                # Keep only the ngrams that are shared between the tables
                A = A[A.index.isin(B.index)] # TODO: instead of this, try to append to B columns of A and set 0 to count?
                B = B[B.index.isin(A.index)]
                cos = A.dot(B) / ( np.linalg.norm(A) * np.linalg.norm(B) ) # cosine similarity
                Proba[idx][attr] = cos

            max = ['None', 0]
            for k, v in Proba[idx].iteritems():
                if v > max[1]:
                    max = [k, v]

            Result[idx] = max

            print('Result for detection: text %s is detected similar to %s with confidence score: %s' % (idx, max[0], max[1] * 100))

        # Return the resulting variables (in a dict of vars)
        return {'Result': Result, 'Result_details': Proba}
