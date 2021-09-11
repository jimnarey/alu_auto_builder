@echo off

if [%1] == [] GOTO Syntax

echo %1

truncate.exe -s 4M %1

mke2fs.exe -t ext4 %1

debugfs.exe -R "mkdir upper" -w %1

debugfs.exe -R "mkdir work" -w %1

GOTO END

:Syntax

echo You must provide a target filename

:END
