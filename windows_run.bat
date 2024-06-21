@echo off
setlocal

:: Function to prompt user for installation
:prompt_install
set /p response=%1 is not installed or is out of date. Would you like to install it now? (y/n): 
if /i "%response%"=="y" (
    %2
    if errorlevel 1 (
        echo Failed to install %1. Please install it manually and rerun the script.
        exit /b 1
    )
) else (
    echo Please install %1 to continue.
    exit /b 1
)
goto :eof

:: Check for Chocolatey
where choco >nul 2>nul
if errorlevel 1 (
    echo Chocolatey is not installed. It is required to install Python and other dependencies.
    call :prompt_install "Chocolatey" "powershell -NoProfile -ExecutionPolicy Bypass -Command iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1')) && SET PATH=%%PATH%%;%%ALLUSERSPROFILE%%\chocolatey\bin"
)

:: Check for Python and ensure its version is 3.10 or higher
where python >nul 2>nul
if errorlevel 1 (
    call :prompt_install "Python 3.10 or higher" "choco install python --version=3.11.9"
)

for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info.major)" 2^>nul') do set PYTHONMAJOR=%%i
for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info.minor)" 2^>nul') do set PYTHONMINOR=%%i

if "%PYTHONMAJOR%"=="" goto ErrorPython
if %PYTHONMAJOR% LSS 3 goto ErrorVersion
if %PYTHONMAJOR% EQU 3 if %PYTHONMINOR% LSS 10 goto ErrorVersion

:: Check for pip
python -m pip --version >nul 2>nul
if errorlevel 1 (
    call :prompt_install "pip" "python -m ensurepip"
)

:: Check for venv
python -m venv --help >nul 2>nul
if errorlevel 1 (
    call :prompt_install "venv" "python -m pip install virtualenv"
)

:: Ensure python points to the correct version
if "%PYTHONMAJOR%" NEQ "3" (
    if "%PYTHONMINOR%" LSS "10" (
        call :prompt_install "Python 3.10 or higher" "choco install python --version=3.11.9"
    )
)

:: Check if the virtual environment exists
if not exist "tui_venv\" (
    echo Creating virtual environment...
    python -m venv tui_venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        rmdir /s /q tui_venv
        exit /b 1
    )
    echo Virtual environment created.
    call tui_venv\Scripts\activate.bat
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies.
        exit /b 1
    )
    echo Dependencies installed.
    deactivate
)

:: Activate the virtual environment
if exist "tui_venv\Scripts\activate.bat" (
    call tui_venv\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo Failed to find the virtual environment activation script.
    rmdir /s /q tui_venv
    exit /b 1
)

:: Check if "update" argument is passed
if "%1"=="update" (
    echo Updating dependencies...
    pip install --upgrade pip
    pip install -r requirements.txt
    echo Dependencies updated.
)

:: Run the main.py script
if "%1"=="dev" (
    echo Running in DEV mode
    textual run --dev application\main.py
) else (
    python application\main.py
)

if errorlevel 1 (
    echo Failed to run the application.
    exit /b 1
)

goto End

:ErrorPython
echo Python 3 is not correctly installed. Please check your Python installation.
goto End

:ErrorVersion
echo Python version must be 3.10 or higher. Please upgrade your Python.
goto End

:End
endlocal
