#!/bin/sh

python -m backend.app init_db

echo "Preparing seed data"
python -m backend.app seed_reference_data

exec gunicorn -w 2 -b 0.0.0.0:5000 backend.wsgi:app --timeout 90
