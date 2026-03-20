@echo off
setlocal
cd /d "%~dp0"

start "SIIRH Backend" cmd /k "%~dp0start_backend.cmd"
timeout /t 4 /nobreak >nul
start "SIIRH Frontend" cmd /k "%~dp0start_frontend.cmd"
timeout /t 4 /nobreak >nul
start "" http://127.0.0.1:5173
