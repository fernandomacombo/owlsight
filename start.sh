#!/usr/bin/env bash
set -e

echo "== Python version =="
python --version

echo "== Django check =="
python manage.py check

echo "== Running migrate =="
python manage.py migrate --noinput

echo "== Collectstatic =="
python manage.py collectstatic --noinput

echo "== Starting gunicorn (preload) =="
gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --log-level debug \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --preload