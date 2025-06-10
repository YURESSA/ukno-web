#!/bin/sh
sleep 10
cd backend
flask db init
flask db migrate
flask db upgrade
cd ..

echo Подготоавливаю данные
python -m backend.app seed_reference_data

exec gunicorn -w 4 -b 0.0.0.0:5000 backend.wsgi:app



