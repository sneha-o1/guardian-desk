#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status.
set -o errexit

echo "--- Running Build Script ---"

# 1. Install all dependencies
pip install -r requirements.txt

# 2. Run static file collection (finds app.js in your 'static' folder)
echo "--- Collecting Static Files ---"
python manage.py collectstatic --noinput

# 3. Run database migrations
echo "--- Applying Database Migrations ---"
python manage.py migrate

echo "Build process complete!"