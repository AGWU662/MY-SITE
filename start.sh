#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if needed..."
python manage.py create_superuser

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 elite_wealth.wsgi:application
