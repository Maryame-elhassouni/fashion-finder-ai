# Fashion Finder IA 👗

![CI](https://github.com/Maryame-elhassouni/fashion-finder-ai/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)

> Recherche vestimentaire par description naturelle — propulsé par **Gemini AI**

## Démarrage rapide
```bash
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000
# API : http://localhost:8000/docs
```

## Tests
```bash
pytest tests/ -v --cov=app
# → ~50 tests, couverture 92%