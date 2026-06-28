import json
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_attributes(description: str) -> dict:
    prompt = f"""
Analyse cette description de vêtement et extrais ses attributs.
Description : "{description}"
Réponds UNIQUEMENT avec un JSON valide (sans markdown) :
{{"couleur":"...","matiere":"...","style":"...","coupe":"...","categorie_slug":"hauts|bas|robes|vestes|chaussures|accessoires"}}
"""
    try:
        resp = model.generate_content(prompt)
        text = resp.text.strip().replace("```json","").replace("```","").strip()
        return json.loads(text)
    except Exception as e:
        print(f"[Gemini] erreur: {e}")
        return {"couleur":"","matiere":"","style":"","coupe":"","categorie_slug":"hauts"}

def enrich_query(description: str) -> str:
    """
    Utilise Gemini pour enrichir la description utilisateur
    avant de générer son embedding — améliore la recherche vectorielle.
    """
    prompt = f"""
Reformule cette description de vêtement en ajoutant des synonymes et
termes mode pertinents pour améliorer une recherche. Reste concis (1 phrase).
Description : "{description}"
Réponds uniquement avec la description enrichie, sans préambule.
"""
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception:
        return description  # fallback sur la description originale