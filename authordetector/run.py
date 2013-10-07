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

from auxlib import *
from authordetector.configparser import ConfigParser
import os, sys, StringIO
import pandas as pd
import time
import traceback
from collections import OrderedDict

json = import_module('ujson')
if json is None:
    json = import_module('json')
    if json is None:
        raise RuntimeError('Unable to find a json implementation')

class Runner:

    rootdir = 'authordetector'

    ## @var vars contain a dynamical dict of variables used for data mining, and will be passed to every other computational function
    vars = {} # we create a reference at startup so that this dict can be passed as a reference to children objects

    ## Initialize a runner object, with all constructs necessary to use the algorithms and process data according to the provided configuration file and commandline arguments
    # @param args recognized and processed commandline arguments
    # @param extras extra commandline arguments that are not explicitly recognized (but will nevertheless be appended to the config file, so that you can overwrite pretty much any configuration parameter you want at commandline)
    def init(self, args, extras):
        self.vars = dict()
        #-- Loading config
        self.config = ConfigParser()
        configfile = args['config']; del args['config'] # delete the config argument, which is at best a self reference
        self.config.init(configfile)
        self.config.load(args, extras, comments=True)

        #-- Loading classes
        for (submod, classname) in self.config.config["classes"].iteritems(): # for each item/module specified in classes
            localname = submod
            if self.config.get('classes_alias') and self.config.get('classes_alias').get(localname):
                submod = self.config.get('classes_alias').get(localname)
            else:
                submod = localname
            # if it is a list of classes, we load all the classes into a local list of classes
            if type(classname) == type(list()):
                #self.__dict__[localname] = {} # initializing the local list of classes
                # for each class in the list
                for oneclassname in classname:
                    # we add the class
                    self.addclass(localname, submod, oneclassname, True)
            # if a special string "all" is supplied, we load all the classes into a local list of classes (if a class with a similar name to the filename exists - the classname can have mixed case, the case doesn't matter if the filename corresponds to the classname.lower())
            elif classname == 'all':
                #self.__dict__[localname] = {} # initializing the local list of classes
                modlist = os.listdir(os.path.join(self.rootdir, submod)) # loading the list of files/submodules
                modlist = list(set([os.path.splitext(mod)[0] for mod in modlist])) # strip out the extension + get only unique values (else we will get .py and .pyc filenames, which are in fact the same module)
                # Trim out the base class and __init__
                # Remove all base modules (modules whose names starts with 'base')
                [modlist.remove(mod) for mod in modlist if mod.startswith('base')]
                # Remove all __init__ modules (these are only used by the python interpreter)
                if '__init__' in modlist:
                    modlist.remove('__init__')

                # For each submodule
                for classname2 in modlist:
                    full_package = '.'.join([self.rootdir, submod, classname2.lower()])
                    mod = import_module(full_package) # we need to load the package before being able to list the classes contained inside
                    # We list all objects contained in this module (normally we expect only one class, but nevermind)
                    for iclass, iclassname in [(obj, obj.__name__) for obj in [getattr(mod, name) for name in dir(mod)] if isinstance(obj, type)]:
                        # If the object is a class, and the class name is the same as the filename, we add an instance of this class!
                        if iclassname.lower() == classname2.lower():
                            # we add the class
                            self.addclass(localname, submod, iclassname, True)
            # if we just have a string, we add the class that corresponds to this string
            # Note: the format must be "submodule": "ClassName", where submodule is the folder containing the subsubmodule, and "ClassName" both the class name, and the subsubmodule filename ("classname.py")
            else:
                self.addclass(localname, submod, classname)

        return True

    ## Instanciate dynamically a class and add it to the local dict
    # @param name key property under which name the module will be accessible (eg: if name='reader', you will have self.reader) - can be set = submod in most cases
    # @param submod name of the subfolder/submodule where the subsubmodule/class resides
    # @param classname both the subsubmodule filename (eg: classname.py) and the class name (eg: ClassName)
    # @param listofclasses if True, instanciate this class in a list of classes, instead of just directly a property of the current object (eg: instead of self.reader, you will get: self.reader["firstparser"], self.reader["secondparser"], etc...)
    def addclass(self, name, submod, classname, listofclasses=False):
        try:

            # Import the class dynamically
            aclass = import_class('.'.join([self.rootdir, submod, classname.lower()]), classname)
            # If we have several classes, we append all of them in a subdict of the attribute assigned for this module ( eg: runner.MyModule[firstclass] )
            if listofclasses:
                # Create the attribute as an OrderedDict if it does not exist yet
                if self.__dict__.get(name) is None: self.__dict__[name] = OrderedDict() # keep the order in which the items were given (all iterators will also follow the order). This allows to set in config the order in which we want the items to be executed.

                # Managing several calls to the same class: if we try to call twice the same class (eg: DropEmptyFeatures) for example at the beginning of PreOptimization and also at the end, there will be only one call because we are using a dict to store the classes. Here we try to avoid that by renaming the class by appending a number at the end.
                # If the class does not already exist in the dict, we can use the name as-is
                if not classname.lower() in self.__dict__[name]:
                    self.__dict__[name][classname.lower()] = aclass(config=self.config, parent=self)
                # Else the class already exists (and is called before in the routine), and thus we have to rename this one
                else:
                    count = 2
                    # Try to rename and increment the counter until we can store the class
                    while 1:
                        # Ok, this class name + current counter does not exist, we can store it
                        newclassname = "%s_%s" % (classname.lower(), str(count))
                        if not newclassname in self.__dict__[name]:
                            self.__dict__[name][newclassname] = aclass(config=self.config, parent=self)
                            break # exit the While loop
                        # Else we increment the counter and continue
                        else:
                            count += 1
            # Else we have only one class, we store it straight away in an attribute
            else:
                self.__dict__[name] = aclass(config=self.config, parent=self)
            return True
        except Exception, e:
            package_full = '.'.join([self.rootdir, submod, classname.lower()])
            print("CRITICAL ERROR: importing a class failed: classname: %s package: %s\nException: %s" % (package_full, classname, e.__repr__()))
            traceback.print_exc() # print traceback
            raise RuntimeError('Unable to import a class/module')

    ## Update the local dict vars of variables
    #
    # This function is used as a proxy to accept any arbitrary number of returned arguments from functions, and will store them locally, and then the vars dict will be passed onto other children objects
    def updatevars(self, dictofvars):
        # Create the local vars dict if it does not exist
        if not hasattr(self, 'vars'):
            self.vars = {}
        # Update/add the values inside dictofvars (if it is a dictionary of variables)
        if type(dictofvars) == type(dict()):
            self.vars.update(dictofvars) # add new variables from dict and merge updated values for already existing variables
        # Else, it may be a list or an object or just a scalar (this means the function is not conforming to the dev standards), then can't know where to put those results and we just memorize them inside a "lastout" entry as-is.
        # In summary: unnamed variables gets stored as temporary variables which may be overwritten at any time by subsequent functions
        else:
            # Delete the previous output
            if self.vars.get("lastout", None): del self.vars["lastout"]
            # Save this output
            self.vars.update({"lastout": dictofvars})

    ## Generically call one object and its method (if obj is a list, it will call the method of each and every one of the modules in the list)
    # @param obj Object or list of objects
    # @param method Method to call in the object(s) (as string)
    # @param args Optional arguments to pass to the method (must be a dictionary, with they keys being the name of the variables)
    # @param return_vars Return a value instead of updating the local vars dict
    # @param verbose Print more details about the executed routine
    # TODO: reduce the number of maintained dictionaries (there are 4: self.vars, allvars, dictofvars and args)
    # TODO: fix return_vars, it does work, but sometimes there is a bleeding effect (mixing up local variables and arguments variables. The best would be to use local variables where needed, but use argument variables foremost, and keep tracking of argument variables that are changed)
    def generic_call(self, obj, method, args=None, return_vars=False, verbose=False):
        # Create the local dict of vars
        allvars = dict() # input dict of vars
        if return_vars: dictofvars = dict() # output dict of vars (if return_vars is True)
        # Append the optional arguments to pass to methods
        if args is not None and type(args) == dict:
                    allvars.update(args)
                    if return_vars: dictofvars.update(args) # args and dictofvars must have ascendance over everything else when using return_vars
        # If we have a list of modules to call, we call the method of each and every one of those modules
        if isinstance(obj, (dict, OrderedDict)):
            # For every module in the list
            for submodule in obj.itervalues():
                # Print infos
                if verbose:
                    print("Routine: Calling module %s..." % submodule.__class__.__name__)
                    sys.stdout.flush()
                # Update the local dict of vars
                allvars.update(self.vars)
                if return_vars: allvars.update(dictofvars)
                # Get the callable object's method
                fullfunc = getattr(submodule, method)
                # Call the specified function for the specified module
                if not return_vars:
                    # By default we store in the local dict
                    self.updatevars(fullfunc(**allvars))
                else:
                    # Else we update a temporary dictofvars and we return it at the end
                    dictofvars.update(fullfunc(**allvars))
                # Force flusing the text into the terminal
                sys.stdout.flush()
            # Return the dictofvars at the end of the loop if the user wants to return the variables to the caller instead of storing them locally
            if return_vars:
                allvars.update(dictofvars) # return the input vars updated with the outputvars
                return allvars

        # Else if it is an object (thus only one module to call), we directly call its method
        else:
            # Print infos
            if verbose: print("Routine: Calling module %s..." % obj.__class__.__name__)
            # Get the callable object's method
            fullfunc = getattr(obj, method)
            # Update the local dict of vars
            allvars.update(self.vars)
            if return_vars: allvars.update(dictofvars)
            # Call the specified function for the specified module
            if not return_vars:
                self.updatevars(fullfunc(**allvars))
            else:
                allvars.update(fullfunc(**allvars)) # return the input vars updated with the outputvars
                return allvars
            # Force flusing the text into the terminal
            sys.stdout.flush()

    ## Execute a routine: call any module(s) given a list of dicts containing {"submodule name": "method of the class to call"}
    # @param executelist A list containing the sequence of modules to launch (Note: the order of the contained elements matters!)
    # @param verbose Print more details about the executed routine
    def execute(self, executelist, verbose=False):
        # Checking constraints first
        if not self.check_constraints():
            print("FATAL ERROR while checking constraints. Please check your configuration. Exiting.")
            return False

        # Loop through all modules in run_learn list
        for mod in executelist:
            # Catch exceptions: if a module fails, we continue onto the next one - TODO: try to set this option ("robust") in a config variable: for dev we want exceptions, in production maybe not (just a warning and then pass).
            #try:
            # Special case: this is a sublist, we run all the modules in the list in parallel
            if type(mod) == type(list()):
                self.generic_call(mod, verbose=verbose) # TODO: launch each submodule in parallel (using subprocess or threading, but be careful: Python's threads aren't efficient so this is not useful at all, and subprocess creates a new object, so how to communicate the computed/returned variables efficiently in memory?)
            else:
                # If it's a dict (specifying the module type and the method to call, format: {"moduletype":"method"})
                if isinstance(mod, dict):
                    # Unpacking the dict
                    module = mod.keys()[0]
                    func = mod.values()[0]
                # Else if it's a string, thus there's only the module type, we will call the default public method
                elif isinstance(mod, basestring):
                    module = mod # it's just a string, the name of the category of modules to call

                    # For the method it's a bit more tricky: we try to get the publicmethod, declared in the base class of each category of modules (and thus inherited by modules)
                    # Special case: we defined multiples modules to load in "classes" config for this category of modules, so we just get publicmethod from the first module in the dict
                    if isinstance (self.__dict__[module], (dict, OrderedDict)):
                        func = self.__dict__[module].itervalues().next().publicmethod
                    # Else it's a single module, we can get the publicmethod right away
                    else:
                        func = self.__dict__[module].publicmethod
                # Else it's not a recognized format, we pass
                else:
                    continue

                # Call the module's method
                self.generic_call(self.__dict__[module], func, verbose=verbose)

            #except Exception, e:
                #print "Exception when executing the routine: %s" % str(e)

            # Force flusing the text into the terminal
            sys.stdout.flush()

        return True

    ## Write down the parameters into a file
    # Format of the file: json structure consisting of a dict where the keys are the names of the vars, and the values are strings encoding the data in csv format
    # TODO: replace by pandas.to_json() when the feature will be put back in the main branch?
    @staticmethod
    def save_vars(jsonfile, dictofvars, exclude=None):
        ## Simple function to insert an item in either a dict or a list
        def addtolistordict(finaldict, key, item):
            if isinstance(finaldict, (dict)):
                finaldict[key] = item
            elif isinstance(finaldict, (list, tuple)):
                finaldict.insert(key, item)

        ## Recursively convert variables into a json intelligible format
        def convert_vars(dictofvars, exclude=None):
            # Loading the correct generator depending on the type of dictofvars
            # If it's a dict we iter over items
            if (isinstance(dictofvars, dict)):
                iter = dictofvars.iteritems()
                finaldict = dict()
            # If it's a list we enumerate it
            elif (isinstance(dictofvars, (list, tuple))):
                iter = enumerate(dictofvars)
                finaldict = list()

            # For each object in our dict of variables
            for (key, item) in iter:
                try:
                    # If this variable is in the exclude list, we skip it
                    if exclude and key in exclude:
                            continue
                # Try to save the pandas object as CSV
                #try:
                    # Only try if there is a method to_csv()
                    # TODO: replace by pandas.to_json() when the feature will be put back in the main branch?
                    if (hasattr(item, 'to_csv')):
                        out = StringIO.StringIO()
                        item.to_csv(out)
                        addtolistordict(finaldict, key, out.getvalue())
                    # Else it is probably not a Pandas object since this method is not available, we just save the value as-is or recursively convert pandas objects if possible
                    else:
                        # If possible, try to convert the item to a list
                        if (hasattr(item, 'tolist')):
                            item = item.tolist()
                        # If this is a recursive object, try to convert the variables inside (they may be pandas objects)
                        if (isinstance(item, (list, dict, tuple)) and not isinstance(item, basestring)):
                            addtolistordict(finaldict, key, convert_vars(item))
                        # Else just save the item as-is
                        else:
                            addtolistordict(finaldict, key, item)
                # Else if it is not a pandas object, we save as-is
                except Exception, e:
                    addtolistordict(finaldict, key, item)
                    print("Notice: couldn't correctly convert the value for the key %s. The value will be saved as-is. Error: %s" % (key, e))
                    pass

            return finaldict

        # Convert recursively the dict of vars
        finaldict = convert_vars(dictofvars, exclude)

        # Save the dict of csv data as a JSON file
        try:
            f = open(jsonfile, 'wb') # open in binary mode to avoid line returns translation (else the reading will be flawed!). We have to do it both at saving and at reading.
            f.write( json.dumps(finaldict, sort_keys=True, indent=4) ) # write the file as a json serialized string, but beautified to be more human readable
            f.close()
            return True
        except Exception, e:
            print("Exception while trying to save the parameters into the parameters file: %s. The parameters have not been saved!" % e)
            return False

    ## Load the parameters from a file
    # Format of the file: json structure consisting of a dict where the keys are the names of the vars, and the values are strings encoding the data in csv format
    # TODO: replace by pandas.from_json() when the feature will be put back in the main branch?
    # @param jsonfile Path to the json file containing the variables to load
    # @param prefixkey A prefix to prepend to the root keys (only for the root variables!)
    @staticmethod
    def load_vars(jsonfile, prefixkey=None):
        ## Simple function to insert an item in either a dict or a list
        def addtolistordict(finaldict, key, item):
            if isinstance(finaldict, (dict)):
                finaldict[key] = item
            elif isinstance(finaldict, (list, tuple)):
                finaldict.insert(key, item)

        ## Convert back variables and returns a dict
        # This is mainly because we need to convert back pandas objects, because pandas does not provide a to_json() function anymore
        # TODO: replace all this by a simple to_json() when it will be fixed in Pandas?
        # @param d Can be either a dict or a list
        # @param prefixkey A prefix to prepend to the root keys (only for the root variables!)
        def convert_vars(d, prefixkey=None, level=0):
            # Loading the correct generator depending on the type of dictofvars
            # If it's a dict we iter over items
            if (isinstance(d, dict)):
                iter = d.iteritems()
                dictofvars = dict()
            # If it's a list we enumerate it
            elif (isinstance(d, (list, tuple))):
                iter = enumerate(d)
                dictofvars = list()

            # For each item in the json
            for key, item in iter:

                # Prepend the prefix to key if specified, and if we are at the root (we don't prefix below)
                if prefixkey and isinstance(prefixkey, (basestring, str)) and level == 0:
                    key = prefixkey + key

                # TODO: Pandas objects are stored in a string for the moment because to_json() was removed. Fix this with a more reliable way to decode those structures in the future.
                if (isinstance(item, basestring)):
                    # Try to load a pandas object (Series or DataFrame)
                    try:
                        buf = StringIO.StringIO(item)
                        df = pd.read_csv(buf, index_col=0, header=0) # by default, load as a DataFrame
                        # if in fact it's a Series (a vector), we reload as a Series
                        # TODO: replace all this by pd.read_csv(buf, squeeze=True) when squeeze will work!
                        if df.shape[1] == 1:
                            buf.seek(0)
                            addtolistordict(dictofvars, key, pd.Series.from_csv(buf))

                            # Failsafe: in case we tried to load a Series but it didn't work well (pandas will failsafe and return the original string), we finally set as a DataFrame
                            if (type(dictofvars[key]) != type(pd.Series()) and type(dictofvars[key]) != type(pd.DataFrame()) or dictofvars[key].dtype == object ): # if it's neither a Series nor DataFrame, we expect the item to be a DataFrame and not a Series
                                addtolistordict(dictofvars, key, df)

                        # Else if it is really a DataFrame, we set it as DataFrame
                        else:
                            if (not df.empty):
                                addtolistordict(dictofvars, key, df)
                            # In the case it is really a string (the resulting pandas object is empty), we just store the string as-is
                            else:
                                addtolistordict(dictofvars, key, item)

                    # If it didn't work well, we load the object as-is (maybe it's simply a string)
                    except Exception, e:
                        addtolistordict(dictofvars, key, item)
                        print("Exception: couldn't correctly load the value for the key %s. Error: %s. This item will be skipped." % (key, e))
                        pass

                # Else it is already a converted Python object (eg: a list, a dict, a number, etc...), we just use it as-is
                else:
                    if isinstance(item, (dict, list, tuple)) and not isinstance(item, basestring):
                        addtolistordict(dictofvars, key, convert_vars(item, level=level+1))
                    else:
                        addtolistordict(dictofvars, key, item)

            return dictofvars


        # Open the file
        with open(jsonfile, 'rb') as f:
            filecontent = f.read()
        # Load the json tree
        jsontree = json.loads(filecontent)

        # Convert recursively the dict of vars (for pandas objects)
        dictofvars = convert_vars(jsontree, prefixkey)

        # Return the list of variables/parameters
        return dictofvars

    ## Check constraints integrity based on classes' definitions
    # This will NOT stop execution, but rather display a warning that integrity might not be safe and thus errors can be encountered in execution. But that might not be the case if the user knows what s/he's doing.
    def check_constraints(self):
        def constraint_error(submodname, constraint):
            print("WARNING: in submodule %s constraint %s is not satisfied! Please check your config." % (submodname, constraint))

        print("Checking constraints...")
        sys.stdout.flush()

        #== Checking workflow
        print("Checking constraints in workflow...")
        if self.vars['Mode'] == 'Learning':
            routine = self.config.get('workflow_learn')
        else:
            routine = self.config.get('workflow')

        prevmod = list() # list of the past modules
        # Iterate over all modules categories
        for mod in routine:
            # mod is an item of the routine, and it can either be a string (module category name), or a dict (modname + method)
            if isinstance(mod, (dict, OrderedDict)): # in this case, we need to unpack the name
                modname = mod.iterkeys().next() # unpack the key
            else: # else it's just a string, it's directly the name
                modname = mod
            # Get the module object
            module = self.__dict__[modname]
            # Little trick to do a for each loop in any case (in case we have only one submodule for this category of modules, or if we have a dict of submodules)
            if (isinstance(module, (dict, OrderedDict))):
                submods = module
            else: # only one submodule, we convert it do a dict
                classname = module.__class__.__name__.lower()
                submods = {classname: module}
            # For each submodule
            for submodname, submod in submods.iteritems():
                # If some constraints are set for this submodule
                if getattr(submod, 'constraints', None) is not None:
                    #-- Checking "after" constraint
                    if submod.constraints.get('after') is not None:
                        # If this submodule must be launched after another module, but this other module was not set before in the workflow, then warning
                        if submod.constraints['after'] not in prevmod:
                            constraint_error(submodname, "%s:%s" % ('after', submod.constraints['after']))

                # Add current submodule name into the list of past modules
                prevmod.append(submodname)
                # Flush output
                sys.stdout.flush()
            # Add current module category into the list of past modules
            prevmod.append(modname)


        return True


    ## Learning routine: Train the system to learn how to detect cheating
    def learn(self, executelist=None):
        # Specify the mode
        self.updatevars({'Mode': 'Learning'})
        self.config.update({'Mode': 'Learning'})

        # Reload the texts config
        if self.__dict__.get('reader', None):
            self.reader.reloadconfig() # make sure the textreader updates the list of texts it must load (depending on Mode)

        # We can pass an execution list either as an argument (used for recursion) or in the configuration
        if not executelist:
            executelist = self.config.get('workflow_learn', None)

        # Standard learning routine
        # If no routine is given, then we execute the standard learning routine
        if not executelist:
            executelist = []
            if self.__dict__.get('preprocessing', None):
                executelist.append({"preprocessing": "process"})
            executelist.append({"featuresextractor": "extract"})
            if self.__dict__.get('patternsextractor', None):
                executelist.append({"patternsextractor": "extract"})
            if self.__dict__.get('merger', None):
                executelist.append({"merger": "merge"})
            if self.__dict__.get('postprocessing', None):
                executelist.append({"postprocessing": "process"})

        # Initialization, do various stuff
        print("Initializing, this can take a few moments, please wait..."); sys.stdout.flush()

        # Execute all modules of the routine (either of config['workflow_learn'] or the standard routine)
        if not self.execute(executelist, verbose=True): # We generally prefer to print all infos when learning
            return False

        print('All done!')

        # End of learning, we save the parameters if a parametersfile was specified
        if self.config.get('parametersfile', None):
            Runner.save_vars(self.config.get('parametersfile'), self.vars, ['X', 'Y', 'X_raw', 'Weights', 'Mode']) # save all vars but X and Y (which may be VERY big and aren't parameters anyway)
            print('Learned parameters saved in: %s' % self.config.get('parametersfile'))

        return True

    ## Detection routine: identify the labels for the unlabeled texts
    def run(self, executelist=None):
        # Specify the mode
        self.updatevars({'Mode': 'Detection'})
        self.config.update({'Mode': 'Detection'})
        if self.__dict__.get('reader', None):
            self.reader.reloadconfig() # make sure the textreader updates the list of texts it must load (depending on Mode)

        # Load the parameters if a file is specified
        if self.config.get('parametersfile', None):
            self.updatevars(Runner.load_vars(self.config.config['parametersfile'], prefixkey='L_'))

        # We can pass an execution list either as an argument (used for recursion) or in the configuration
        if not executelist:
            executelist = self.config.get('workflow', None)

        # Standard detection routine
        # If no routine is given, then we execute the standard detection routine
        if not executelist:
            executelist = []
            if self.__dict__.get('preprocessing', None):
                executelist.append({"preprocessing": "process"})
            executelist.append({"featuresextractor": "extract"})
            if self.__dict__.get('patternsextractor', None):
                executelist.append({"patternsextractor": "extract"})
            if self.__dict__.get('postprocessing', None):
                executelist.append({"postprocessing": "process"})
            executelist.append({"detector": "detect"})

        # Execute all modules of the routine (either of config['workflow'] or the standard routine)
        if not self.execute(executelist, verbose=True): # We generally prefer to print all infos
            return False

        # End of identification, we save the results in a file if specified
        if self.config.get('resultsfile', None):
            Runner.save_vars(self.config.get('resultsfile'), {'Result': self.vars.get('Result'), 'Result_details': self.vars.get('Result_details')}) # save the Result and Result_details variable
            print('Identification results saved in: %s' % self.config.get('resultsfile'))

        return True

if __name__ == '__main__':
    runner = Runner()
    runner.init()
    runner.run()