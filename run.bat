@echo off
start cmd /k "cd /d d:\SmartGriev\backend && python manage.py runserver 0.0.0.0:8000"
timeout /t 2 >nul
start cmd /k "cd /d d:\SmartGriev\frontend && npm run dev"
