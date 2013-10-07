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

import lib.argparse as argparse
import sys

from authordetector.run import Runner
import interactive

## Parse the commandline arguments
# @param argv A list of strings containing the arguments (optional)
def parse_cmdline_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    desc = '''Author Detector ---
    Description: Detect the style of an author and then recognize an author.
    '''
    epi = '''Note: commandline switches have precedence over configuration file. This also means that you can use absolutely any parameter that is valid in a configuration file, as a commandline argument, and inversely.'''

    #-- Constructing the parser
    parser = argparse.ArgumentParser(description=desc,
                                     add_help=True, argument_default=argparse.SUPPRESS, conflict_handler="resolve",
                                     epilog=epi)

    #-- Getting the arguments
    parser.add_argument('--help', '-help', '-h', dest='help', action='store_true', default=False,
                        help='show this help message and exit')
    parser.add_argument('--interactive', '-i', dest='interactive', action='store_true', default=False,
                        help='interactive mode, open an ipython notebook web interface (you need ipython notebook to be installed). Note: any additional argument will be propagated to the IPython Notebook.')
    parser.add_argument('--script', '-s', dest='script', action='store_true', default=False,
                        help='do not run the main loop, only load the constructs and config file, and then return a Runner instance so that you can use these constructs in whatever way you want using Python or Notebook.')
    parser.add_argument('--config', '-c', dest='config', action='store', default='config.json',
                        help='specify a path to a specific configuration file you want to use')
    parser.add_argument('--parametersfile', '-p', dest='parametersfile', action='store',
                        help='REQUIRED - parameters file, containing the best learned parameters (if --learn is set, the parametersfile will be written with the best learned parameters, else it will be read at detection to reload the parameters in memory)')
    parser.add_argument('--textroot', '-t', dest='textroot', action='store', default='texts',
                        help='path where the texts files are (relative or absolute)')
    parser.add_argument('--textconfig', '-tc', dest='textconfig', action='store', default='textconfig.json',
                        help='path to the config listing texts to learn with paths and labels')
    parser.add_argument('--textconfig_detection', '-td', dest='textconfig', action='store', default='textconfig_detection.json',
                        help='path to the config listing unlabeled texts to identify')
    parser.add_argument('--learn', '-l', dest='learn', action='store_true', default=False,
                        help='Learning mode: learn the parameters from the labeled texts (if not specified, detection mode will be enabled)')



    #-- Parsing (loading) the arguments
    try:
        [args, extras] = parser.parse_known_args(argv) # Storing all arguments into args, and remaining unprocessed (unrecognized) arguments by authordetector will be propagated to other applications (eg: IPython Notebook)
        #extras.insert(0, sys.argv[0]) # add the path to this script file (to normalize the arguments)
        #sys.argv = extras # replace the system arguments by only the remaining unprocessed ones. This will produce a bug with ipython notebook
    except BaseException, e: # in case of an exception at parsing arguments, try to continue
        print('Exception: %s' % str(e)) # print the exception anyway
        pass

    return (args, extras, parser)

## Main entry point, processes commandline arguments and then launch the appropriate module
# @param argv A list of strings containing the arguments (optional)
def main(argv=None):
    #-- Parsing (loading) the arguments
    [args, extras, parser] = parse_cmdline_args(argv)
    args = args.__dict__ # convert to an array (so that it becomes iterable)

    #-- Processing the commandline switches
    # Help message
    if args['help']:
        parser.print_help()
        return
    # Interactive mode, we launch the IPython Notebook
    elif args['interactive']:
        interactive.launch_notebook(extras)
    # Scripting mode: load the config and make the constructs, but do not run the main loop
    elif args['script']:
        runner = Runner()
        runner.init(args, extras)
        return runner
    # Learning mode
    elif args['learn']:
        print("AuthorDetector: Learning mode")
        print("Initialization of the Runner module and all submodules specified in the config file %s..." % args['config'])
        runner = Runner()
        runner.init(args, extras)
        print("Learning the parameters from texts defined in %s and saving in %s.\nPlease wait, this may take a while depending on how big your datafile is..." % (args['textconfig'], args['parametersfile']))
        return runner.learn()
    # Run the detection mode by default
    else:
        print("AuthorDetector: Detection mode")
        print("Initialization of the Runner module and all submodules specified in the config file %s..." % args['config'])
        runner = Runner()
        runner.init(args, extras)
        #print("AuthorDetector: launching the detection and outputting results in the file: " % args['resultsfile'])
        return runner.run()


if __name__ == '__main__':
    sys.exit(main())
