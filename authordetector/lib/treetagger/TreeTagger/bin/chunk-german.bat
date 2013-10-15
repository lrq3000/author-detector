@echo off

set TAGDIR=C:\TreeTagger

set BIN=%TAGDIR%\bin
set CMD=%TAGDIR%\cmd
set LIB=%TAGDIR%\lib
set TAGOPT=%LIB%\german.par -quiet -token -lemma -sgml -no-unknown
set CHUNKOPT=%LIB%\german-chunker.par -token -sgml -eps 0.00000001 -hyphen-heuristics
set OPT=-nae "if ($#F==0){print}else{print \"$F[0]-$F[1]\n\"}"

if "%2"=="" goto label1
perl %CMD%\tokenize.pl -a %LIB%\german-abbreviations "%~1" | %BIN%\tree-tagger %TAGOPT% | perl %OPT% | %BIN%\tree-tagger %CHUNKOPT% | perl %CMD%\filter-chunker-output.perl | %BIN%\tree-tagger %TAGOPT% > "%~2"
goto end

:label1
if "%1"=="" goto label2
perl %CMD%\tokenize.pl -a %LIB%\german-abbreviations "%~1" | %BIN%\tree-tagger %TAGOPT% | perl %OPT% | %BIN%\tree-tagger %CHUNKOPT% | perl %CMD%\filter-chunker-output-german.perl | %BIN%\tree-tagger %TAGOPT%
goto end

:label2
echo.
echo Usage: chunk-german file {file}
echo.

:end
