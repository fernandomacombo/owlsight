#!/usr/bin/env bash
set -e

echo "== Python version =="
python --version

echo "== Django check =="
python manage.py check

echo "== Running migrate =="
python manage.py migrate --noinput

echo "== Ensuring admin =="
python manage.py ensure_admin

echo "== Collectstatic =="
python manage.py collectstatic --noinput

echo "== Starting gunicorn (preload) =="
gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 1 \
  --threads 2 \
  --timeout 180 \
  --graceful-timeout 180 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --capture-output