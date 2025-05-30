#!/bin/bash

echo "Setting environment variables..."
export FLASK_APP="run.py"
export FLASK_ENV="development"
export FLASK_DEBUG=1

echo "Checking for virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv .venv
    source .venv/bin/activate
else
    echo "Activating existing virtual environment..."
    source .venv/bin/activate
fi

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running DB migrations..."
if [ ! -d "migrations" ]; then
    flask db init
fi

flask db migrate -m "Auto migration via script"
flask db upgrade

echo "Starting Flask server..."
flask run
