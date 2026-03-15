# 🇮🇳 IndiaTrack — India News & NSE Stock Impact

India-focused news aggregator with live NSE prices, stock tagging, and AI market impact analysis via Claude.

## Stack
- **Backend** — Python FastAPI + httpx + stdlib XML (Python 3.13 safe, only 3 packages)
- **Frontend** — React + Vite
- **Prices** — Yahoo Finance (free, no API key)
- **AI** — Anthropic Claude (optional, for market impact analysis)

## Features
- 📰 20+ trusted Indian news sources (ET, Mint, BusinessLine, NDTV, Hindu, PIB, MoneyControl…)
- 📈 Live NSE stock prices via Yahoo Finance (15-min delayed)
- 🏷 Auto-tags each article with affected NSE symbols
- ✦ Claude AI: bullish/bearish/neutral signal + per-stock impact reason
- 📡 Scrolling live ticker of top gainers/losers
- 🔍 Filter news by stock symbol, category, source, keyword
- ⚠️ Built-in disclaimer — not financial advice

## Local Development

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload
```
→ http://localhost:8000
→ http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
→ http://localhost:5173

---

## Deploy

### Render (backend)
1. New Web Service → connect GitHub repo
2. Root: `backend` | Build: `pip install -r requirements.txt`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Env vars:
   - `ANTHROPIC_API_KEY` = `sk-ant-...` (get from console.anthropic.com)
   - `ALLOWED_ORIGINS` = `https://your-app.vercel.app`

### Vercel (frontend)
1. Import GitHub repo, set root = `frontend`
2. Env var: `VITE_API_URL` = `https://your-render-url.onrender.com`

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/news` | Articles. Params: `category`, `source`, `stock`, `q`, `limit` |
| `GET /api/prices` | Live NSE prices. Param: `symbols` (comma-separated) |
| `GET /api/prices/top` | Top 5 gainers + losers |
| `GET /api/stats` | Article counts, top tagged stocks |
| `POST /api/analyze` | Claude AI market impact analysis |
| `GET /docs` | Swagger UI |

---

## Stock Tagging
`backend/app/stocks.py` contains the full keyword → NSE symbol map.
Add your own mappings easily — just extend the `KEYWORD_MAP` dict.

## Disclaimer
This tool is for informational purposes only. Stock tags are auto-generated
from keyword matching and are indicative only. This is not SEBI-registered
financial advice. Always consult a qualified advisor before investing.
