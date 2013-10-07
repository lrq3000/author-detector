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

## @package regexpfilter
#
# Strip or keep only expressions matching the given list of regular expressions

from authordetector.preprocessor.basepreprocessor import BasePreProcessor
import re

## RegexpFilter
#
# Strip or keep only expressions matching the given list of regular expressions
class RegexpFilter(BasePreProcessor):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BasePreProcessor.__init__(self, config, parent, *args, **kwargs)

    ## Strip or keep only expressions matching the given list of regular expressions
    # @param Text A raw text input from a reader
    # @return dict A dict containing Text, the preprocessed text
    def process(self, Text=None, *args, **kwargs):
        mode = self.config.get('regexpfilter_mode', 'strip') # either 'strip' or 'keep'
        pat = self.config.get('regexpfilter_patterns')

        # Only if a pattern was set
        if pat is not None:
            # Convert to a list if it's not
            if not isinstance(pat, list):
                pat = [pat]

            # Compare the text to each pattern
            for p in pat:
                # Strip mode: we remove all occurrences
                if mode == 'strip':
                    Text = re.sub(p, '', Text)
                # Keep mode: we recursively keep only the patterns found
                else:
                    Text = ' '.join(re.findall(p, Text))

        return {'Text': Text}
