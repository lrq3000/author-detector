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

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

__author__  = 'lrq3000'
__version__ = '1.0.0'


# Check Python version is 2.7
import sys
if sys.version_info >= (3,):
    raise SystemExit("Sorry, cannot continue, this application is not yet compatible with python version 3! (or try using python 2to3 utility)")
if sys.version_info < (2,6):
    raise SystemExit("Sorry, cannot continue, this application is not compatible with python versions earlier than 2.6!")

# Change current working directory (so that relative paths work correctly)
import inspect, os
filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
os.chdir(path)

import authordetector.main

## Main entry point for the AuthorDetector program
# @param argv A list of strings containing the arguments (optional)
def main(argv=None):
    return authordetector.main.main(argv)

if __name__ == '__main__':
    sys.exit(main())