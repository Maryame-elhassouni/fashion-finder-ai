#!/bin/bash
echo "🚀 Démarrage Fashion Finder IA..."

echo "⏳ Démarrage PostgreSQL..."
sudo service postgresql start
sleep 2

echo "⏳ Activation du venv..."
source venv/bin/activate

echo "⏳ Application des migrations..."
source venv/bin/activate
alembic upgrade head

echo "⏳ Seed des catégories..."
export PYTHONPATH=$(pwd)
python3 backend/seed_categories.py

echo "✓ Prêt ! Démarrage du serveur FastAPI..."
echo "📖 Swagger : http://localhost:8000/docs"
uvicorn backend.app.main:app --reload --port 8000