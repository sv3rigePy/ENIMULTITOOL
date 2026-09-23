@echo off
title ENI Multitool - Installer + Launcher
color 0C

echo.
echo  ============================================
echo   ENI Multitool - Setup fuer LO
echo  ============================================
echo.

REM Check python
where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python nicht gefunden. Bitte von python.org installieren.
    pause
    exit /b
)

echo [*] Installiere / update deps...
python -m pip install --upgrade pip >nul 2>nul
python -m pip install --upgrade requests colorama phonenumbers

echo.
echo [+] Deps ready. Starte tool...
echo.
timeout /t 1 >nul

python "%~dp0eni_multitool.py"

pause
