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

## @package authordetector.interactive
# Manage the interactive interface using IPython Notebook

import sys
import IPython.frontend.terminal.ipapp as ipapp
#from IPython.frontend.html.notebook import notebookapp # if you want to just import the notebook, but some commandline switches like --ipython-dir won't work

## Launch an interactive interface using IPython Notebook
#   @param  *args   a list of extra commandline switches you want to propagate to IPython Notebook
def launch_notebook(*args):
    app = ipapp.TerminalIPythonApp.instance()
    #app = notebookapp.NotebookApp.instance() # if you want to just import the notebook, but some commandline switches like --ipython-dir won't work
    allargs = ['notebook', '--pylab', 'inline', 'ipynb', '--ipython-dir', 'ipynb-profile'] # Set the minimum set of arguments necessary to launch the ipython notebook (note: --ipython-dir is necessary for windows, you need to set a local dir, else ipython might not have access to the default config folder inside Users); you can add --no-browser for daemon at startup; --notebook-dir=/home/foo/wherever to change notebook dir, or just give the directory as a parameter (it's the same)
    if args: # add optional commandline arguments if at least one is supplied (arguments not recognized by authordetector will be propagated to IPython Notebook)
        allargs.extend(*args)
    app.initialize(allargs) # Initialize the IPython Notebook
    sys.exit(app.start()) # Start the IPython Notebook (will open a new page in the browser)

if __name__ == '__main__':
    launch_notebook()