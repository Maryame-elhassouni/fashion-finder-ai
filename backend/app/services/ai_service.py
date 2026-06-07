import json
import google.generativeai as genai
from backend.app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

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

def classify_category(description: str) -> str:
    prompt = f'Classe ce vêtement. Description: "{description}". Réponds UN SEUL MOT parmi: hauts, bas, robes, vestes, chaussures, accessoires'
    try:
        resp  = model.generate_content(prompt)
        slug  = resp.text.strip().lower().split()[0]
        valid = {"hauts","bas","robes","vestes","chaussures","accessoires"}
        return slug if slug in valid else "hauts"
    except:
        return "hauts"    
    