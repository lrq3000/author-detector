@echo off

set TAGDIR=C:\TreeTagger

set BIN=%TAGDIR%\bin
set CMD=%TAGDIR%\cmd
set LIB=%TAGDIR%\lib
set TAGOPT=%LIB%\english.par -token -lemma -sgml -no-unknown

if "%2"=="" goto label1
perl %CMD%\tokenize.pl -e -a %LIB%\english-abbreviations "%~1" | %BIN%\tree-tagger %TAGOPT% > "%~2"
goto end

:label1
if "%1"=="" goto label2
perl %CMD%\tokenize.pl -e -a %LIB%\english-abbreviations "%~1" | %BIN%\tree-tagger %TAGOPT% 
goto end

:label2
echo.
echo Usage: tag-english file {file}
echo.

:end
