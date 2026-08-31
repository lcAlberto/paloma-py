#!/bin/sh
set -e

echo "==> Rodando Migrations..."
python manage.py migrate --noinput

echo "==> Verificando Superuser..."
python manage.py create_admin

# Executa seed apenas se a flag SEED_ON_DEPLOY for True
if [ "$SEED_ON_DEPLOY" = "true" ]; then
    echo "==> Executando Seed Data..."
    python manage.py seed_data
fi

echo "==> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "==> Iniciando Gunicorn..."
exec gunicorn core_api.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4