from sentence_transformers import SentenceTransformer

# Modèle léger multilingue (français inclus), ~470MB téléchargé une fois
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model

def generate_embedding(text: str) -> list[float]:
    """Génère un vecteur d'embedding pour un texte."""
    model = get_embedding_model()
    return model.encode(text).tolist()