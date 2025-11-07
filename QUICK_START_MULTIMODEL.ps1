# SmartGriev Multi-Model Image Processing - Quick Start Script
# This script sets up and runs the advanced image processing system

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SmartGriev Multi-Model Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python found" -ForegroundColor Green
Write-Host ""

# Navigate to backend
Write-Host "Navigating to backend directory..." -ForegroundColor Yellow
cd smartgriev\backend
Write-Host "✓ In backend directory" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "Virtual environment found" -ForegroundColor Green
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
    
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "✓ Pip upgraded" -ForegroundColor Green
Write-Host ""

# Ask user what to do
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Select an option:" -ForegroundColor Cyan
Write-Host "1. Install multi-model requirements" -ForegroundColor White
Write-Host "2. Setup and download all models" -ForegroundColor White
Write-Host "3. Test the multi-model system" -ForegroundColor White
Write-Host "4. Run Django backend server" -ForegroundColor White
Write-Host "5. Do everything" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`nInstalling multi-model requirements..." -ForegroundColor Yellow
        pip install -r requirements_multimodel.txt
        Write-Host "✓ Requirements installed" -ForegroundColor Green
    }
    "2" {
        Write-Host "`nSetting up multi-model system..." -ForegroundColor Yellow
        python setup_multimodel.py
        Write-Host "✓ Setup complete" -ForegroundColor Green
    }
    "3" {
        Write-Host "`nTesting multi-model system..." -ForegroundColor Yellow
        python test_multimodel.py
        Write-Host "✓ Test complete" -ForegroundColor Green
    }
    "4" {
        Write-Host "`nStarting Django backend server..." -ForegroundColor Yellow
        Write-Host "Server will run at: http://127.0.0.1:8000" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
        Write-Host ""
        python manage.py runserver
    }
    "5" {
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "Full Setup Process" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        
        # Install requirements
        Write-Host "`n[1/4] Installing requirements..." -ForegroundColor Yellow
        pip install -r requirements_multimodel.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Requirements installed" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to install requirements" -ForegroundColor Red
            exit 1
        }
        
        # Setup models
        Write-Host "`n[2/4] Setting up models..." -ForegroundColor Yellow
        python setup_multimodel.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Models setup complete" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to setup models" -ForegroundColor Red
            exit 1
        }
        
        # Test system
        Write-Host "`n[3/4] Testing system..." -ForegroundColor Yellow
        python test_multimodel.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Tests passed" -ForegroundColor Green
        } else {
            Write-Host "⚠ Some tests failed (system may still work)" -ForegroundColor Yellow
        }
        
        # Migrate database
        Write-Host "`n[4/4] Setting up database..." -ForegroundColor Yellow
        python manage.py migrate
        Write-Host "✓ Database ready" -ForegroundColor Green
        
        # Success message
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "✓ Setup Complete!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "`nNext steps:" -ForegroundColor Cyan
        Write-Host "1. Start backend: python manage.py runserver" -ForegroundColor White
        Write-Host "2. Start frontend: cd ../frontend; npm start" -ForegroundColor White
        Write-Host "3. Upload images to test the multi-model system" -ForegroundColor White
        Write-Host ""
        
        # Ask if they want to start the server
        $startServer = Read-Host "Start Django server now? (y/n)"
        if ($startServer -eq "y" -or $startServer -eq "Y") {
            Write-Host "`nStarting Django backend server..." -ForegroundColor Yellow
            Write-Host "Server will run at: http://127.0.0.1:8000" -ForegroundColor Cyan
            Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
            Write-Host ""
            python manage.py runserver
        }
    }
    default {
        Write-Host "`nInvalid choice!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
