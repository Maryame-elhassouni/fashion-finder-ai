from app.core.chroma import get_collection
from app.services.embedding_service import generate_embedding
from app.services.ai_service import enrich_query


def vector_search(
    description: str,
    category_id: int | None = None,
    n_results: int = 8
) -> list[dict]:
    """
    Pipeline complet de recherche vectorielle :
    1. Enrichir la description avec Gemini
    2. Générer l'embedding
    3. Chercher dans ChromaDB (avec filtre catégorie optionnel)
    4. Retourner les résultats avec score de similarité
    """

    enriched = enrich_query(description)
    query_vec = generate_embedding(enriched)

    collection = get_collection()

    where_filter = {"category_id": category_id} if category_id else None

    results = collection.query(
        query_embeddings=[query_vec],
        n_results=n_results,
        where=where_filter
    )

    output = []

    if results["ids"] and results["ids"][0]:
        for i, article_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i]

            # Convertir la distance cosinus en score de similarité (0 → 1)
            similarity_score = max(0.0, 1.0 - distance)

            output.append({
                "article_id": int(article_id),
                "similarity_score": round(similarity_score, 3),
                "metadata": results["metadatas"][0][i],
            })

    return output