import asyncio
import re
import httpx
from app.rss import parse_feed
from app.sectors import tag_sectors

FEEDS = [
    # ── MARKETS / BUSINESS ────────────────────────────────────────────────────
    {"url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",  "source": "Economic Times",    "category": "markets"},
    {"url": "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",   "source": "Economic Times",    "category": "business"},
    {"url": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms","source":"Economic Times",  "category": "economy"},
    {"url": "https://www.livemint.com/rss/markets",                                  "source": "Mint",              "category": "markets"},
    {"url": "https://www.livemint.com/rss/companies",                                "source": "Mint",              "category": "business"},
    {"url": "https://www.livemint.com/rss/economy",                                  "source": "Mint",              "category": "economy"},
    {"url": "https://www.thehindubusinessline.com/markets/rss?id=markets",           "source": "BusinessLine",      "category": "markets"},
    {"url": "https://www.thehindubusinessline.com/economy/rss?id=economy",           "source": "BusinessLine",      "category": "economy"},
    {"url": "https://www.moneycontrol.com/rss/results.xml",                          "source": "MoneyControl",      "category": "markets"},
    {"url": "https://www.moneycontrol.com/rss/business.xml",                         "source": "MoneyControl",      "category": "business"},

    # ── TOP NEWS / NATIONAL ───────────────────────────────────────────────────
    {"url": "https://feeds.feedburner.com/ndtvnews-top-stories",                     "source": "NDTV",              "category": "top"},
    {"url": "https://www.thehindu.com/news/national/feeder/default.rss",             "source": "The Hindu",         "category": "national"},
    {"url": "https://indianexpress.com/section/india/feed/",                         "source": "Indian Express",    "category": "national"},
    {"url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",            "source": "Times of India",    "category": "top"},
    {"url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",       "source": "Hindustan Times",   "category": "national"},

    # ── GOVERNMENT / POLICY ───────────────────────────────────────────────────
    {"url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",               "source": "PIB India",         "category": "policy"},
    {"url": "https://www.thehindu.com/business/Economy/feeder/default.rss",          "source": "The Hindu",         "category": "economy"},
    {"url": "https://indianexpress.com/section/business/economy/feed/",              "source": "Indian Express",    "category": "economy"},

    # ── TECHNOLOGY ────────────────────────────────────────────────────────────
    {"url": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",       "source": "Economic Times",    "category": "technology"},
    {"url": "https://www.livemint.com/rss/technology",                               "source": "Mint",              "category": "technology"},

    # ── STARTUPS ──────────────────────────────────────────────────────────────
    {"url": "https://economictimes.indiatimes.com/small-biz/startups/rssfeeds/14590210.cms","source":"Economic Times","category":"startups"},
    {"url": "https://www.livemint.com/rss/startup",                                  "source": "Mint",              "category": "startups"},

    # ── COMMODITIES ───────────────────────────────────────────────────────────
    {"url": "https://economictimes.indiatimes.com/markets/commodities/rssfeeds/2146842.cms","source":"Economic Times","category":"commodities"},
]

_FAKE = re.compile(
    r"you won.?t believe|shocking truth|one weird trick|"
    r"secret they don.?t want|100% proof|plandemic|wake up",
    re.IGNORECASE,
)


async def _fetch(client: httpx.AsyncClient, meta: dict) -> list[dict]:
    try:
        r = await client.get(meta["url"], timeout=12)
        arts = parse_feed(r.text, meta)
        result = []
        for a in arts:
            if _FAKE.search(a["title"]):
                continue
            # tag stocks
            a["sectors"] = tag_sectors(a["title"], a["summary"])
            result.append(a)
        return result
    except Exception as e:
        print(f"[feed] {meta['source']}: {e}")
        return []


async def fetch_all() -> list[dict]:
    async with httpx.AsyncClient(
        follow_redirects=True,
        headers={"User-Agent": "IndiaTrack/1.0 (News Aggregator)"},
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
