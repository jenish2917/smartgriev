@echo off
start cmd /k "cd /d e:\smartgriev2.0\smartgriev\backend && venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000 --noreload"
timeout /t 5 >nul
start cmd /k "cd /d e:\smartgriev2.0\smartgriev\frontend-new && npm run dev"
