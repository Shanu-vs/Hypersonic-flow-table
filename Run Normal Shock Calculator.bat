@echo off
rem ---------------------------------------------------------------
rem  Double-click launcher for the Normal Shock Calculator.
rem  Runs the Python source directly (needs Python 3 installed).
rem  pythonw.exe is used so no black console window appears.
rem ---------------------------------------------------------------
where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw "%~dp0normal_shock_gui.py"
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        start "" python "%~dp0normal_shock_gui.py"
    ) else (
        echo Python was not found on this PC.
        echo Install Python 3 from https://www.python.org/downloads/
        echo or use dist\NormalShockCalculator.exe instead.
        pause
    )
)
