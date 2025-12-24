#!/bin/bash
# Startup script for Render deployment
# Ensures migrations run before starting the server

set -e  # Exit on error

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec gunicorn HealthOracle.wsgi:application --config gunicorn_config.py
