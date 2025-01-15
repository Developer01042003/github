#!/usr/bin/env bash
# Exit on error
set -o errexit
set -o nounset  # To exit on unset variables

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories for static and media files..."
mkdir -p static staticfiles media

# Make migrations for all apps
echo "Making migrations for all apps..."
python manage.py makemigrations

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser (ensure no input errors with default or environment variable overrides)
echo "Creating superuser if not already existing..."
DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-adminpassword}"

python manage.py createsuperuser --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" || echo "Superuser creation skipped due to existing username."

# Final message
echo "Build and setup completed successfully!"
