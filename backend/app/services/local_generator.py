import random

COLORS = [
    "noir", "blanc", "bleu", "beige", "gris",
    "vert", "rose", "rouge", "camel", "marine"
]

MATERIALS = [
    "coton", "lin", "laine", "denim",
    "viscose", "polyester", "cuir"
]

STYLES = [
    "casual", "élégant", "moderne",
    "oversize", "minimaliste", "chic"
]

BRANDS = [
    "Nova Fashion",
    "Urban Mode",
    "Maison Style",
    "Luna Wear",
    "Elegance Paris",
    "City Chic",
    "Trend Factory",
    "ModeX"
]

NAMES = {
    "hauts": [
        "T-shirt", "Chemise", "Pull", "Sweat", "Polo", "Blouse"
    ],
    "bas": [
        "Jean", "Pantalon", "Short", "Jupe"
    ],
    "robes": [
        "Robe midi", "Robe longue", "Robe courte", "Robe portefeuille"
    ],
    "vestes": [
        "Blazer", "Veste", "Manteau", "Trench"
    ],
    "chaussures": [
        "Sneakers", "Bottes", "Sandales", "Escarpins"
    ],
    "accessoires": [
        "Sac", "Ceinture", "Écharpe", "Casquette", "Montre"
    ]
}


def generate_local_articles(category, count):
    articles = []

    for _ in range(count):
        base = random.choice(NAMES[category])
        color = random.choice(COLORS)
        material = random.choice(MATERIALS)
        style = random.choice(STYLES)

        articles.append({
            "name": f"{base} {color}",
            "description":
                f"{base} en {material} de couleur {color}, style {style}, "
                f"confortable et adapté au quotidien.",
            "price": round(random.uniform(19, 199), 2),
            "brand": random.choice(BRANDS)
        })

    return articles