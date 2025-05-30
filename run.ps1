# PowerShell script to run Flask server for the mini-blogging-api

Write-Host "Setting environment variables..."
$env:FLASK_APP = "run.py"
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = 1

Write-Host "Checking for virtual environment..."
if (-Not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python3.11 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    
} else {
    Write-Host "Activating existing virtual environment..."
    .\.venv\Scripts\Activate.ps1
}

Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host "Running DB migrations..."

if (-Not (Test-Path "migrations")) {
    flask db init
}

flask db migrate -m "Auto migration via script"
flask db upgrade

Write-Host "Starting Flask server..."
flask run
