REM Help
C:\Python27\python.exe authordetector.py --help
pause
REM Learning phase
C:\Python27\python.exe authordetector.py --learn -c config.json --textconfig textconfig.json -p parameters.txt
pause
REM Detection phase (can be launched directly if you already generated a parameters.txt)
C:\Python27\python.exe authordetector.py -c config.json -p parameters.txt --textconfig_detection textconfig_detection.json
pause
