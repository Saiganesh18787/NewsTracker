import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.cache import get_articles
from app.sectors import SECTORS, get_sector
from app.summarizer import analyze

app = FastAPI(title="IndiaTrack API", version="2.0")

origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/")
async def root():
    return {"status": "ok", "app": "IndiaTrack", "docs": "/docs"}


@app.get("/api/news")
async def news(
    category: str = Query("all"),
    source:   str = Query("all"),
    sector:   str = Query(""),
    q:        str = Query(""),
    limit:    int = Query(60),
):
    arts = await get_articles()
    if category != "all":
        arts = [a for a in arts if a["category"] == category]
    if source != "all":
        arts = [a for a in arts if a["source"] == source]
    if sector:
        arts = [a for a in arts if sector in a.get("sectors", [])]
    if q:
        ql = q.lower()
        arts = [a for a in arts
                if ql in a["title"].lower() or ql in a["summary"].lower()]
    return {"total": len(arts), "articles": arts[:limit]}


@app.get("/api/categories")
async def categories():
    arts = await get_articles()
    cats = sorted({a["category"] for a in arts})
    return {"categories": ["all"] + cats}


@app.get("/api/sources")
async def sources():
    arts = await get_articles()
    srcs = sorted({a["source"] for a in arts})
    return {"sources": ["all"] + srcs}


@app.get("/api/sectors")
async def sectors_list():
    """Return all sector definitions with metadata."""
    return {
        "sectors": [
            {"name": name, **SECTORS[name]}
            for name in SECTORS
        ]
    }


@app.get("/api/sectors/trending")
async def trending_sectors():
    """Return sectors ranked by number of articles mentioning them today."""
    arts = await get_articles()
    counts: dict[str, int] = {}
    for a in arts:
        for s in a.get("sectors", []):
            counts[s] = counts.get(s, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    result = []
    for name, count in ranked:
        info = get_sector(name)
        result.append({
            "name": name, "count": count,
            "icon": info["icon"], "color": info["color"],
            "index": info["index"],
        })
    return {"trending": result}


@app.get("/api/stats")
async def stats():
    arts = await get_articles()
    by_src = {}; by_cat = {}; by_sector = {}
    for a in arts:
        by_src[a["source"]]   = by_src.get(a["source"], 0)   + 1
        by_cat[a["category"]] = by_cat.get(a["category"], 0) + 1
        for s in a.get("sectors", []):
            by_sector[s] = by_sector.get(s, 0) + 1
    top = sorted(by_sector.items(), key=lambda x: x[1], reverse=True)[:8]
    return {
        "total": len(arts), "by_source": by_src,
        "by_category": by_cat, "top_sectors": top,
    }


@app.post("/api/analyze")
async def analyze_article(payload: dict):
    url     = payload.get("url", "")
    title   = payload.get("title", "")
    snippet = payload.get("summary", "")
    sectors = payload.get("sectors", [])
    if not url:
        raise HTTPException(400, "url is required")
    try:
        result = await analyze(url, title, snippet, sectors)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))
