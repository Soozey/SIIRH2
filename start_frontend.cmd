@echo off
setlocal
cd /d "%~dp0siirh-frontend"

where npm.cmd >nul 2>nul
if errorlevel 1 (
  echo npm est introuvable dans le PATH Windows.
  pause
  exit /b 1
)

set VITE_API_URL=http://127.0.0.1:8001
echo Demarrage du frontend SIIRH sur http://127.0.0.1:5173
npm.cmd run dev -- --host 127.0.0.1 --port 5173
