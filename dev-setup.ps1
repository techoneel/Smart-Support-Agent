# PowerShell script for setting up development environment
Write-Host "Setting up Smart Support Agent development environment..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.9+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Green
python -m venv venv
. .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -e .
pip install -e ".[dev]"

# Create data directories
Write-Host "Creating data directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path data | Out-Null
New-Item -ItemType Directory -Force -Path logs | Out-Null

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Green
    Copy-Item .env.example .env
    Write-Host "Please edit .env with your API keys and configuration" -ForegroundColor Yellow
}

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Activate the virtual environment with: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan