@echo off
setlocal enableextensions enabledelayedexpansion

echo.
echo === Wan 2.2 Prompt Crafter - One Click EXE Builder ===
echo Working directory: %CD%
echo.

rem Go to the script's directory
cd /d "%~dp0"

rem ---------------------------------------------------------
rem 1) Locate or install Python (prefers py launcher)
rem ---------------------------------------------------------
set "PYTHON_CMD="

for %%P in (py python) do (
  %%P --version >nul 2>&1
  if not errorlevel 1 (
    set "PYTHON_CMD=%%P"
    goto :have_python
  )
)

:install_python
echo [INFO] Python not found. Downloading Python 3.10.11 (x64)...
set "PY_VER=3.10.11"
set "PY_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-amd64.exe"

where curl >nul 2>&1
if errorlevel 1 (
  echo [WARN] curl not available. Using PowerShell to download...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile 'python-installer.exe'"
) else (
  curl -L "%PY_URL%" -o "python-installer.exe"
)

if not exist "python-installer.exe" (
  echo [ERROR] Failed to download Python installer.
  exit /b 1
)

echo [INFO] Installing Python silently...
start /wait "" "python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
if exist "python-installer.exe" del /q "python-installer.exe"

rem Try to refresh PATH for current session (common install paths)
set "PATH=%ProgramFiles%\Python310;%ProgramFiles%\Python310\Scripts;%ProgramFiles%\Python311;%ProgramFiles%\Python311\Scripts;%LocalAppData%\Programs\Python\Python310;%LocalAppData%\Programs\Python\Python310\Scripts;%LocalAppData%\Programs\Python\Python311;%LocalAppData%\Programs\Python\Python311\Scripts;%PATH%"

for %%P in (py python) do (
  %%P --version >nul 2>&1
  if not errorlevel 1 (
    set "PYTHON_CMD=%%P"
    goto :have_python
  )
)

echo [ERROR] Python installation appears to have failed or PATH not updated.
exit /b 1

:have_python
echo [INFO] Using Python command: %PYTHON_CMD%
echo.

rem ---------------------------------------------------------
rem 2) Ensure pip and install project requirements
rem ---------------------------------------------------------
%PYTHON_CMD% -m ensurepip --upgrade
%PYTHON_CMD% -m pip install --upgrade pip

if exist "requirements.txt" (
  echo [INFO] Installing dependencies from requirements.txt...
  %PYTHON_CMD% -m pip install -r requirements.txt
) else (
  echo [WARN] requirements.txt not found; installing minimal runtime + PyInstaller...
  %PYTHON_CMD% -m pip install customtkinter requests clipboard pyinstaller
)

rem ---------------------------------------------------------
rem 3) Build EXE with PyInstaller
rem ---------------------------------------------------------
set "ICON_PATH=C:\Users\WontML\Pictures\1a\icon.png"
set "ICON_OP="
if exist "%ICON_PATH%" (
  set "ICON_OP=--icon ""%ICON_PATH%"" --splash ""%ICON_PATH%"""
) else (
  echo [WARN] Icon/splash not found at "%ICON_PATH%". Building without icon/splash.
)

set "EXCLUDES=--exclude-module PyQt5 --exclude-module PyQt6 --exclude-module qtpy --exclude-module PySide2 --exclude-module PySide6"

echo.
echo [INFO] Running PyInstaller...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --windowed app.py --name "Wan2PromptCrafter" %ICON_OP% %EXCLUDES%
if errorlevel 1 (
  echo [ERROR] PyInstaller build failed.
  exit /b 1
)

echo.
echo [SUCCESS] Build complete!
echo Output: "%CD%\dist\Wan2PromptCrafter.exe"
echo.
pause