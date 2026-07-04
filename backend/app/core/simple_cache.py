"""
Cache mémoire simple avec TTL — alternative à Redis pour le développement.
Évite de refaire le même appel Gemini deux fois en quelques minutes.
"""
import time
import hashlib

_cache: dict[str, tuple[float, any]] = {}
TTL_SECONDS = 3600  # 1 heure

def make_cache_key(*args) -> str:
    raw = "|".join(str(a) for a in args)
    return hashlib.md5(raw.encode()).hexdigest()

def cache_get(key: str):
    if key in _cache:
        expires_at, value = _cache[key]
        if time.time() < expires_at:
            return value
        else:
            del _cache[key]
    return None

def cache_set(key: str, value, ttl: int = TTL_SECONDS):
    _cache[key] = (time.time() + ttl, value)

def cache_stats() -> dict:
    return {"entries": len(_cache)}