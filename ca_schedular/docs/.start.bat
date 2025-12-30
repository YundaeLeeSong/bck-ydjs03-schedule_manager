@echo off
@REM ============================================================
@REM Script Name: start.bat
@REM Description: This script automates the following tasks:
@REM              1. ...
@REM              2. ...
@REM                 - ...
@REM                 - ...
@REM Usage: ...
@REM Author: Jaehoon Song
@REM Date: 2025-01-15
@REM ============================================================
SETLOCAL ENABLEDELAYEDEXPANSION





::===============================================================
::= Pre-script
::===============================================================
@REM @param
@REM < ANSI coloring >
@REM Usage:
@REM    TEST_FAIL (RED)     : echo %TEST_FAIL%texttexttext%RESET%
@REM    TEST_PASS (GREEN)   : echo %TEST_PASS%texttexttext%RESET%
@REM    USRPROMPT (YELLOW)  : echo %USRPROMPT%texttexttext%RESET%
@REM    DEBUG_SYS (BLUE)    : echo %DEBUG_SYS%texttexttext%RESET%
@REM    DEBUG_USR (CYAN)    : echo %DEBUG_USR%texttexttext%RESET%
set "RESET=[0m"
set "TEST_FAIL=[31m"
set "TEST_PASS=[32m"
set "USRPROMPT=[33m"
set "DEBUG_SYS=[34m"
set "DEBUG_USR=[36m"
@REM @param
@REM < Script Metadata References >
@REM Data Example:
@REM    SCRIPT_FULLPATH (e.g., "C:\path\to\script.bat")
@REM    SCRIPT_FILENAME (e.g., "script")
@REM    SCRIPT_NAMENEXT (e.g., "script.bat")
@REM    SCRIPT_DIR_PATH (e.g., "C:\path\to\")
set SCRIPT_FULLPATH=%0
set SCRIPT_FILENAME=%~n0
set SCRIPT_NAMENEXT=%~nx0
set SCRIPT_DIR_PATH=%~dp0
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: 0: return if in `repo`
@REM set CURR_DIR=%SCRIPT_DIR_PATH:~0,-1%
@REM set CURR_DIR=%CURR_DIR:~-5%
@REM if "%CURR_DIR%"=="\repo" (
@REM     echo %DEBUG_SYS%Move this %SCRIPT_NAMENEXT% to your own desktop.%RESET%
@REM     pause
@REM     exit /b 1
@REM )
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: 1: return if not `admin privilege`
@REM net session >nul 2>&1
@REM if errorlevel 1 (
@REM     echo This script must be run as an administrator.
@REM     echo Please 
@REM     echo #1. right-click the .bat file 
@REM     echo #2. select "Run as administrator".
@REM     echo.
@REM     echo.
@REM     pause
@REM     exit /b
@REM ) else (
@REM     echo Welcome!You are running in %TEST_PASS%administrator mode%RESET%.
@REM     pause
@REM )









@REM Find the path to git.exe
for /f "delims=" %%G in ('where git') do set "GIT_CMD_PATH=%%G"
@REM Navigate to the parent directory of git.exe and then the bin folder
set "GIT_PARENT_PATH=!GIT_CMD_PATH!\..\..\bin"
for %%G in ("!GIT_PARENT_PATH!") do set "GIT_BIN_PATH=%%~fG"
@REM Check if bash.exe exists in the bin folder
if exist "!GIT_BIN_PATH!\bash.exe" (
    echo !YELLOW!bash.exe found in !GIT_BIN_PATH!.!RESET!
    REM Add Git bin path to the PATH for the current session
    set "PATH=!PATH!;!GIT_BIN_PATH!"
    echo ------------------------------
    where bash
    echo ------------------------------
) else (
    echo "!GIT_BIN_PATH!"
    echo !RED!bash.exe not found. Something is wrong.!RESET!
    goto End
)



:: Define the location of the .bashrc file
set BASHRC_PATH=%USERPROFILE%\.bashrc
set README_PATH=%SCRIPT_DIR_PATH%\README.md
:: Check if the .bashrc file exists
if exist "%BASHRC_PATH%" (
    echo .bashrc exists at: %BASHRC_PATH%
    echo Opening the file...
) else (
    echo .bashrc not found.
    echo Creating a new one at: %BASHRC_PATH%
    (
        echo # ~/.bashrc
    ) > "%BASHRC_PATH%"
)
:: Pause to display the output
@REM call pause
:: Check if README_PATH exists, and if not, exit early
if not exist "%README_PATH%" (
    echo README.md does %TEST_FAIL%NOT exists%RESET%.
    echo It is %TEST_FAIL%NOT a repository%RESET%.
    pause
    exit /B
)

:: Open the repository based on README.md location asynchronously
start /B "" code "%SCRIPT_DIR_PATH%"

:: Wait for 2 seconds to ensure the command has time to initialize (adjust as needed)
timeout /t 2 /nobreak > nul

:: Open the .bashrc config file asynchronously
start "" "%BASHRC_PATH%"
start "" "%README_PATH%"

exit /B 0