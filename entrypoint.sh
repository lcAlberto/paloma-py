#!/bin/sh
set -e

echo "==> Rodando Migrations..."
python manage.py migrate --noinput

echo "==> Verificando Superuser..."
python manage.py create_admin

if [ "$SEED_ON_DEPLOY" = "true" ]; then
    echo "==> Executando Seed Data..."
    python manage.py seed_data
fi

echo "==> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

if [ $# -eq 0 ]; then
    echo "==> Iniciando Gunicorn (Produção)..."
    exec gunicorn core_api.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4
else
    echo "==> Executando comando customizado..."
    exec "$@"
fi