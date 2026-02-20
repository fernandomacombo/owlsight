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
  --worker-class gthread \
  --threads 4 \
  --workers 1 \
  --timeout 300 \
  --graceful-timeout 300 \
  --log-level debug \
  --access-logfile - \
  --error-logfile - \
  --capture-output