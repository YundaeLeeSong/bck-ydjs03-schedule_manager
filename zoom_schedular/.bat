@echo off
:: ============================================================
:: Script Name  : start.bat
:: Description  : Automates project setup by loading custom functions and:
::                1. Validating administrator privileges
::                2. Detecting Git repository
::                3. Locating Git Bash and adding to PATH
::                4. Ensuring ~/.bashrc exists
::                5. Opening project and key files
:: Usage        : Run this script from the project root directory.
:: Author       : Jaehoon Song
:: Date         : 2025-05-15
:: Notes        : Delegates all business logic to functions.bat
:: ============================================================
SETLOCAL EnableDelayedExpansion


:: ----------------------------------------------------------------
:: ANSI color definitions (used for logging/error output)
:: ----------------------------------------------------------------
set "COLOR_RESET=[0m"
set "COLOR_FAIL=[31m"    :: Red
set "COLOR_PASS=[32m"    :: Green
set "COLOR_INFO=[33m"    :: Yellow
set "COLOR_DEBUG=[34m"   :: Blue
set "COLOR_TRACE=[36m"   :: Cyan

:: ----------------------------------------------------------------
:: Locate and load user-defined functions
:: ----------------------------------------------------------------
set "SCRIPT_DIR=%~dp0"

:: ----------------------------------------------------------------
:: Main Execution Flow
:: ----------------------------------------------------------------
@REM call :requireAdmin          || exit /b 1
@REM call :isGitRepo             || exit /b 1
call :addGitBashToPath      || exit /b 1
call :ensureBashrc          || exit /b 1
call :openFiles "%SCRIPT_DIR%" || exit /b 0

endlocal
exit /b 0












::-----------------------------------------------------------------
:: Function: requireAdmin
:: Ensures script is running with admin privileges.
:: Returns 0 if admin, else exits with code 1.
::-----------------------------------------------------------------
:requireAdmin
    net session >nul 2>&1
    if errorlevel 1 (
        echo %COLOR_FAIL%ERROR:%COLOR_RESET% Administrator privileges required.
        pause
        exit /b 1
    ) 
    rem no output on success
    exit /b 0

::-----------------------------------------------------------------
:: Function: isGitRepo
:: Verifies current SCRIPT_DIR is a Git repository (contains .git).
:: Returns 0 if yes, else exits with code 1.
::-----------------------------------------------------------------
:isGitRepo
    if exist "%SCRIPT_DIR%\.git" (
        rem OK: .git folder found
        exit /b 0
    ) else (
        echo %COLOR_FAIL%ERROR:%COLOR_RESET% '%SCRIPT_DIR%' is not a Git repository.
        pause
        exit /b 1
    )

::-----------------------------------------------------------------
:: Function: addGitBashToPath
:: Locates Git’s bash.exe and appends its bin folder to PATH.
:: Returns 0 on success, else exits with code 1.
::-----------------------------------------------------------------
:addGitBashToPath
    rem find git.exe
    for /f "delims=" %%G in ('where git 2^>nul') do set "GIT_CMD=%%~G"
    if not defined GIT_CMD (
        echo %COLOR_FAIL%ERROR:%COLOR_RESET% git.exe not found in PATH.
        pause
        exit /b 1
    )

    rem derive bin folder from git.exe location
    for %%H in ("%GIT_CMD%") do (
        set "GIT_ROOT=%%~dpH.."
    )
    set "GIT_BIN=%GIT_ROOT%\bin"

    rem verify bash.exe exists
    if exist "%GIT_BIN%\bash.exe" (
        set "PATH=%PATH%;%GIT_BIN%"
        exit /b 0
    ) else (
        echo %COLOR_FAIL%ERROR:%COLOR_RESET% bash.exe not found under '%GIT_BIN%'.
        pause
        exit /b 1
    )

::-----------------------------------------------------------------
:: Function: ensureBashrc
:: Creates the user’s ~/.bashrc if missing.
:: Returns 0 always.
::-----------------------------------------------------------------
:ensureBashrc
    set "BASHRC=%USERPROFILE%\.bashrc"
    if not exist "%BASHRC%" (
        > "%BASHRC%" echo "# ~/.bashrc (generated on %DATE%)"
    )
    exit /b 0

::-----------------------------------------------------------------
:: Function: openFiles
:: Opens VS Code on project dir and launches .bashrc & README if present.
:: Param %1 = project directory (with trailing backslash)
:: Returns 0.
::-----------------------------------------------------------------
:openFiles
    set "PROJECT_DIR=%~1"
    start "" code "%PROJECT_DIR%"
    rem open .bashrc in default editor

    :: Wait for 2 seconds to ensure the command has time to initialize (adjust as needed)
    timeout /t 2 /nobreak > nul

    start "" "%BASHRC%"
    rem open README.md if exists
    if exist "%PROJECT_DIR%README.md" (
        start "" "%PROJECT_DIR%README.md"
    )
    exit /b 0
