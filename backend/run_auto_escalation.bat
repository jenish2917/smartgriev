@echo off
REM Auto-Escalation Script for SmartGriev
REM Escalates unresolved complaints older than 3 days

cd /d e:\Smartgriv\smartgriev\backend

REM Activate virtual environment (adjust path if needed)
call ..\venv\Scripts\activate.bat

REM Run auto-escalation command
echo Starting auto-escalation at %date% %time%
python manage.py auto_escalate_complaints --days 3 --send-notifications

REM Log completion
echo Auto-escalation completed at %date% %time% >> auto_escalation.log

REM Deactivate virtual environment
deactivate

pause
