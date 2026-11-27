@echo off
chcp 65001 >nul
title Wedding Website - Local Server
cd /d "%~dp0"

python --version >nul 2>nul
if %errorlevel%==0 (
    python run.py %*
    goto :eof
)

py --version >nul 2>nul
if %errorlevel%==0 (
    py run.py %*
    goto :eof
)

where node >nul 2>nul
if %errorlevel%==0 (
    echo Starting server with Node.js...
    node server.js %*
    goto :eof
)

echo Neither Python nor Node.js was found on PATH.
echo Please install Python 3 from https://www.python.org/downloads/ or Node.js.
pause
