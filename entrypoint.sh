#!/bin/bash
set -e

echo "=== Collecting Static Files ==="
python manage.py collectstatic --noinput

echo "=== Database Migration Fix ==="

# Check if we can connect to DB
python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection(); print('DB Connected!')" || {
    echo "DB connection failed!"
    exit 1
}

# Check if the column exists
echo "Checking if has_virtual_card column exists..."
COLUMN_EXISTS=$(python -c "
import django
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(\"\"\"
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'accounts_customuser' AND column_name = 'has_virtual_card'
    \"\"\")
    print('yes' if cursor.fetchone() else 'no')
")

if [ "$COLUMN_EXISTS" = "no" ]; then
    echo "Column missing! Faking migration 0004 backward and reapplying..."
    
    # Mark migration 0004 as not applied
    python manage.py migrate accounts 0003 --fake
    
    # Now run all migrations
    python manage.py migrate --noinput
else
    echo "Columns exist, running normal migration..."
    python manage.py migrate --noinput
fi

echo "=== Creating superuser if needed ==="
python manage.py create_superuser || echo "Superuser check complete"

echo "=== Starting Gunicorn server ==="
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 elite_wealth.wsgi:application