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

## @package simpleinference
#
# Simple inference to detect the most probable Patterns table and thus attribute(s) for a given text

from authordetector.detector.basedetector import BaseDetector
from authordetector.lib.debug import debug

## SimpleInference
#
# Simple inference to detect the most probable Patterns table and thus attribute(s) for a given text
class SimpleInference(BaseDetector):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BaseDetector.__init__(self, config, parent, *args, **kwargs)

    ## Detect the desired attribute of the given text based on learned parameters
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
                # Smooth the proba to avoid 0
                min = LP.ix[:,'freq'].min()
                if min == 0: min = 0.000000000001

                # Deprecated: iterative method
                #Proba[idx][attr] = 1
                #for idn, s in P.iterrows():
                    #idn = int(idn) # make sure this is not a string but a number, else the index comparison will fail
                    #if idn in LP.index: # more efficient than a try/except block (was profiled)
                        #Proba[idx][attr] = Proba[idx][attr] * LP.ix[idn,'freq']
                    #else: # Sort of Laplacian smoothing: take the minimum freq value to avoid 0
                        #Proba[idx][attr] = Proba[idx][attr] * min

                # New method: vectorized computation
                #p = P.join(LP, rsuffix='_L') # first merge the two patterns tables on index
                #p = p.ix[:,'freq'] * p.ix[:,'freq_L'] # multiply the frequencies
                p = P.ix[:,'freq'] * LP.ix[:,'freq'] # multiply the frequencies of both patterns tables (automagically matched by index thank's to Pandas)
                p = p.fillna(min) # fill minimum values for patterns in P that aren't found in LP
                Proba[idx][attr] = p.sum() # sum it

            max = ['None', 0]
            for k, v in Proba[idx].iteritems():
                if v > max[1]:
                    max = [k, v]

            Result[idx] = max

            print('Result for detection: text %s is detected similar to %s with confidence score: %s' % (idx, max[0], max[1] * 100))

        # Return the resulting variables (in a dict of vars)
        return {'Result': Result, 'Result_details': Proba}
