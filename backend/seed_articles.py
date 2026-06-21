from backend.app.core.database import SessionLocal
from backend.app.models.article import Article
from backend.app.models.category import Category


ARTICLES = [
    {"name":"T-shirt oversize coton blanc","description":"T-shirt ample en coton bio 100% ...","price":29.90,"brand":"Sézane","category_slug":"hauts"},
    {"name":"Chemise lin rayée bleue","description":"Chemise légère en lin ...","price":54.00,"brand":"Jacquemus","category_slug":"hauts"},
    {"name":"Pull col roulé camel","description":"Pull doux en laine ...","price":79.90,"brand":"Mango","category_slug":"hauts"},

    {"name":"Jean slim taille haute bleu","description":"Jean slim taille haute ...","price":89.00,"brand":"Levi's","category_slug":"bas"},
    {"name":"Pantalon large kaki","description":"Pantalon wide leg ...","price":65.00,"brand":"Zara","category_slug":"bas"},
    {"name":"Short en jean brut","description":"Short en denim brut ...","price":39.90,"brand":"Pull&Bear","category_slug":"bas"},

    {"name":"Robe midi fleurie","description":"Robe longueur midi ...","price":72.00,"brand":"& Other Stories","category_slug":"robes"},
    {"name":"Robe noire fourreau","description":"Robe fourreau ...","price":110.00,"brand":"Claudie Pierlot","category_slug":"robes"},
    {"name":"Robe en velours bordeaux","description":"Robe mi-longue ...","price":95.00,"brand":"ba&sh","category_slug":"robes"},

    {"name":"Veste en cuir noir biker","description":"Veste courte en cuir ...","price":249.00,"brand":"The Kooples","category_slug":"vestes"},
    {"name":"Blazer oversize beige","description":"Blazer slouchy ...","price":149.00,"brand":"COS","category_slug":"vestes"},
    {"name":"Manteau long camel","description":"Manteau long droit ...","price":320.00,"brand":"Totême","category_slug":"vestes"},

    {"name":"Sneakers blanches minimalistes","description":"Baskets basses ...","price":119.00,"brand":"Common Projects","category_slug":"chaussures"},
    {"name":"Bottines Chelsea marron","description":"Boots Chelsea ...","price":145.00,"brand":"Vagabond","category_slug":"chaussures"},
    {"name":"Sandales plates dorées","description":"Sandales à lanières ...","price":85.00,"brand":"Ancient Greek Sandals","category_slug":"chaussures"},

    {"name":"Sac tote en toile naturelle","description":"Grand tote bag ...","price":55.00,"brand":"Baggu","category_slug":"accessoires"},
    {"name":"Écharpe en soie imprimée","description":"Carré en soie ...","price":89.00,"brand":"Hermès","category_slug":"accessoires"},
    {"name":"Ceinture cuir réversible","description":"Ceinture réversible ...","price":65.00,"brand":"Maje","category_slug":"accessoires"},
    {"name":"Bob en lin blanc","description":"Chapeau bob ...","price":38.00,"brand":"Jacquemus","category_slug":"accessoires"},
    {"name":"Lunettes de soleil rondes","description":"Monture métallique ...","price":95.00,"brand":"Ray-Ban","category_slug":"accessoires"},
]


def seed_articles():
    db = SessionLocal()

    try:
        inserted = 0

        for a in ARTICLES:
            slug = a["category_slug"]

            cat = db.query(Category).filter(Category.slug == slug).first()
            if not cat:
                print(f"⚠ catégorie introuvable: {slug}")
                continue

            exists = db.query(Article).filter(Article.name == a["name"]).first()
            if exists:
                continue

            article = Article(
                name=a["name"],
                description=a["description"],
                price=a["price"],
                brand=a["brand"],
                category_id=cat.id
            )

            db.add(article)
            inserted += 1

        db.commit()
        return inserted

    finally:
        db.close()