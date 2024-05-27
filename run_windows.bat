@echo off
setlocal

:: Check for Python and ensure it's version 3.10 or higher
where python >nul 2>nul || (echo Python 3 is not installed. Please install Python 3 to continue. & exit /b)
for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info.major)" 2^>nul') do set PYTHONMAJOR=%%i
for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info.minor)" 2^>nul') do set PYTHONMINOR=%%i

if "%PYTHONMAJOR%"=="" goto ErrorPython
if %PYTHONMAJOR% LSS 3 goto ErrorVersion
if %PYTHONMAJOR% EQU 3 if %PYTHONMINOR% LSS 10 goto ErrorVersion

:: Check for pip and venv
python -m pip --version >nul 2>nul || (echo pip is not installed. Please install pip. & goto End)
python -m venv --help >nul 2>nul || (echo venv is not installed. Please install the Python venv module. & goto End)

:: Check if the virtual environment exists
if not exist "tui_venv\" (
    echo Creating virtual environment...
    python -m venv tui_venv
    echo Virtual environment created.

    :: Activate virtual environment and install dependencies
    call tui_venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo Dependencies installed.
) else (
    echo Activating virtual environment...
    call tui_venv\Scripts\activate.bat
)

:: Run the main.py script
python application\main.py
goto End

:ErrorPython
echo Python 3 is not correctly installed. Please check your Python installation.
goto End

:ErrorVersion
echo Python version must be 3.10 or higher. Please upgrade your Python.
goto End

:End
endlocal
