@echo off
:: Ensure the script is running with administrative privileges
openfiles >nul 2>&1
if '%ERRORLEVEL%' NEQ '0' (
    echo This script requires administrative privileges.
    echo Please right-click on the script and select 'Run as administrator'.
    pause
    exit /b 1
)

:: Install Chocolatey if not installed
choco -v >nul 2>&1
if '%ERRORLEVEL%' NEQ '0' (
    echo Installing Chocolatey...
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    if '%ERRORLEVEL%' NEQ '0' (
        echo Failed to install Chocolatey. If prompted above, please restart your command prompt, then run the script again. Otherwise, please install it manually.
        pause
        exit /b 1
    )
    :: Add Chocolatey to the PATH for the current session
    SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
    echo Chocolatey installed successfully. Please restart your command prompt or restart your system and run this script again.
    pause
    exit /b 1
)

:: Ensure PATH for Chocolatey is correct
SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

:: Install Python if not installed or version is less than 3.10
python --version 2>nul | findstr "Python 3.10"
if '%ERRORLEVEL%' NEQ '0' (
    echo Installing Python 3.10...
    choco install python --version=3.10 -y
    if '%ERRORLEVEL%' NEQ '0' (
        echo Failed to install Python. If prompted above, please restart your machine, then run the script again. Otherwise, please install it manually.
        pause
        exit /b 1
    )
    :: Refresh environment variables for the current session
    SET "PATH=%PATH%;C:\Python310;C:\Python310\Scripts"
    echo Python installed successfully. Please restart your system and run this script again.
    pause
    exit /b 1
)

:: Ensure pip is installed
python -m pip --version 2>nul
if '%ERRORLEVEL%' NEQ '0' (
    echo Installing pip...
    python -m ensurepip --upgrade
    if '%ERRORLEVEL%' NEQ '0' (
        echo Failed to install pip. Please install it manually.
        pause
        exit /b 1
    )
)

:: Check for the virtual environment folder
if not exist "tui_venv" (
    echo Creating virtual environment...
    python -m venv tui_venv
    if '%ERRORLEVEL%' NEQ '0' (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

:: Activate the virtual environment
call tui_venv\Scripts\activate
if '%ERRORLEVEL%' NEQ '0' (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install dependencies if virtual environment was just created
pip list | findstr "snet.cli" >nul 2>&1
if '%ERRORLEVEL%' NEQ '0' (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed.
)

:: Check if "update" argument is passed
if '%1'=='update' (
    echo Updating dependencies...
    pip install --upgrade pip
    pip install -r requirements.txt
    if '%ERRORLEVEL%' NEQ '0' (
        echo Failed to update dependencies.
        pause
        exit /b 1
    )
    echo Dependencies updated.
)

:: Run the main.py script
if '%1'=='dev' (
    echo Running in DEV mode
    textual run --dev application/main.py
) else (
    python application/main.py
)

if '%ERRORLEVEL%' NEQ '0' (
    echo Failed to run the application.
    pause
    exit /b 1
)

pause
