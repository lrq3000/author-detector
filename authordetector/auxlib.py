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

import sys, exceptions

def import_module(module_name):
    ''' Reliable import, courtesy of Armin Ronacher '''
    try:
        __import__(module_name)
    except ImportError:
        exc_type, exc_value, tb_root = sys.exc_info()
        tb = tb_root
        while tb is not None:
            if tb.tb_frame.f_globals.get('__name__') == module_name:
                raise exc_type, exc_value, tb_root
            tb = tb.tb_next
        return None
    return sys.modules[module_name]

def str2int(s):
    ''' Convert a string to int '''
    try:
        return int(s)
    except exceptions.ValueError:
        return int(float(s))

def import_class(packagepath, classname):
    mod = __import__(packagepath, fromlist=[classname])
    myclass = getattr(mod, classname)
    return myclass

#def import_class(fullpackage):
    #d = fullpackage.rfind(".")
    #classname = fullpackage[d+1:len(fullpackage)]
    #module = __import__(fullpackage[0:d], globals(), locals(), [classname])
    #return getattr(module, classname)
