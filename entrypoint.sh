#!/bin/sh
set -e

echo "----> Starting entrypoint"

if [ -n "$POSTGRES_HOST" ]; then
  echo "Waiting for Postgres at ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
  until pg_isready -h "$POSTGRES_HOST" -p "${POSTGRES_PORT:-5432}" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
    echo "Postgres unavailable - sleeping"
    sleep 1
  done
  echo "Postgres is ready"
fi

echo "Apply database migrations"
python manage.py migrate --noinput

if [ "$DJANGO_PRODUCTION" = "1" ]; then
  echo "Starting Gunicorn"
  exec gunicorn szebi_core.wsgi:application --bind 0.0.0.0:8000 --workers 3
else
  echo "Starting Django development server"
  exec python manage.py runserver 0.0.0.0:8000
fi