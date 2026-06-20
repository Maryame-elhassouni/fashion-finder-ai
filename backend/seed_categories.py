from backend.app.core.database import SessionLocal
from backend.app.models.category import Category

CATEGORIES = [
    {"name": "Hauts",             "slug": "hauts",        "icon_emoji": "👕"},
    {"name": "Bas",               "slug": "bas",          "icon_emoji": "👖"},
    {"name": "Robes",             "slug": "robes",        "icon_emoji": "👗"},
    {"name": "Vestes & Manteaux", "slug": "vestes",       "icon_emoji": "🧥"},
    {"name": "Chaussures",        "slug": "chaussures",   "icon_emoji": "👟"},
    {"name": "Accessoires",       "slug": "accessoires",  "icon_emoji": "👜"},
]

db = SessionLocal()
inserted = 0
for cat in CATEGORIES:
    if not db.query(Category).filter(Category.slug == cat["slug"]).first():
        db.add(Category(**cat))
        inserted += 1
db.commit()
db.close()
print(f"✓ {inserted} catégories insérées")