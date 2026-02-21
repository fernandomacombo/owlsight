#!/usr/bin/env bash
set -e

echo "== Python version =="
python --version

echo "== Django check =="
python manage.py check --deploy || python manage.py check

echo "== Running migrate =="
python manage.py migrate --noinput

echo "== Ensuring admin =="
python manage.py ensure_admin

echo "== Collecting static =="
python manage.py collectstatic --noinput

echo "== Starting gunicorn =="
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --timeout 300