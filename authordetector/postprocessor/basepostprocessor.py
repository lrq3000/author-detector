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

## @package basepostprocessor
#
# This contains the base post processor class that you can use as a template for other classes

from authordetector.base import BaseClass

## BasePostProcessor
#
# Base post processor class that you can use as a template for other classes
# Simply return the same as the input
class BasePostProcessor(BaseClass):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    # Define what can be returned by this type of module relative to the input data. Or said differently: what will this kind of module _may_ do with the input data? (they may but some modules may do less or more).
    # You should define this in the base class of each category of modules.
    # Flags: transform = transform an input variable into a new variable (with a new name and new datatype) - add: add new variables in addition to input - change: return the same variables (with same datatype) as input but changed
    dataflags = {
        'transform': False,
        'add': True,
        'change': True
    }

    # Public main method that should be called by Runner
    publicmethod = 'process'

    constraints = {
        'after': 'patternsextractor'
    }

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BaseClass.__init__(self, config, parent, *args, **kwargs)

    ## Do various postprocessing stuff
    # Here it simply returns the input
    # @param Patterns The extracted patterns
    # @return dict A dict containing postprocessed Patterns
    def process(self, Patterns=None, *args, **kwargs):

        Patterns = dict(Patterns) # Use this to make sure Patterns is a dictionary

        # do some postprocessing stuff

        # Return the resulting variables (in a dict of vars)
        return {'Patterns': Patterns}
