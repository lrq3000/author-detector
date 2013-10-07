## @mainpage AuthorDetector developer's documentation
#  @section intro_sec Introduction
#  AuthorDetector is a framework to quickly develop, experiment and prototype author identification models.
#
# The main purpose of this project is to be:
# - Modular: can just create new algorithms and modules without even knowing how other modules work.
# - Reusable: no need to recode preprocessors, readers, featuresextractor and postprocessors, you just focus on your new algorithm.
# - Flexible: you can create new modules, replace any module in the workflow or even change the entire workflow by creating new modules categories.
# - Low overhead: you don't have to care about usual repetitive stuff like how to set a new variable in the config or how the learned parameters will be saved and reloaded, most of those "administrative" stuff are automated.
# - User-friendly: you can easily define new config variables using myvar = self.config.get("myvar"), without having to define anything outside the scope of your own module. There is also a nice GUI thank's to IPython Notebook, and the application can also be fully scripted in a user's Python script.
# - Simple and tiny: the core framework consists of only a few python scripts with few methods and functions, easily comprehensible and extendable if you need to.
#
# @section overview_sec Overview
#
# The Framework is a set of a few core modules that are necessary for functionning and cannot be replaced, which are all the scripts placed at the root of the "authordetector" subfolder, mainly:
# - run.py which is the main Runner script (will run everything neatly given a configuration file and output the results). This is the main manager script. It also manages the global namespace of variables and modules. This is the "glue" of all the other (core and workflow) modules.
# - main.py which is the commandline entry point of the program and will launch the desired functionalities.
# - configparser.py which contains ConfigParser and manage all the configuration. This object is instanciated by Runner and then referenced inside all modules thank's to Base class, so that any module can access the whole configuration file at any moment (and thus declare very simply its very own configuration parameters).
# - base.py which is the base class that all classes/modules must inherit from to get the basic functionnalities like access to the config file and parent class. However, you will generally prefer to inherit from the specific base class of your type of module (eg: basepostaction/basepostaction.py)
# - auxlib.py which provides a few important functions (mainly to import modules while catching errors and to import classes generically).
#
# Apart from these base core modules, there is what we call the Workflow, which consists of all the other modules that are placed inside subfolders (the subfolder represent the type of functionality they implement). Currently these types are available (ordered by the standard workflow):
# - reader: read and parse the text files.
# - preprocessor: optimizations on the raw text that will always be applied before the learning process or detection process, directly on the texts (eg: stopwords filtering, xml stripping, etc.).
# - featuresextractor: given a text by the reader, extract raw features that will be used to form patterns later (eg: text split into a list of words, a list of lemmas, a list of grammatical categories of words, etc..). This kind of module should always return a list of items per text.
# - patternsextractor: given a list of features, extract patterns (eg: ngrams from a list of words). This module should return a list of patterns per text.
# - merger: merge patterns list of multiple text into one if they share the same label.
# - postprocessor: optimizations of the parameters after the learning process (eg: filter ngrams with low score below the mean, compute tf-idf instead of raw frequencies, etc.).
# - detector: (should be renamed to identification) given a list of learned patterns tables from labeled texts, and a patterns table for an unlabeled text, match the similarity between the unlabeled patterns table and the learned patterns table (ie: try to find the learned patterns table that is the most similar to the unlabeled text) (eg: cosine similarity).
# - lib: not really modules, this folder contains auxiliary libraries (eg: debug, argparse, TreeTagger).
#
#
# Then inside these folders you will find the modules, which all share the same public entry points (same public methods, thus the access is the same but the functionality provided varies per module).
#
# One thing you need to know is that you can specify completely how you want the program to run, and what algorithms to use, and in which order, directly in the configuration file (see below the related chapter for more infos).
#
# An important note is about the configuration file and commandline arguments: they are all shared and accessible to all modules, and are considerated the same (except that commandline arguments have precedence over configuration file).
# This mean that you can use any configuration parameter as a commandline argument, and vice versa (except for the configuration file location: you need to specify it at commandline).
#
# Another important note is about the variables management: all the variables returned by modules are stored in a kind of protected namespace, which is a global namespace inside Runner.
# Indeed, all variables are accessible inside runner.vars (eg: runner.vars['X']), and will be propagated to all other modules and methods.
#
# @section createkindmodule_sec Create your own kind of module
#
# It is very easily possible to create a new kind of module: all you need to do is:
# - create a new subfolder inside "authordetector", eg "newkind".
# - create an __init__.py file at the root of the folder "newkind" (you can leave it empty or just put a #, it's just used for Python to recognize your new folder as a Python submodule).
# - create a base class with the name "base" + name of the subfolder (eg: "basenewkind.py") and create a new class inside with the same name as the python file (eg: "BaseNewKind") and inherit from BaseClass (authordetector/base.py). To get done with this quicker and more easily, you can copy the base class from another module and just change to the appropriate names.
# - define 1 or 2 public generic methods that will be accessed for learning, and the second one for prediction (some modules do need only one public access, like postaction which only requires the method "action"). This is necessary for the software to be generic, thus modules need to implement public and generic entry points that provide the same "broad concept functionality".
#
# Then in these modules folders, will find several modules, each with a different name and purpose.
#
# @section createmodule_sec Create your own module
#
# If you want to create your own module, you simply have to:
# - make a new python file in the appropriate subfolder (eg: "newkind/mynewmodule.py")
# - create, inside this file, a class with the same name (but not necessarily the same case, eg: "class MyNewMODULE")
# - you must then implement in your class at least the public generic methods that the base class implements.
#
# @section configuration_sec Configuration
#
# AuthorDetector main modules (ie: Runner, ConfigParser) provide a few main configuration parameters, but then each module can specify its own.
#
# Please refer to the documentation of the module if you want to know more about the configuration parameters you can use.
#
# Here is a non-exhaustive list of AuthorDetector main configuration parameters:
# - run: routine to be used at detection (list of modules and their methods to call) - order matters!
# - run_learn: routine to be used at learning (list of modules and their methods to call) - order matters!
# - classes: list of modules to load (Note that you can load more classes and not use them in run or run_learn! They will be then preloaded and available for manual introspection and usage).
# - textconfig: list of text files to use for learning, with file path and labels
# - textconfig_detection: path to the unlabeled text files to identify.
# - parametersfile: where the parameters will be saved after learning, and later loaded for detection
#
# @section variables_sec Variables management
#
# At some point of the project, one of the biggest problem was: how to return variables in a way that they are generically handled and passed to the correct methods and modules that needs them, but with keeping clear methods declaration (ie: which variables are required by a method) and without having a too big overhead on the methods nor in memory (ie: no duplication).
#
# The solution adopted was to use a global, private namespace managed by Runner (in runner.vars), shared by reference to all submodules, and which was managed directly by submodules instead of the main Runner framework.
#
# In fact, to be totally precise, submodules don't get a reference to the global variables manager: variables are unpacked when calling the methods of the submodules. This has a triple advantage: first it keeps the genericity that was wanted, secondly it forces to use keyword arguments and thus the classes become inheritables, thirdly and foremost it allows to keep clear definitions of the variables required by the methods (eg: mymethod(X=None, Y=None, *args, **kwargs)), and thus even with the genericity, the methods still stay faithful to the python idiomatic of keeping things clear.
#
# However, this requires that submodules methods return a dict of vars, and not just a variable alone nor a list (see below in chapter Advices and guidelines for an example). Other kind of objects than dict of vars will be stored but temporarily under a placeholder name (runner.vars['lastout1]), because there is no label to assign them to and to propagate to other modules. But this is a meager payback for this simple and elegant solution.
#
#
# @section interactive_sec Interactive GUI
#
# You can load and use AuthorDetector in a IPython Notebook GUI.
#
# All you need to do is install a recent IPython release (which contains notebooks), and launch AuthorDetector with these arguments:
#
# python authordetector.py --interactive
#
# A webpage should open in your browser and you can then use one of the notebooks to run authordetector just by clicking, everything is done for you.
#
# If it doesn't work or you have troubles installing all the required libraries, you can try a scientific Python distribution like Canopy, and then just open the file ipynb/AuthorDetector.ipynb inside Canopy.
#
# The main interest for this GUI is foremost to test the datas or results or to develop your own algorithms directly in this GUI, and then porting the code to your own module once it's working (that's what I did for most modules). Example codes are offered to help you.
#
# @section advices_sec Advices and guidelines
# - This project rely heavily on Pandas and Numpy, and it is advised that you use Pandas objects whenever possible.
# - Always inherit from the base class of your kind of module (eg: basepostaction.py). If you create a new category of modules, first create the base class and inherits from the general base class base.py.
# - For public methods (that will be accessed from outside or by Runner), ALWAYS use keywords arguments + variable positional and keyword arguments.
# Eg:
#
# def mymethod(X, Y): # this is not good at all, it won't work
#   pass
#
# def mymethod(X=None, Y=None, *args, **kwargs): # this will work and will be inheritable and overloadable
#   pass
#
# - If you want your returned values to be memorized in the Runner's global namespace (thus accessible to other modules) and saved in the parameters file, return your variables in a dictionary.
# Eg:
#
# return myvalue # won't work, the value will not be stored nor accessible to other modules
#
# return {'Myvalue': myvalue} # This will be stored and accessible in runner.vars['Myvalue']
#
# - Prefer to use dict() or Pandas Series/DataFrame instead of list() whenever possible (and at all levels use recursive dict() inside a dict() instead of recursive list()), especially if it's a variable you want to store in the Runner, because list() do not allow to iterate over the keys (with enumerate() you get a new sequence of numbers but not in the same order, with dict() you can always fetch the original keys). Most classes expect X and Patterns to be dict() of DataFrames.
# - At detection/identification phase, learned parameters are reloaded under another name: their old name prepended with 'L_' (eg: 'Patterns' becomes 'L_Patterns'). This is made to ensure that you can both use the learned variables and variables of texts to be identified at the same time, without any collision.
# - You can reuse your methods without inheriting if your method is generic enough (eg: a mathematical computation). Just add "@staticmethod" above the method to call it whenever you want. You can see such an example in postprocessor TermFrequency.tf(), which is used in postprocessor FilterLowCount.
#
#
#  @section license_sec License
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
#