import time
from typing import Any, Optional

class TTLCache:
    def __init__(self):
        self._store: dict = {}
    
    def set(self, key: str, value: Any, ttl_seconds: int = 1800):
        self._store[key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds
        }
    
    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry["expires_at"]:
            del self._store[key]
            return None
        return entry["value"]
    
    def clear(self, key: str):
        self._store.pop(key, None)

briefing_cache = TTLCache()
