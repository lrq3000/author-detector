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

## @package xmlstripper
#
# Strip xml tags from the text

from authordetector.preprocessor.basepreprocessor import BasePreProcessor
import xml.etree.ElementTree as ET

## XMLStripper
#
# Strip xml tags from the text
class XMLStripper(BasePreProcessor):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BasePreProcessor.__init__(self, config, parent, *args, **kwargs)

    ## Strip xml tags from the text
    # Reliably strip xml tags using xml parser (instead of regexp), but the input must be a correctly formatted xml
    # @param Text A raw text input from a reader
    # @return dict A dict containing Text, the preprocessed text
    def process(self, Text=None, *args, **kwargs):
        tree = ET.fromstring(Text)
        notags = ET.tostring(tree, encoding='utf8', method='text')
        return {'Text': notags}
