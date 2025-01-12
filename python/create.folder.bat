:: @echo off

:: Store the original directory and variables
@setlocal enableextensions
@cd /d "%~dp0"

:: Check for administrative rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    powershell start -verb runas "%~dpnx0"
    exit /b
)

:: Make portable models folder instead of system disk
set myDIR="C:\Users\%USERNAME%\.cache"
rmdir /S /Q "%myDIR%\vosk"
IF not exist "%myDIR%" (mkdir "%myDIR%")
mklink /D "%myDIR%\vosk" "%cd%\models\vosk"
