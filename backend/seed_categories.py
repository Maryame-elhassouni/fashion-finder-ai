from backend.app.core.database import SessionLocal
from backend.app.models.category import Category
import backend.app.core.database as database
from backend.app.core.config import settings
from backend.app.models import *

CATEGORIES = [
    {"name": "Hauts",             "slug": "hauts",        "icon_emoji": "👕"},
    {"name": "Bas",               "slug": "bas",          "icon_emoji": "👖"},
    {"name": "Robes",             "slug": "robes",        "icon_emoji": "👗"},
    {"name": "Vestes & Manteaux", "slug": "vestes",       "icon_emoji": "🧥"},
    {"name": "Chaussures",        "slug": "chaussures",   "icon_emoji": "👟"},
    {"name": "Accessoires",       "slug": "accessoires",  "icon_emoji": "👜"},
]

database.init_engine(settings.DATABASE_URL)

db = database.SessionLocal()
inserted = 0
for cat in CATEGORIES:
    if not db.query(Category).filter(Category.slug == cat["slug"]).first():
        db.add(Category(**cat))
        inserted += 1
db.commit()
db.close()
print(f"✓ {inserted} catégories insérées")