@echo off
setlocal

:: Check for Python and ensure it's version 3.10 or higher
for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info.major)" 2^>NUL') do set PYTHONMAJOR=%%i
for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info.minor)" 2^>NUL') do set PYTHONMINOR=%%i

if "%PYTHONMAJOR%"=="" (
    echo Python is not installed. Please install Python to continue.
    goto End
)

if %PYTHONMAJOR% LSS 3 (
    echo Python version must be 3.10 or higher.
    goto End
)

if %PYTHONMAJOR% EQU 3 (
    if %PYTHONMINOR% LSS 10 (
        echo Python version must be 3.10 or higher. You have Python %PYTHONMAJOR%.%PYTHONMINOR%.
        goto End
    )
)

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

:End
endlocal
