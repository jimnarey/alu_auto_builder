@echo off

if [%1] == [] GOTO Syntax


debugfs -R 'rdump / save_part_contents' save.img

GOTO END

:Syntax

echo You must provide the tempdir root for the extract operation

:END