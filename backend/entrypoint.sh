#!/bin/sh

sleep 10

cd backend

# Проверяем, существует ли папка миграций
if [ ! -d "migrations" ]; then
  echo "Инициализация миграций..."
  flask db init
  flask db migrate
fi


flask db upgrade

cd ..

echo "Подготавливаю данные"
python -m backend.app seed_reference_data

exec gunicorn -w 4 -b 0.0.0.0:5000 backend.wsgi:app
