"""
Génère 80 articles supplémentaires via Gemini pour enrichir le catalogue à 100.
Si Gemini est indisponible (quota, erreur réseau...), un générateur local est utilisé.
"""

import json
import google.generativeai as genai

from app.models.article import Article
from app.models.category import Category
import app.core.database as database
from app.core.config import settings
from app.services.local_generator import generate_local_articles

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

CATEGORIES_TARGET = {
    "hauts": 14,
    "bas": 14,
    "robes": 13,
    "vestes": 13,
    "chaussures": 13,
    "accessoires": 13,
}


def generate_batch(category_name: str, count: int) -> list[dict]:
    prompt = f"""
Génère {count} articles vestimentaires de la catégorie "{category_name}" pour un
catalogue de mode français.

Pour chaque article, donne :
- un nom court (max 6 mots)
- une description détaillée (15 à 25 mots)
- un prix réaliste en euros
- une marque fictive

Réponds UNIQUEMENT avec un tableau JSON valide :

[
  {{
    "name":"...",
    "description":"...",
    "price":99.0,
    "brand":"..."
  }}
]
"""

    response = model.generate_content(prompt)

    text = (
        response.text.strip()
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(text)


database.init_engine(settings.DATABASE_URL)
db = database.SessionLocal()

total_added = 0

for slug, count in CATEGORIES_TARGET.items():

    cat = db.query(Category).filter(Category.slug == slug).first()

    if not cat:
        print(f"⚠ Catégorie '{slug}' introuvable")
        continue

    print(f"🤖 Génération de {count} articles pour '{slug}'...")

    try:
        # ---------- Gemini ----------
        items = generate_batch(slug, count)
        source = "Gemini"

    except Exception as e:
        print(f"❌ Gemini indisponible : {e}")
        print("➡ Bascule vers le générateur local...")

        # ---------- Génération locale ----------
        items = generate_local_articles(slug, count)
        source = "Local"

    added = 0

    for item in items:

        existing = (
            db.query(Article)
            .filter(Article.name == item["name"])
            .first()
        )

        if existing:
            continue

        db.add(
            Article(
                name=item["name"],
                description=item["description"],
                price=round(float(item["price"]), 2),
                brand=item.get("brand", "Fashion Brand"),
                category_id=cat.id,
            )
        )

        added += 1
        total_added += 1

    db.commit()

    print(f"   ✓ {added} articles ajoutés ({source})")

db.close()

print(f"\n✅ Total : {total_added} nouveaux articles ajoutés")