import os, re, json, httpx

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
_cache: dict[str, dict] = {}


async def _get_text(url: str) -> str:
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15,
                                     headers={"User-Agent": "IndiaTrack/2.0"}) as c:
            r = await c.get(url)
        html = re.sub(r"<(script|style|nav|footer|header)[^>]*>.*?</\1>",
                      "", r.text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", text).strip()[:3500]
    except Exception as e:
        return f"[fetch failed: {e}]"


async def analyze(url: str, title: str, snippet: str, sectors: list[str]) -> dict:
    """
    Returns JSON:
      summary      — 2-3 sentence factual summary
      signal       — "bullish" | "bearish" | "neutral" (overall market tone)
      reason       — one-line overall market reasoning
      sector_impact — list of {sector, impact, reason, index} dicts
    """
    if not API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set on server.")
    if url in _cache:
        return _cache[url]

    body = await _get_text(url)
    sectors_str = ", ".join(sectors) if sectors else "none identified"

    prompt = f"""You are a senior Indian market analyst writing for Dalal Street investors.

Article title: {title}
Snippet: {snippet}
Tagged sectors: {sectors_str}
Article text: {body}

Respond ONLY with this exact JSON (no markdown, no extra text):
{{
  "summary": "2-3 sentence plain factual summary of the news",
  "signal": "bullish" or "bearish" or "neutral",
  "reason": "one sentence: overall impact on Indian markets",
  "sector_impact": [
    {{
      "sector": "exact sector name from tagged list",
      "impact": "bullish" or "bearish" or "neutral",
      "reason": "max 15 words: why this news affects this sector",
      "index": "relevant NSE index e.g. Nifty Bank, Nifty IT, Nifty Auto"
    }}
  ]
}}

Rules:
- Only include sectors from the tagged list above
- impact must be exactly: bullish, bearish, or neutral
- reason must be factual, not speculative
- max 3 sectors in sector_impact
- Valid JSON only, no extra text"""

    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": "claude-sonnet-4-6", "max_tokens": 600,
                  "messages": [{"role": "user", "content": prompt}]},
        )

    if r.status_code != 200:
        raise ValueError(f"Anthropic API error {r.status_code}")

    raw = r.json()["content"][0]["text"].strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    result = json.loads(raw)
    _cache[url] = result
    return result
