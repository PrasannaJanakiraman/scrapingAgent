#!/bin/bash
set -e

# Install pip dependencies if antenv doesn't exist
if [ ! -d "/home/site/wwwroot/antenv" ]; then
    echo "Virtual environment not found. Installing dependencies..."
    cd /home/site/wwwroot
    pip install -r requirements.txt
fi

# Install Playwright browser
python -m playwright install chromium
python -m playwright install-deps chromium

# Start the app
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --log-level debug
