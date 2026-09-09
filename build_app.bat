@echo off
rem ---------------------------------------------------------------
rem  Rebuild dist\NormalShockCalculator.exe from the Python source.
rem  Run this again after editing normal_shock_gui.py.
rem ---------------------------------------------------------------
cd /d "%~dp0"

echo [1/3] building the icon ...
python make_icon.py || goto :fail

echo [2/3] making sure PyInstaller is installed ...
python -m pip install --quiet --disable-pip-version-check pyinstaller || goto :fail

echo [3/3] packaging the application ...
python -m PyInstaller --noconfirm --onefile --windowed ^
    --icon "%~dp0shock.ico" ^
    --add-data "%~dp0shock.ico;." ^
    --name NormalShockCalculator ^
    --distpath dist --workpath build\work --specpath build ^
    normal_shock_gui.py || goto :fail

echo.
echo Done.  The application is  dist\NormalShockCalculator.exe
pause
exit /b 0

:fail
echo.
echo BUILD FAILED - see the messages above.
pause
exit /b 1
