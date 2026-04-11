# Final Fix for Python Configuration Issue
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fixing Python Configuration (Final Solution)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get Python executable path
$pythonExe = (Get-Command python).Source
Write-Host "Python found at: $pythonExe" -ForegroundColor Green

# Clear all Python-related environment variables
$env:PYTHONHOME = $null
$env:PYTHONPATH = $null
$env:PYTHONSTARTUP = $null
Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
Remove-Item Env:PYTHONSTARTUP -ErrorAction SilentlyContinue

Write-Host "Environment variables cleared" -ForegroundColor Green

# Solution 1: Create venv in parent directory
$parentDir = Split-Path -Parent $PWD
$venvPath = Join-Path $parentDir "BackendAPI_Trading_venv"

Write-Host ""
Write-Host "Creating virtual environment in: $venvPath" -ForegroundColor Yellow

# Use Python with --isolated flag to avoid site-packages issues
& $pythonExe -I -m venv $venvPath --clear

if ($LASTEXITCODE -ne 0) {
    Write-Host "Method 1 failed. Trying method 2..." -ForegroundColor Yellow
    
    # Solution 2: Use virtualenv if available
    $hasVirtualenv = & $pythonExe -m pip list | Select-String "virtualenv"
    if ($hasVirtualenv) {
        & $pythonExe -m virtualenv $venvPath --no-site-packages
    } else {
        # Solution 3: Create venv with explicit paths
        $pythonDir = Split-Path -Parent $pythonExe
        & $pythonExe -m venv $venvPath --python $pythonExe
    }
}

if (-not (Test-Path $venvPath)) {
    Write-Host ""
    Write-Host "ERROR: Could not create virtual environment!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative Solution: Move project to a different directory" -ForegroundColor Yellow
    Write-Host "Or use system Python without venv:" -ForegroundColor Yellow
    Write-Host "  python -m pip install -r requirements.txt --user" -ForegroundColor White
    Write-Host "  python run.py" -ForegroundColor White
    pause
    exit 1
}

Write-Host "Virtual environment created successfully!" -ForegroundColor Green

# Activate venv
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
}

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
$venvPython = Join-Path $venvPath "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $venvPython -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Dependencies installed successfully!" -ForegroundColor Green

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    @"
# App Configuration
DEBUG=False

# Database
DATABASE_URL=sqlite:///./trading_bot.db

# Security - CHANGE THESE IN PRODUCTION!
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-12345
ENCRYPTION_KEY=dev-encryption-key-32-bytes-long-12345678

# CORS
CORS_ORIGINS=["*"]

# IP Whitelist
ENABLE_IP_WHITELIST=False

# Telegram (Optional)
ENABLE_TELEGRAM=False
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Exchange
DEFAULT_EXCHANGE=binance
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host ".env file created!" -ForegroundColor Green
}

# Create a launcher script
$launcherScript = @"
@echo off
call "$venvPath\Scripts\activate.bat"
python run.py
"@
$launcherScript | Out-File -FilePath "RUN_SERVER.bat" -Encoding ASCII

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Virtual environment created at: $venvPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "To start the server, run:" -ForegroundColor Yellow
Write-Host "  RUN_SERVER.bat" -ForegroundColor White
Write-Host ""
Write-Host "Or manually:" -ForegroundColor Yellow
Write-Host "  $venvPath\Scripts\activate" -ForegroundColor White
Write-Host "  python run.py" -ForegroundColor White
Write-Host ""

# Ask if user wants to start server now
$response = Read-Host "Start server now? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "Starting server..." -ForegroundColor Cyan
    Write-Host "Server will be available at:" -ForegroundColor Yellow
    Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  - Health: http://localhost:8000/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    
    & $venvPython run.py
}

pause

