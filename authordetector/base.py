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

## @package base
#
# This contains the base classes that are used by most other classes (in subfolders)
# Remember that the main function (eg: process() ) in your implemented class should return a dict of vars (eg: return {'X': var})

## BaseClass
#
# Base class for most other classes (in subfolders)
class BaseClass(object):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    ## Constructor
    # @param config An instance of the ConfigParser class
    # @param parent The parent class, so that a child class can access the parent class namespace (variables and methods) at any moment
    def __init__(self, config=None, parent=None, *args, **kwargs):
        if not self.loadconfig(config):
            print('CRITICAL ERROR : COULD NOT LOAD CONFIG IN CLASS %s' % self.__class__)
            raise SystemExit(220)
        if parent:
            self.parent = parent
        return object.__init__(self)

    ## Register the configuration to be directly accessible as a variable inside this object
    # @param config An instance of the ConfigParser class, or path to the config file
    def loadconfig(self, config, *args, **kwargs):

        # No config, we quit
        if not config:
            return False

        # If we were supplied a string, we consider it to be the path to the config file to load
        if isinstance(config, basestring):
            # Loading the config
            from configparser import ConfigParser
            self.config = ConfigParser()
            self.config.init(config)
            self.config.load(*args)
        # Else we already have a loaded config object, we just reference it locally
        else:
            self.config = config

        return True