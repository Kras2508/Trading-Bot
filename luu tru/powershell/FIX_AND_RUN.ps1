# Fix Python Configuration and Run Server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fixing Python Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Clear environment variables that might cause issues
$env:PYTHONHOME = $null
$env:PYTHONPATH = $null
Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue

Write-Host "Step 1: Environment variables cleared" -ForegroundColor Green

# Check if venv exists, if not create it
if (-not (Test-Path "venv")) {
    Write-Host "Step 2: Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment!" -ForegroundColor Red
        Write-Host "Trying alternative method..." -ForegroundColor Yellow
        
        # Try with full path to python
        $pythonPath = (Get-Command python).Source
        & $pythonPath -m venv venv
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Cannot create venv. Please check Python installation." -ForegroundColor Red
            pause
            exit 1
        }
    }
    Write-Host "Virtual environment created!" -ForegroundColor Green
} else {
    Write-Host "Step 2: Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Step 3: Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Could not activate venv script. Trying alternative..." -ForegroundColor Yellow
    & "venv\Scripts\python.exe" -m pip --version | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Using venv python directly..." -ForegroundColor Yellow
        $env:VIRTUAL_ENV = (Resolve-Path "venv").Path
    }
}

# Upgrade pip
Write-Host "Step 4: Upgrading pip..." -ForegroundColor Yellow
& "venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    python -m pip install --upgrade pip --quiet
}

# Install dependencies
Write-Host "Step 5: Installing dependencies..." -ForegroundColor Yellow
& "venv\Scripts\python.exe" -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Dependencies installed successfully!" -ForegroundColor Green

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "Step 6: Creating .env file..." -ForegroundColor Yellow
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

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Yellow
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Health: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run server using venv python
& "venv\Scripts\python.exe" run.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Server failed to start!" -ForegroundColor Red
    Write-Host "Trying alternative method..." -ForegroundColor Yellow
    & "venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

pause

