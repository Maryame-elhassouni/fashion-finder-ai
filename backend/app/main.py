from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI(
    title="Fashion Finder IA",
    description="Recherche vestimentaire par description — propulsé par Gemini",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = [{"champ": str(e["loc"]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422,
                        content={"detail": "Données invalides", "errors": errors})

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Fashion Finder IA", "ia": "Gemini"}