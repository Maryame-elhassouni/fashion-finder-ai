#!/bin/bash
set -e
echo "Attente de la BDD..."
sleep 3
echo "Application des migrations..."
alembic upgrade head
echo "Seed des catégories..."
python seed_categories.py 2>/dev/null || true
echo "Démarrage du serveur..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload