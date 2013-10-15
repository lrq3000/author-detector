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

## @package treetagger
#
# Use TreeTagger to parse all texts and returns lemmas or grammatical category

from authordetector.featuresextractor.basefeaturesextractor import BaseFeaturesExtractor
import authordetector.lib.treetagger.treetaggerwrapper as treetaggerwrapper
import os

## TreeTagger
#
# Use TreeTagger to parse all texts and returns lemmas or grammatical categories
class TreeTagger(BaseFeaturesExtractor):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BaseFeaturesExtractor.__init__(self, config, parent, *args, **kwargs)

    ## Extract features from a text
    # This will extract and return either a list of lemmas, or either the grammatical categories
    # Thank's to Fabien Poulard for his tutorial (french): http://www.fabienpoulard.info/post/2011/01/09/Python-et-Tree-Tagger
    # @param None The texts will be directly accessed through the Reader
    # @return dict A dict containing X, a dict of features PER text (so X[0] will contain all the lemmas/gramcat for text 0, X[1] all features for text 1, etc.)
    def extract(self, *args, **kwargs):

        # Rename TreeTagger's Linux binary to avoid conflicts (by default, same name is used for both MacOSX and Linux binaries)
        for lang in treetaggerwrapper.g_langsupport.iterkeys(): # update for each language
            treetaggerwrapper.g_langsupport[lang]["binfile-lin"] = "tree-tagger-lin"

        # Construction et configuration du wrapper
        tagger = treetaggerwrapper.TreeTagger(TAGLANG=self.config.get("treetagger_lang", "fr"), TAGDIR=self.config.get("treetagger_tmpdir", os.path.join('authordetector', 'lib', 'treetagger', 'TreeTagger')),
                                              TAGINENC=self.config.get("treetagger_charset", "utf-8"), TAGOUTENC=self.config.get("treetagger_charset", "utf-8"))

        return_value = self.config.get("treetagger_return", '') # The type of features we want to return: lemmas, grammatical categories or both?
        charset = self.config.get("reader_charset", 'utf-8')

        # Init the list
        tags = list()

        # Get a generator to iterate over all the available texts
        gen = self.parent.reader.get_all_texts()
        for idx, text in enumerate(gen): # get text and index for each available file
            # Init the sublist or subdict for the current text (one sublist or subdict of features per text)
            if return_value == 'both':
                tags.insert(idx, {'lemmas': list(), 'gramcat': list()} )
            else:
                tags.insert(idx, list())

            # Process through TreeTagger
            triplets = tagger.TagText(text, encoding=charset) # TagText returns a list of items, each items being a triplet of: original word, grammatical category, lemma. Each one being separated by one \t

            # Reformat the triplets and extract only what we want (save memory space and easier to access later)
            for triplet in triplets:
                # Encode our unicode object into UTF-8 (to make sure that all other Python modules will be able to correctly parse it, else modules will try to encode into ascii (instead of decoding) and you will get 'ascii' codec can't encode character...)
                #triplet = triplet.encode('utf-8') # already done in basetextreader now
                # Split the string into a triplet list
                triplet = triplet.split("\t")
                # If the triplet is still a string or the list contains only one item, it means TreeTagger couldn't parse it. We simply skip.
                if isinstance(triplet, (str, basestring)) or len(triplet) == 1:
                    continue

                # Store the values we want from the triplet (either lemmas, either grammatical categories, either both)
                if return_value == 'both':
                    tags[idx]['lemmas'].append(triplet[2])
                    tags[idx]['gramcat'].append(triplet[1])
                elif return_value == 'lemmas':
                    tags[idx].append(triplet[2])
                else:
                    tags[idx].append(triplet[1])

            # For lemmas, we need to filter out unknown words
            if return_value == 'lemmas':
                blen = len(tags[idx])
                tags[idx] = [x for x in tags[idx] if x != '<unknown>']
                if self.config.get("debug"):
                    print("Removed %s unknown tags from lemmas of text %s" % ((blen-len(tags[idx])), idx) )

        return {'X': tags} # always return a dict of vars
