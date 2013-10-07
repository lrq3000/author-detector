#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2001-2007 Martin Blais. All Rights Reserved
# Copyright (C) 2010 Bear http://code-bear.com/bearlog/
# Copyright (C) 2013 lrq3000

# Excerpt from SnakeFood to recursively list all imports of modules using AST parsing
# Additions to print the versions of each module if available

import os, sys
import compiler
from compiler.ast import Discard, Const
from compiler.visitor import ASTVisitor
import numbers

def pyfiles(startPath):
    r = []
    d = os.path.abspath(startPath)
    if os.path.exists(d) and os.path.isdir(d):
        for root, dirs, files in os.walk(d):
            for f in files:
                n, ext = os.path.splitext(f)
                if ext == '.py':
                    r.append([root, f])
    return r

class ImportVisitor(object):
    def __init__(self):
        self.modules = []
        self.recent = []
    def visitImport(self, node):
        self.accept_imports()
        self.recent.extend((x[0], None, x[1] or x[0], node.lineno, 0)
                           for x in node.names)
    def visitFrom(self, node):
        self.accept_imports()
        modname = node.modname
        if modname == '__future__':
            return # Ignore these.
        for name, as_ in node.names:
            if name == '*':
                # We really don't know...
                mod = (modname, None, None, node.lineno, node.level)
            else:
                mod = (modname, name, as_ or name, node.lineno, node.level)
            self.recent.append(mod)
    def default(self, node):
        pragma = None
        if self.recent:
            if isinstance(node, Discard):
                children = node.getChildren()
                if len(children) == 1 and isinstance(children[0], Const):
                    const_node = children[0]
                    pragma = const_node.value
        self.accept_imports(pragma)
    def accept_imports(self, pragma=None):
        self.modules.extend((m, r, l, n, lvl, pragma)
                            for (m, r, l, n, lvl) in self.recent)
        self.recent = []
    def finalize(self):
        self.accept_imports()
        return self.modules

class ImportWalker(ASTVisitor):
    def __init__(self, visitor):
        ASTVisitor.__init__(self)
        self._visitor = visitor
    def default(self, node, *args):
        self._visitor.default(node)
        ASTVisitor.default(self, node, *args)

def parse_python_source(fn):
    contents = open(fn, 'rU').read()
    ast = compiler.parse(contents)
    vis = ImportVisitor()

    compiler.walk(ast, vis, ImportWalker(vis))
    return vis.finalize()

def find_imports_and_print(startPath):
    for d, f in pyfiles(startPath):
        print d, f
        print parse_python_source(os.path.join(d, f))

def find_imports(startPath):
    moduleslist = {}
    # Get the list of .py files and iterate over
    for d, f in pyfiles(startPath):
        # For each .py file, parse and get the list of imports
        mod = parse_python_source(os.path.join(d, f))
        # For each imported module, store only the root module (eg: sys.os -> will store only sys)
        for m in mod:
            moduleslist[m[0].split(".")[0]] = True
    # Return the list of unique modules names
    return moduleslist.keys()

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

def find_versions(moduleslist):
    ''' Find the version of each module if available (and only for modules installed, does not work with locally included files) '''
    modver = {}
    # For each module
    for mod in moduleslist:
        ver = 'NA'
        m = import_module(mod) # Import the module
        if m is None: # The module is not installed
            ver = 'Not installed'
        # Else the module is installed and imported, we try to find the version
        else:
            # Iterate over all keys and try to find the version
            verlist = []
            for k, v in m.__dict__.iteritems():
                if ( 'version' in k.lower() or '__version__'  in k.lower() or 'ver' in k.lower() ) \
                    and isinstance(v, (basestring, numbers.Number)) :
                    verlist.append(v)
        # Store the version
        if len(verlist) > 1:
            modver[mod] = verlist
        elif len(verlist) == 1:
            modver[mod] = verlist[0]
        else:
            modver[mod] = ver
    # Return a dict where the keys are the modules names and values are the versions
    return modver


if __name__ == '__main__':
    import pprint
    moduleslist = find_imports(os.path.join('..', '..', 'authordetector'))
    modver = find_versions(moduleslist)
    print('List of modules imported:')
    print(moduleslist)
    print('-'*50)
    print('List of modules and versions:')
    pprint.pprint(modver)
    input("Press Enter to continue...")
