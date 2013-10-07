#!/usr/bin/env python
# encoding: utf-8

## @package basepatternsextractor
#
# This contains the base patterns extractor class that you can use as a template for other classes

from authordetector.base import BaseClass

## BasePatternsExtractor
#
# Base features patterns class that you can use as a template for other classes
# Simply return the same as the input
class BasePatternsExtractor(BaseClass):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BaseClass.__init__(self, config, parent, *args, **kwargs)

    ## Extract patterns from a text
    # Here it simply returns the input
    # @param X The extracted features
    # @return dict A dict containing X2, the patterns
    def extract(self, X=None, *args, **kwargs):
        return {'X2': X}
