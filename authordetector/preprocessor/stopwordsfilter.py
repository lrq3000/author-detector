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

## @package stopwordsfilter
#
# Strip or keep only the stopwords, given a list of stopwords

from authordetector.preprocessor.basepreprocessor import BasePreProcessor
import re
import codecs

## StopWordsFilter
#
# Strip or keep only the stopwords, given a list of stopwords
class StopWordsFilter(BasePreProcessor):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BasePreProcessor.__init__(self, config, parent, *args, **kwargs)

    ## Strip or keep only the stopwords, given a list of stopwords
    # @param Text A raw text input from a reader
    # @return dict A dict containing Text, the preprocessed text
    def process(self, Text=None, *args, **kwargs):
        charset = self.config.get("reader_charset", 'utf-8')
        mode = self.config.get('stopwordsfilter_mode', 'strip') # either 'strip' or 'keep'
        stopwords = self.config.get('stopwordsfilter_file') # path to the file containing the stopwords

        if stopwords is not None:
            slist = []
            with codecs.open(stopwords, 'r', encoding=charset) as f:
                for s in f: # for each line (stopword) in the file
                    s = s.strip() # trip empty spaces
                    if len(s) > 0: # check that the line is not empty
                        slist.append(s)

            # Compile all the words in a single regexp
            pat = re.compile(r'\b('+'|'.join(slist)+r')\b', re.I)
            # Strip mode: we remove all stopwords
            if mode == 'strip':
                Text = pat.sub('', Text)
            # Keep mode: keep only stopwords and remove all the other words
            else:
                Text = ' '.join(pat.findall(Text))

        return {'Text': Text}
