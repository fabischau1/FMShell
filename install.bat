@echo off
:main
echo hello do you want to install this programm (you need to install python)
set /p input1=
if /i %input1%==Yes goto checktos
if /i %input1%==No goto dontinstall
:checktos
echo just asking did you read the terms of service? type Yes if Yes and No if NO
set /p input=
if /i %input%==Yes goto install
if /i %input%==No goto TOS
:install
mkdir "C:\FMShell"
mkdir "C:\FMShell\settings"
python -c "import urllib.request; urllib.request.urlretrieve('https://fabischau1.github.io/FMShell/FMShell.py', r'C:\FMShell\FMShell.py')"
echo Progress: [==--------] 20% 
timeout /t 1 >nul
cls
python -c "import urllib.request; urllib.request.urlretrieve('https://fabischau1.github.io/FMShell/icon.ico', r'C:\FMShell\icon.ico')"
echo Progress: [====------] 40% 
timeout /t 1 >nul
cls
python -c "import urllib.request; urllib.request.urlretrieve('https://fabischau1.github.io/FMShell/README.md', r'C:\FMShell\README.md')"
echo Progress: [======----] 60% 
timeout /t 1 >nul
cls
python -c "import urllib.request; urllib.request.urlretrieve('https://fabischau1.github.io/FMShell/LICENSE.md', r'C:\FMShell\LICENSE.md')"
echo Progress: [========--] 80% 
timeout /t 1 >nul
cls
python -c "import urllib.request; urllib.request.urlretrieve('https://fabischau1.github.io/FMShell/TOS.html', r'C:\FMShell\TOS.html')"
echo Progress: [==========] 100% 
timeout /t 1 >nul
cls
set shortcut_path="%USERPROFILE%\Desktop\FM Shell.lnk"
set target_path="C:\FMShell\FMShell.py"
set icon_path="C:\FMShell\icon.ico"
python -c "import os; import winshell; shortcut = winshell.shortcut(); shortcut.path = r'C:\FMShell\FMShell.py'; shortcut.icon_location = r'C:\FMShell\icon.ico'; shortcut.write(r'%USERPROFILE%\Desktop\FM Shell.lnk')"
cls
echo installation complete
pause
exit

:checktos
start https://fabischau1.github.io/FMShell/TOS.html
goto main

:dontinstall
echo sorry to hear that :(
echo well i hope you still have a great day ;)
pause
exit