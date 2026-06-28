"""Indexe tous les articles PostgreSQL dans ChromaDB."""
import app.core.database as database
from app.core.chroma import get_collection
from app.services.embedding_service import generate_embedding
from app.models.article import Article
from app.core.config import settings

database.init_engine(settings.DATABASE_URL)

db = database.SessionLocal()
collection = get_collection()

articles = db.query(Article).all()
print(f"📦 {len(articles)} articles à indexer...")

ids, embeddings, metadatas, documents = [], [], [], []

for article in articles:
    text = f"{article.name}. {article.description}"
    vec = generate_embedding(text)
    ids.append(str(article.id))
    embeddings.append(vec)
    documents.append(text)
    metadatas.append({
        "article_id": article.id,
        "category_id": article.category_id,
        "price": article.price,
        "name": article.name
    })

    # Sauvegarder l'embedding_id sur l'article
    article.embedding_id = str(article.id)
if ids:
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )
    db.commit()

db.close()
print(f"✓ {len(ids)} articles indexés dans ChromaDB")