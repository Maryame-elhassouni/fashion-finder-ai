import chromadb
from pathlib import Path

CHROMA_DIR = Path(__file__).resolve().parents[2] / "chroma_data"
CHROMA_DIR.mkdir(exist_ok=True)

chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

def get_collection():
    """Récupère ou crée la collection des articles."""
    return chroma_client.get_or_create_collection(
        name="fashion_articles",
        metadata={"hnsw:space": "cosine"}
    )