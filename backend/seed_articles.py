from backend.app.core.database import SessionLocal
from backend.app.models.article import Article
from backend.app.models.category import Category

ARTICLES = [
  # HAUTS (slug: hauts)
  {"name":"T-shirt oversize coton blanc","description":"T-shirt ample en coton bio 100%, col rond, coupe boxy, parfait pour le quotidien. Style minimaliste et épuré.","price":29.90,"brand":"Sézane","category_slug":"hauts"},
  {"name":"Chemise lin rayée bleue","description":"Chemise légère en lin à rayures bleu marine, col classique, manches longues retroussables. Style décontracté chic.","price":54.00,"brand":"Jacquemus","category_slug":"hauts"},
  {"name":"Pull col roulé camel","description":"Pull doux en laine mélangée, col roulé haut, coupe ajustée. Coloris camel tendance, idéal en automne-hiver.","price":79.90,"brand":"Mango","category_slug":"hauts"},
  # BAS (slug: bas)
  {"name":"Jean slim taille haute bleu","description":"Jean slim taille haute en denim stretch bleu indigo, 5 poches, fermeture zip. Coupe valorisante et confortable.","price":89.00,"brand":"Levi's","category_slug":"bas"},
  {"name":"Pantalon large kaki","description":"Pantalon wide leg en coton kaki, taille élastiquée avec cordon, poches latérales profondes. Style streetwear décontracté.","price":65.00,"brand":"Zara","category_slug":"bas"},
  {"name":"Short en jean brut","description":"Short en denim brut non traité, ourlets froncés, taille mi-haute. Coupe droite et décontractée pour l'été.","price":39.90,"brand":"Pull&Bear","category_slug":"bas"},
  # ROBES (slug: robes)
  {"name":"Robe midi fleurie","description":"Robe longueur midi en viscose imprimé fleuri coloré, col V, manches bouffantes, ceinture à nouer. Style romantique estival.","price":72.00,"brand":"& Other Stories","category_slug":"robes"},
  {"name":"Robe noire fourreau","description":"Robe fourreau en crêpe noir, col carré, sans manches, fermeture zip dos. Coupe élégante et structurée pour soirée.","price":110.00,"brand":"Claudie Pierlot","category_slug":"robes"},
  {"name":"Robe en velours bordeaux","description":"Robe mi-longue en velours bordeaux, col V profond, manches longues évasées, style années 70 chic et sensuel.","price":95.00,"brand":"ba&sh","category_slug":"robes"},
  # VESTES (slug: vestes)
  {"name":"Veste en cuir noir biker","description":"Veste courte en cuir véritable noir, col mao, fermeture éclair asymétrique argentée, coupe ajustée. Style rock intemporel.","price":249.00,"brand":"The Kooples","category_slug":"vestes"},
  {"name":"Blazer oversize beige","description":"Blazer slouchy en laine beige sable, revers larges, double boutonnage, épaules tombantes. Style androgyne et moderne.","price":149.00,"brand":"COS","category_slug":"vestes"},
  {"name":"Manteau long camel","description":"Manteau long droit en lainage camel, col châle, ceinture amovible, poches intérieures. Classique chic pour l'hiver.","price":320.00,"brand":"Totême","category_slug":"vestes"},
  # CHAUSSURES (slug: chaussures)
  {"name":"Sneakers blanches minimalistes","description":"Baskets basses en cuir blanc, semelle épaisse légèrement plateforme, lacets plats. Design épuré et polyvalent.","price":119.00,"brand":"Common Projects","category_slug":"chaussures"},
  {"name":"Bottines Chelsea marron","description":"Boots Chelsea en cuir marron cognac, élastiques latéraux, bout carré, semelle crantée. Pratiques et élégantes.","price":145.00,"brand":"Vagabond","category_slug":"chaussures"},
  {"name":"Sandales plates dorées","description":"Sandales à lanières fines en cuir doré, semelle ultra-plate, boucle dorée réglable. Style grec et intemporel.","price":85.00,"brand":"Ancient Greek Sandals","category_slug":"chaussures"},
  # ACCESSOIRES (slug: accessoires)
  {"name":"Sac tote en toile naturelle","description":"Grand tote bag en coton naturel écru, anses longues en cuir, intérieur doublé avec poche zip. Pratique et éco-responsable.","price":55.00,"brand":"Baggu","category_slug":"accessoires"},
  {"name":"Écharpe en soie imprimée","description":"Carré en soie 90x90cm, imprimé géométrique multicolore, bords roulottés main. Peut se porter en foulard, bandeau ou pochette.","price":89.00,"brand":"Hermès","category_slug":"accessoires"},
  {"name":"Ceinture cuir réversible","description":"Ceinture réversible noir/cognac en cuir pleine fleur, boucle dorée interchangeable, largeur 3cm. Deux looks en une.","price":65.00,"brand":"Maje","category_slug":"accessoires"},
  {"name":"Bob en lin blanc","description":"Chapeau bob en lin blanc naturel, bord moyen, intérieur coton. Léger et respirant, idéal pour l'été.","price":38.00,"brand":"Jacquemus","category_slug":"accessoires"},
  {"name":"Lunettes de soleil rondes","description":"Monture métallique fine dorée, verres ronds teintés brun dégradé, protection UV400. Style vintage années 70.","price":95.00,"brand":"Ray-Ban","category_slug":"accessoires"},
]

db = SessionLocal()
count = 0
for a in ARTICLES:
    slug = a.pop("category_slug")
    cat  = db.query(Category).filter(Category.slug == slug).first()
    if not cat:
        print(f"⚠ Catégorie '{slug}' introuvable")
        continue
    if not db.query(Article).filter(Article.name == a["name"]).first():
        db.add(Article(**a, category_id=cat.id))
        count += 1
db.commit()
db.close()
print(f"✓ {count} articles insérés")