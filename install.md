INSTALL INSTRUCTIONS
===================

To use this software, you need a few popular scientific libraries, but which can be hard to install.

First, you need to use Python 2.7 (Python 3 is unsupported at the moment).

Then you can install the required libraries. There are several ways to install them in order to use this software:

PythonXY (Windows only)
--------------------------------------

Python(x,y) is a Python distribution packaged with a lots of scientific libraries, with every conflicts already resolved for you.

This solution works only if you run a Windows OS.

You can install Python(x,y) from https://code.google.com/p/pythonxy/wiki/Downloads

To make sure everything works as intended, you should download the version 2.7.5.0, which contains all the required libraries and with about the same versions that were used during development.

There is also an experimental port to Linux: https://code.google.com/p/pythonxy-linux/

Enthought Canopy Express (ex EPD Free)
-------------------------------------------------

Enthought Canopy Express is similar to Python(x,y) but contains a lot less libraries (but it still contains everything that is necessary to run this software).

However, it is cross-platform and works on Windows, Linux and MacOSX.

You can get a copy here:
https://www.enthought.com/products/epd/free/

or here:
https://www.enthought.com/downloads/

After installing ECE, you MUST update (as of 2013-08) the IPython package if you want to use the --interactive option, else it will crash (the packaged ipython is too buggy).
To do that, simply open the "Canopy" software, then go in "Package Manager", search for "ipython", click on it to highlight it, then click on the "Show more info" button just below the package name, and then at the bottom of the package manager window, click on the "Show" button beside "There are xx versions of this package".
Finally, select ipython 0.13.1 (which is the one that was used in the development environment), or any later version if you would like to try.

Finally, you can either use the software using the gui, or by commandline.

-> By GUI:

Simply launch the "Canopy" application software, and then open the Editor. Inside, you just have to load the file "authordetector/ipynb/*.nb" (meaning any .nb file inside the authordetector/ipynb folder), and it should open the notebook inside the Canopy Editor. Make sure to execute the code to change the current working directory.

-> By commandline:

You need to make sure that you launch the software with the right Python interpreter (ECE provides 3 different layers of Python - you must use the User layer, then it will automatically fall back to the other layers if needed).
For more information about these layers and where to find the User layer on any supported platform:
http://docs.enthought.com/canopy/configure/faq.html

As an example, on Windows 7, you will need to use something like this:
C:\Users\User_Name_Here\AppData\Local\Enthought\Canopy\User\Scripts\python.exe authordetector.py --interactive

You can also launch from a terminal the file called "launch-with-enthought-canopy.py", which should automate the finding of the right python executable.
BEWARE: it won't work if you run it from inside the Canopy Editor! This is because Canopy already launch its own instance of IPython. Therefore, you must launch this script from a terminal outside of Canopy.

Continuum Analytics' Anaconda distribution
---------------------------------------------------------------

Similar to Canopy Express, this is a Python distribution packaged with a lot of scientific libraries. Available for Linux, Windows and MacOSX, so feel free to try it if Canopy Express does not suit you.

Package manager (SnakeBasket using Pip)
----------------------------------------------------------------

This solution works best on Linux, but should be cross-platform.

You can try to use the provided package manager to install all the required libraries from source.

The process should be totally automatic, and is cross-platform, BUT is not guaranteed to work, because since you will compile from source, it may require you to install some libraries and tools (like gcc or mingw) before being able to compile these.

To use this method, just do:

cd authordetector/install/
python install-dependencies.py

Also, if you have Git installed and would like to resolve recursively all dependencies, you can edit the requirement.txt file and uncomment the first lines (and comment all the other ones). SnakeBasket (a wrapper around Pip) will take care of git cloning and fetch recursively all necessary required dependencies.

Manual install
--------------------

As a last resort, you can try to install each library by yourself, by crawling the "requirements.txt" list and downloading and then installing each library, one-by-one (and in the order in requirements.txt, else you will run into troubles).

This works particularly well for platforms where you can find installers or packages, like Linux (using an external package manager such as dpkg or rpm for example), or Windows, particularly by downloading packages from y Christoph Gohlke's website:
http://www.lfd.uci.edu/~gohlke/pythonlibs/

