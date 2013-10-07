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

## @package basevalidator
#
# This contains the base model validator class that you can use as a template for other classes (eg: cross-validation, ROC curve, etc.)

from authordetector.base import BaseClass

## BaseValidator
#
# Base model validator class that you can use as a template for other classes (eg: cross-validation, ROC curve, etc.)
class BaseValidator(BaseClass):

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
        'change': False
    }

    # Public main method that should be called by Runner
    publicmethod = 'process'

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BaseClass.__init__(self, config, parent, *args, **kwargs)

    ## Compute a model validation (ie: metrics indicating how well the model performs)
    # Here it does nothing
    def validate(self, *args, **kwargs):

        # Compute a model validation here.
        # You are free to compute it at anytime and in any way you want.

        # Return the resulting variables (in a dict of vars)
        return {'ValidationScore': None}
