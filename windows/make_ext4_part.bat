@echo off

if [%1] == [] GOTO Syntax

echo %1

@REM truncate.exe -s 4M %1

@REM mke2fs.exe -t ext4 %1

@REM debugfs.exe -R "mkdir upper" -w %1

@REM debugfs.exe -R "mkdir work" -w %1

%~dp0truncate.exe -s 4M %1

%~dp0mke2fs.exe -t ext4 %1

%~dp0debugfs.exe -R "mkdir upper" -w %1

%~dp0debugfs.exe -R "mkdir work" -w %1

GOTO END

:Syntax

echo You must provide a target filename

:END
