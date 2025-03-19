#!/bin/sh

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "PostgreSQL is up!"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

if [ "$DEBUG" = "True" ]; then
    echo "Running Django development server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Running Gunicorn production server..."
    exec gunicorn --bind 0.0.0.0:8000 E_commerce.wsgi:application
fi
