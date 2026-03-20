@echo off
setlocal
cd /d "%~dp0siirh-backend"

where python >nul 2>nul
if errorlevel 1 (
  echo Python est introuvable dans le PATH Windows.
  pause
  exit /b 1
)

echo Demarrage du backend SIIRH sur http://127.0.0.1:8001
python start_server.py
