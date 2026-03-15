import asyncio
import re
import httpx
from app.rss import parse_feed
from app.sectors import tag_sectors

FEEDS = [
    # ── TOP / BREAKING (India) ─────────────────────────────────────────────────
    {"url": "https://feeds.feedburner.com/ndtvnews-top-stories",                          "source": "NDTV",              "category": "top"},
    {"url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",                 "source": "Times of India",    "category": "top"},
    {"url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",            "source": "Hindustan Times",   "category": "top"},

    # ── NATIONAL (India) ───────────────────────────────────────────────────────
    {"url": "https://www.thehindu.com/news/national/feeder/default.rss",                  "source": "The Hindu",         "category": "national"},
    {"url": "https://indianexpress.com/section/india/feed/",                              "source": "Indian Express",    "category": "national"},
    {"url": "https://www.thehindu.com/news/national/rss?id=national",                     "source": "The Hindu",         "category": "national"},
    {"url": "https://feeds.feedburner.com/ndtvnews-india-news",                           "source": "NDTV",              "category": "national"},
    {"url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",                 "source": "Times of India",    "category": "national"},

    # ── GOVERNMENT / POLICY (India) ────────────────────────────────────────────
    {"url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",                    "source": "PIB India",         "category": "policy"},
    {"url": "https://indianexpress.com/section/business/economy/feed/",                   "source": "Indian Express",    "category": "policy"},
    {"url": "https://www.thehindu.com/business/Economy/feeder/default.rss",               "source": "The Hindu",         "category": "policy"},

    # ── MARKETS (India) ────────────────────────────────────────────────────────
    {"url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",       "source": "Economic Times",    "category": "markets"},
    {"url": "https://www.livemint.com/rss/markets",                                       "source": "Mint",              "category": "markets"},
    {"url": "https://www.thehindubusinessline.com/markets/rss?id=markets",                "source": "BusinessLine",      "category": "markets"},
    {"url": "https://www.moneycontrol.com/rss/results.xml",                               "source": "MoneyControl",      "category": "markets"},

    # ── BUSINESS (India) ───────────────────────────────────────────────────────
    {"url": "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",        "source": "Economic Times",    "category": "business"},
    {"url": "https://www.livemint.com/rss/companies",                                     "source": "Mint",              "category": "business"},
    {"url": "https://www.moneycontrol.com/rss/business.xml",                              "source": "MoneyControl",      "category": "business"},

    # ── ECONOMY (India) ────────────────────────────────────────────────────────
    {"url": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",  "source": "Economic Times",    "category": "economy"},
    {"url": "https://www.livemint.com/rss/economy",                                       "source": "Mint",              "category": "economy"},
    {"url": "https://www.thehindubusinessline.com/economy/rss?id=economy",                "source": "BusinessLine",      "category": "economy"},

    # ── TECHNOLOGY (India) ─────────────────────────────────────────────────────
    {"url": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",            "source": "Economic Times",    "category": "technology"},
    {"url": "https://www.livemint.com/rss/technology",                                    "source": "Mint",              "category": "technology"},

    # ── STARTUPS (India) ───────────────────────────────────────────────────────
    {"url": "https://economictimes.indiatimes.com/small-biz/startups/rssfeeds/14590210.cms", "source": "Economic Times", "category": "startups"},
    {"url": "https://www.livemint.com/rss/startup",                                       "source": "Mint",             "category": "startups"},

    # ── COMMODITIES (India) ────────────────────────────────────────────────────
    {"url": "https://economictimes.indiatimes.com/markets/commodities/rssfeeds/2146842.cms", "source": "Economic Times", "category": "commodities"},

    # ══ INTERNATIONAL ══════════════════════════════════════════════════════════

    # ── WORLD NEWS ─────────────────────────────────────────────────────────────
    {"url": "https://feeds.bbci.co.uk/news/world/rss.xml",                                "source": "BBC News",          "category": "world"},
    {"url": "https://www.theguardian.com/world/rss",                                      "source": "The Guardian",      "category": "world"},
    {"url": "https://www.aljazeera.com/xml/rss/all.xml",                                  "source": "Al Jazeera",        "category": "world"},
    {"url": "https://feeds.skynews.com/feeds/rss/world.xml",                              "source": "Sky News",          "category": "world"},
    {"url": "https://feeds.npr.org/1001/rss.xml",                                         "source": "NPR",               "category": "world"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",                     "source": "NY Times",          "category": "world"},

    # ── GLOBAL MARKETS ─────────────────────────────────────────────────────────
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",                  "source": "NY Times",          "category": "global-markets"},
    {"url": "https://www.theguardian.com/business/rss",                                   "source": "The Guardian",      "category": "global-markets"},
    {"url": "https://feeds.bbci.co.uk/news/business/rss.xml",                             "source": "BBC News",          "category": "global-markets"},
    {"url": "https://feeds.skynews.com/feeds/rss/business.xml",                           "source": "Sky News",          "category": "global-markets"},

    # ── GLOBAL TECH ────────────────────────────────────────────────────────────
    {"url": "https://feeds.arstechnica.com/arstechnica/index",                            "source": "Ars Technica",      "category": "global-tech"},
    {"url": "https://www.wired.com/feed/rss",                                             "source": "Wired",             "category": "global-tech"},
    {"url": "https://thenextweb.com/feed/",                                               "source": "The Next Web",      "category": "global-tech"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",                "source": "NY Times",          "category": "global-tech"},

    # ── GEOPOLITICS (Asia focus — relevant to India) ───────────────────────────
    {"url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml",                           "source": "BBC News",          "category": "geopolitics"},
    {"url": "https://www.theguardian.com/world/asia/rss",                                 "source": "The Guardian",      "category": "geopolitics"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",                     "source": "NY Times",          "category": "geopolitics"},

    # ── SCIENCE & CLIMATE ──────────────────────────────────────────────────────
    {"url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",              "source": "BBC News",          "category": "science"},
    {"url": "https://www.theguardian.com/science/rss",                                    "source": "The Guardian",      "category": "science"},
    {"url": "https://www.nasa.gov/rss/dyn/breaking_news.rss",                             "source": "NASA",              "category": "science"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Climate.xml",                   "source": "NY Times",          "category": "science"},
]

_FAKE = re.compile(
    r"you won.?t believe|shocking truth|one weird trick|"
    r"secret they don.?t want|100% proof|plandemic|wake up",
    re.IGNORECASE,
)

# Categories that belong to India (local/national)
INDIA_CATEGORIES = {
    "top", "national", "policy", "markets",
    "business", "economy", "technology",
    "startups", "commodities",
}

# Categories that are international
INTERNATIONAL_CATEGORIES = {
    "world", "global-markets", "global-tech",
    "geopolitics", "science",
}


async def _fetch(client: httpx.AsyncClient, meta: dict) -> list[dict]:
    try:
        r = await client.get(meta["url"], timeout=12)
        arts = parse_feed(r.text, meta)
        result = []
        for a in arts:
            if _FAKE.search(a["title"]):
                continue
            a["sectors"] = tag_sectors(a["title"], a["summary"])
            # Tag whether article is india or international
            a["region"] = "india" if meta["category"] in INDIA_CATEGORIES else "international"
            result.append(a)
        return result
    except Exception as e:
        print(f"[feed] {meta['source']} ({meta['category']}): {e}")
        return []


async def fetch_all() -> list[dict]:
    async with httpx.AsyncClient(
        follow_redirects=True,
        headers={"User-Agent": "IndiaTrack/2.0 (News Aggregator)"},
    ) as client:
        batches = await asyncio.gather(*[_fetch(client, m) for m in FEEDS])

    seen: set[str] = set()
    out: list[dict] = []
    for batch in batches:
        for a in batch:
            if a["url"] and a["url"] not in seen:
                seen.add(a["url"])
                out.append(a)

    out.sort(key=lambda x: x["published"], reverse=True)
    return out