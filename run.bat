@echo off
start cmd /k "cd /d d:\SmartGriev\backend && python manage.py runserver 0.0.0.0:8000 --noreload"
timeout /t 5 >nul
start cmd /k "cd /d d:\SmartGriev\frontend-new && npm run dev"
