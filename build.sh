#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status.
set -o errexit

echo "--- Running Build Script ---"

# CRITICAL FIX: Use 'python3' and ensure dependencies are installed before migration
# Render's system usually handles VENV activation, but we ensure 'pip' and 'python' point to the right place.

# 1. Install all dependencies
echo "--- Installing Dependencies ---"
pip install -r requirements.txt

# 2. Run static file collection (Must run before migrations for some setups)
echo "--- Collecting Static Files ---"
python manage.py collectstatic --noinput

# 3. Run database migrations (This is where the import failed)
echo "--- Applying Database Migrations ---"
# We run 'migrate' last, as dependencies and static files must be ready
python manage.py migrate

echo "Build process complete!"