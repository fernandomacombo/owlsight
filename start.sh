#!/usr/bin/env bash
set -e

echo "== Python version =="
python --version

echo "== Running migrate =="
python manage.py migrate --noinput

echo "== Collectstatic =="
python manage.py collectstatic --noinput

echo "== Starting gunicorn =="
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8080}