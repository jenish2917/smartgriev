@echo off
REM SmartGriev - Start Both Servers
REM This script starts both backend and frontend servers

echo.
echo ============================================================
echo   SmartGriev - Starting Both Servers
echo ============================================================
echo.

REM Check if port 8000 is in use
echo [1/4] Checking if port 8000 is available...
netstat -ano | findstr :8000 > nul
if %errorlevel% equ 0 (
    echo Port 8000 is in use. Killing existing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        taskkill /F /PID %%a > nul 2>&1
    )
    timeout /t 2 > nul
    echo Port 8000 freed!
)

REM Start Backend Server
echo.
echo [2/4] Starting Backend Server (Port 8000)...
cd /d "%~dp0backend"
start "SmartGriev Backend" cmd /k "python gemini_chatbot_server.py"
timeout /t 3 > nul

REM Verify Backend is running
echo.
echo [3/4] Verifying Backend Server...
python -c "import requests; r = requests.get('http://127.0.0.1:8000/api/chatbot/health/', timeout=5); print('Backend Status:', r.status_code)" 2>nul
if %errorlevel% equ 0 (
    echo Backend Server: RUNNING on http://127.0.0.1:8000
) else (
    echo Backend Server: FAILED TO START
    pause
    exit /b 1
)

REM Start Frontend Server
echo.
echo [4/4] Starting Frontend Server (Port 3000)...
cd /d "%~dp0frontend"
start "SmartGriev Frontend" cmd /k "npm run dev"

echo.
echo ============================================================
echo   SERVERS STARTED SUCCESSFULLY!
echo ============================================================
echo.
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:3000
echo.
echo   Press any key to open browser...
pause > nul

REM Open browser
start http://localhost:3000

echo.
echo   Servers are running in separate windows.
echo   Close those windows to stop the servers.
echo.
pause
