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

## @package basetextreader
#
# This contains the base text reader that you can use as a template for other classes
# Note: you must make sure that your class will properly encode any input into a charset you define (preferable utf-8)

from authordetector.base import BaseClass
from authordetector.configparser import ConfigParser
import os
import codecs

## BaseTextReader
#
# Base text reader, reads txt files as-is
# Note: default encoding is utf-8
class BaseTextReader(BaseClass):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## @var textconfig
    # Contains the text configuration parameters from the textconfig file

    ## @var textrootdir
    # Root directory where the text files reside (can be relative or absolute)

    # Define what can be returned by this type of module relative to the input data. Or said differently: what will this kind of module _may_ do with the input data? (they may but some modules may do less or more).
    # You should define this in the base class of each category of modules.
    # Flags: transform = transform an input variable into a new variable (with a new name and new datatype) - add: add new variables in addition to input - change: return the same variables (with same datatype) as input but changed
    dataflags = {
        'transform': False,
        'add': True,
        'change': False
    }

    # Public main method that should be called by Runner
    publicmethod = 'get_text'

    constraints = {
        'after': None
    }

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        C = BaseClass.__init__(self, config, parent, *args, **kwargs)
        self.__dict__['textconfig'] = ConfigParser()
        self.reloadconfig()

        return C

    ## Return the text config parameters for a given index
    # This is a wrapper for BaseTextReader.textconfig.get()
    # @param idx Index of the text
    # @return dict Dictionary of parameters
    def get_params(self, idx, *args, **kwargs):
        if not isinstance(idx, int) or idx < 0:
            raise Exception("Index is expected to be a positive integer")

        return self.textconfig.get(idx)

    ## Return the filepath of a text for a given index
    # @param idx Index of the text
    # @return string Filepath of the text
    def get_filepath(self, idx, *args, **kwargs):
        return os.path.join(self.textrootdir, self.get_params(idx)['file'])

    ## Return the raw text for a given index
    # @param idx Index of the text
    # @return string Full raw text (no preprocessing)
    def get_raw_text(self, idx, *args, **kwargs):
        charset = self.config.get("reader_charset", 'utf-8')
        with codecs.open(self.get_filepath(idx), 'rb', encoding=charset) as f:
            text = f.read()
            text = text.encode(charset) # encode in the specified charset
        return text

    ## Return the preprosseced text for a given index
    # @param idx Index of the text
    # @return string Full preprocessed text
    def get_preprocessed_text(self, idx, *args, **kwargs):
        text = self.get_raw_text(idx)
        if self.parent.__dict__.get('preprocessor', None):
            dictofvars = self.parent.generic_call(self.parent.preprocessor, 'process', args={'Text': text}, return_vars=True)
        return dictofvars.get('Text')

    ## Wrapper function that, for a given text index, will return either the raw text or either the preprocessed text, depending if a preprocessor was configured
    # NOTICE: this method MUST be implemented in all readers!
    # @param idx Index of the text
    # @return string Full raw or preprocessed text
    def get_text(self, idx, *args, **kwargs):
        if self.parent.__dict__.get('preprocessor', None):
            return self.get_preprocessed_text(idx, *args, **kwargs)
        else:
            return self.get_raw_text(idx, *args, **kwargs)

    ## Generator function, will return all texts, one at a time
    # NOTICE: this method MUST be implemented in all readers!
    # @return gen A generator producing one text for each access
    def get_all_texts(self, *args, **kwargs):
        for idx in xrange(len(self.parent.reader)):
            yield self.get_text(idx)

    ## Return the total number of texts specified in the textconfig
    # NOTICE: this method MUST be implemented in all readers!
    def __len__(self, *args, **kwargs):
        return len(self.textconfig.config)

    ## Return the total number of texts specified in the textconfig
    def count(self, *args, **kwargs):
        return len(self)

    def reloadconfig(self, *args, **kwargs):
        if self.parent.vars.get("Mode", 'Learning') == 'Learning':
            self.textconfig.init(configfile=self.config.get("textconfig"))
        else:
            self.textconfig.init(configfile=self.config.get("textconfig_detection"))
        self.textconfig.load(comments=True)
        self.textrootdir = self.config.get("textrootdir")
