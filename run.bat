@echo off
start cmd /k "cd /d d:\smartgrive\smartgriev\backend && D:\smartgrive\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000 --noreload"
timeout /t 5 >nul
start cmd /k "cd /d d:\smartgrive\smartgriev\frontend-new && npm run dev"
