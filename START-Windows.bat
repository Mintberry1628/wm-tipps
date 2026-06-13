@echo off
title WM 2026 KI-Tipps
cd /d "%~dp0"
echo Starte WM-2026-Tipp-App ...
start "" http://localhost:8026
python serve.py
pause
