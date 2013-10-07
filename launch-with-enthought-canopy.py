#!/usr/bin/env python
# encoding: utf-8

# Launch the application if you installed Enthought Canopy Express
# NOTE: do NOT launch this python script from Canopy Editor, it will fail because it already launch its own instance of IPython, and you can't launch a different one from inside! (you will get MultipleInstanceError).

import sys
import getpass
from subprocess import call, check_output

if sys.platform == 'win32' or sys.platform == 'cygwin':
    username = getpass.getuser()
    cmd1 = 'C:\Users\\'+username+'\AppData\Local\Enthought\Canopy\User\Scripts\python.exe'
    cmd2 = 'C:\Users\\'+username+'\AppData\Local\Enthought\Canopy32\User\Scripts\python.exe'

elif sys.platform == 'linux2' or sys.platform == 'linux' or sys.platform == 'generic':
    cmd1 = r'~/Enthought/Canopy_64bit/User/Scripts/python'
    cmd2 = r'~/Enthought/Canopy_32bit/User/Scripts/python'

elif sys.platform == 'mac' or sys.platform == 'darwin':
    cmd1 = r'~/Library/Enthought/Canopy_64bit/User/Python'
    cmd2 = r'~/Library/Enthought/Canopy_32bit/User/Python'

# Get current working directory
import inspect, os
filename = inspect.getframeinfo(inspect.currentframe()).filename
basepath = os.path.dirname(os.path.abspath(filename))

# Python script command
command = [os.path.join(basepath,'authordetector.py'), '--interactive']

if os.path.exists(cmd1):
    cmd = [cmd1]
    cmd.extend(command)
    print('AAA')
elif os.path.exists(cmd2):
#    return_code = call(cmd2+' '+command, shell=True)
    cmd = [cmd2]
    cmd.extend(command)

#out = check_output(os.path.join(basepath,'test.py')+' --test', shell=True)
#out = check_output(' '.join(cmd), shell=False)
rtncode = call(' '.join(cmd), shell=False)
print(rtncode)
#import authordetector.main
#process = Process(target=authordetector.main.main, args=('--interactive'))
#process.start()
