@echo off

if [%1] == [] GOTO Syntax
if [%2] == [] GOTO Syntax

debugfs.exe -R 'rdump / %2' %1

GOTO END

:Syntax

echo You must provide an input UCE and a target directory

:END