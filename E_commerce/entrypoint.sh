#!/bin/sh
set -e  # stop the script on first error

# Default command is to run server
CMD=${1:-"web"}

wait_for_postgres() {
  echo "Waiting for PostgreSQL to be ready..."
  until python -c "import psycopg2; psycopg2.connect(host='$DB_HOST', port=$DB_PORT, user='$POSTGRES_USER', password='$POSTGRES_PASSWORD', dbname='$POSTGRES_DB')" 2>/dev/null; do
    echo "PostgreSQL not ready yet... waiting"
    sleep 2
  done
  echo "PostgreSQL is up!"
}

if [ "$CMD" = "web" ]; then
  wait_for_postgres

  echo "Applying database migrations..."
  python manage.py makemigrations --noinput
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

elif [ "$CMD" = "celery" ]; then
  wait_for_postgres
  echo "Starting Celery worker..."
  exec celery -A E_commerce worker --loglevel=info

elif [ "$CMD" = "celery-beat" ]; then
  wait_for_postgres
  echo "Starting Celery beat..."
  exec celery -A E_commerce beat --loglevel=info

else
  echo "Unknown CMD: $CMD"
  exit 1
fi
# ==============================above is for railway deply========================================
# ===============================local working fine========================
# #!/bin/sh
# set -e  # stop the script on first error

# # Default command is to run server
# CMD=${1:-"web"}

# if [ "$CMD" = "web" ]; then
#   echo "Waiting for PostgreSQL to be ready..."
#   while ! nc -z $DB_HOST $DB_PORT; do
#     sleep 1
#   done
#   echo "PostgreSQL is up!"

#   echo "Applying database migrations..."
#   python manage.py makemigrations --noinput
#   python manage.py migrate --noinput

#   echo "Collecting static files..."
#   python manage.py collectstatic --noinput

#   if [ "$DEBUG" = "True" ]; then
#       echo "Running Django development server..."
#       exec python manage.py runserver 0.0.0.0:8000
#   else
#       echo "Running Gunicorn production server..."
#       exec gunicorn --bind 0.0.0.0:8000 E_commerce.wsgi:application
#   fi

# elif [ "$CMD" = "celery" ]; then
#   echo "Starting Celery worker..."
#   exec celery -A E_commerce worker --loglevel=info

# elif [ "$CMD" = "celery-beat" ]; then
#   echo "Starting Celery beat..."
#   exec celery -A E_commerce beat --loglevel=info

# else
#   echo "Unknown CMD: $CMD"
#   exit 1
# fi

# ======================================================================
# #!/bin/sh

# echo "Waiting for PostgreSQL to be ready..."
# while ! nc -z $DB_HOST $DB_PORT; do
#   sleep 1
# done
# echo "PostgreSQL is up!"

# echo "Applying database migrations..."
# python manage.py migrate --noinput

# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# if [ "$DEBUG" = "True" ]; then
#     echo "Running Django development server..."
#     exec python manage.py runserver 0.0.0.0:8000
# else
#     echo "Running Gunicorn production server..."
#     exec gunicorn --bind 0.0.0.0:8000 E_commerce.wsgi:application
# fi
#===================================
