import asyncio, time
from app.feeds import fetch_all

_cache: dict = {"data": [], "at": 0.0, "lock": None}
TTL = 300

def _lock():
    if _cache["lock"] is None:
        _cache["lock"] = asyncio.Lock()
    return _cache["lock"]

async def get_articles() -> list[dict]:
    async with _lock():
        if time.time() - _cache["at"] > TTL or not _cache["data"]:
            print("[cache] refreshing India feeds …")
            _cache["data"] = await fetch_all()
            _cache["at"]   = time.time()
            print(f"[cache] {len(_cache['data'])} articles loaded")
        return _cache["data"]
