@echo off
::-----------------------------------------------------------------------------
:: Script Name : start.bat
:: Description : Automates repository setup:
::               1. Verifies administrator privileges
::               2. Locates Git Bash and updates PATH
::               3. Ensures a user .bashrc exists
::               4. Validates repository presence via README.md
::               5. Opens repository and config files in VS Code
::
:: Usage       : Double‑click or run from CLI
:: Author      : Jaehoon Song
:: Date        : 2025-01-15
::-----------------------------------------------------------------------------

SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

::=== ANSI Color Codes =========================================================
SET "COLOR_RESET=[0m"
SET "COLOR_FAIL=[31m"
SET "COLOR_PASS=[32m"
SET "COLOR_WARN=[33m"
SET "COLOR_INFO=[34m"

::=== Script Metadata =========================================================
SET "SCRIPT_PATH=%~f0"
SET "SCRIPT_NAME=%~n0"
SET "SCRIPT_DIR=%~dp0"

::=== Main Execution ===========================================================
CALL :CheckAdmin             :: Ensure elevated privileges
CALL :FindGitBash            :: Locate Git Bash and add to PATH
CALL :EnsureBashrc           :: Create or confirm ~/.bashrc
CALL :ValidateRepository     :: Verify README.md exists
CALL :OpenFiles              :: Launch VS Code and config files

ENDLOCAL
EXIT /B 0

::==============================================================================
:: Function : CheckAdmin
:: Purpose  : Exit if not running with administrator rights
::==============================================================================
:CheckAdmin
    NET SESSION >NUL 2>&1
    IF ERRORLEVEL 1 (
        echo %COLOR_FAIL%Administrator privileges required.%COLOR_RESET%
        echo Right-click "%SCRIPT_NAME%.bat" and select "Run as administrator".
        PAUSE
        EXIT /B 1
    ) ELSE (
        echo %COLOR_PASS%Administrator mode OK.%COLOR_RESET%
    )
    GOTO :EOF

::==============================================================================
:: Function : FindGitBash
:: Purpose  : Locate git.exe, ensure bash.exe is present, update PATH
::==============================================================================
:FindGitBash
    FOR /F "usebackq delims=" %%G IN (`where git 2^>nul`) DO SET "GIT_PATH=%%G"
    IF NOT DEFINED GIT_PATH (
        echo %COLOR_FAIL%git.exe not found in PATH.%COLOR_RESET%
        EXIT /B 1
    )
    FOR %%G IN ("%GIT_PATH%\..\..\bin") DO SET "GIT_BIN=%%~fG"
    IF EXIST "%GIT_BIN%\bash.exe" (
        echo %COLOR_INFO%Found bash at "%GIT_BIN%\bash.exe"%COLOR_RESET%
        SET "PATH=%PATH%;%GIT_BIN%"
    ) ELSE (
        echo %COLOR_FAIL%bash.exe not found in "%GIT_BIN%".%COLOR_RESET%
        EXIT /B 1
    )
    GOTO :EOF

::==============================================================================
:: Function : EnsureBashrc
:: Purpose  : Create .bashrc in user profile if missing
::==============================================================================
:EnsureBashrc
    SET "BASHRC=%USERPROFILE%\.bashrc"
    IF NOT EXIST "%BASHRC%" (
        echo %COLOR_WARN%Creating "%BASHRC%"%COLOR_RESET%
        (echo "# ~/.bashrc initialized by start.bat")>"%BASHRC%"
    ) ELSE (
        echo %COLOR_INFO%"%BASHRC%" already exists.%COLOR_RESET%
    )
    GOTO :EOF

::==============================================================================
:: Function : ValidateRepository
:: Purpose  : Confirm repository by checking for README.md
::==============================================================================
:ValidateRepository
    SET "README=%SCRIPT_DIR%README.md"
    IF NOT EXIST "%README%" (
        echo %COLOR_FAIL%Not a repository: "%README%" missing.%COLOR_RESET%
        PAUSE
        EXIT /B 1
    )
    GOTO :EOF

::==============================================================================
:: Function : OpenFiles
:: Purpose  : Launch VS Code workspace and open config files
::==============================================================================
:OpenFiles
    start "" code "%SCRIPT_DIR%"    :: Open project in VS Code
    TIMEOUT /T 2 /NOBREAK >NUL          :: Wait for VS Code to load
    start "" "%BASHRC%"               :: Open .bashrc
    start "" "%README%"              :: Open README.md
    GOTO :EOF
