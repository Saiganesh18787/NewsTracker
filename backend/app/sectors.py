"""
Sector tagging engine for IndiaTrack.
Maps news keywords → affected Indian market sectors.
More reliable than individual stock prediction — news moves sectors, not just one stock.
"""

# ── Sector definitions ────────────────────────────────────────────────────────
# Each sector has: display name, icon, color, and representative NSE indices/ETFs
SECTORS: dict[str, dict] = {
    "Banking & Finance": {
        "icon": "🏦", "color": "#1a56db",
        "desc": "Banks, NBFCs, insurance, housing finance",
        "index": "Nifty Bank / Nifty Financial Services",
        "examples": "HDFC Bank, SBI, ICICI, Bajaj Finance, LIC",
    },
    "Information Technology": {
        "icon": "💻", "color": "#7c3aed",
        "desc": "IT services, software, BPO, digital",
        "index": "Nifty IT",
        "examples": "TCS, Infosys, Wipro, HCL Tech, Tech Mahindra",
    },
    "Oil & Gas": {
        "icon": "🛢", "color": "#b45309",
        "desc": "Exploration, refining, distribution, LPG",
        "index": "Nifty Oil & Gas",
        "examples": "Reliance, ONGC, BPCL, IOC, HPCL, GAIL",
    },
    "Pharmaceuticals": {
        "icon": "💊", "color": "#0891b2",
        "desc": "Drug makers, generic pharma, hospitals, diagnostics",
        "index": "Nifty Pharma",
        "examples": "Sun Pharma, Dr Reddy's, Cipla, Divi's, Lupin",
    },
    "Automobile & EV": {
        "icon": "🚗", "color": "#065f46",
        "desc": "Passenger cars, two-wheelers, EVs, auto components",
        "index": "Nifty Auto",
        "examples": "Maruti, Tata Motors, M&M, Bajaj Auto, Hero",
    },
    "Metals & Mining": {
        "icon": "⚙️", "color": "#64748b",
        "desc": "Steel, aluminium, copper, iron ore, coal",
        "index": "Nifty Metal",
        "examples": "Tata Steel, JSW Steel, Hindalco, SAIL, Coal India",
    },
    "FMCG & Consumer": {
        "icon": "🛒", "color": "#d97706",
        "desc": "Food, personal care, household goods, retail",
        "index": "Nifty FMCG",
        "examples": "HUL, ITC, Nestle, Britannia, Dabur, D-Mart",
    },
    "Infrastructure & Capital Goods": {
        "icon": "🏗", "color": "#b91c1c",
        "desc": "Roads, railways, ports, power, engineering",
        "index": "Nifty Infrastructure",
        "examples": "L&T, NTPC, Power Grid, Adani Ports, BHEL",
    },
    "Defence & Aerospace": {
        "icon": "🛡", "color": "#1e3a5f",
        "desc": "Defence PSUs, aerospace, shipbuilding",
        "index": "Nifty India Defence",
        "examples": "HAL, BEL, Mazagon Dock, GRSE, Cochin Shipyard",
    },
    "Real Estate": {
        "icon": "🏢", "color": "#7e22ce",
        "desc": "Residential, commercial, REITs, housing finance",
        "index": "Nifty Realty",
        "examples": "DLF, Godrej Properties, Prestige, Oberoi Realty",
    },
    "Renewable Energy": {
        "icon": "🌱", "color": "#15803d",
        "desc": "Solar, wind, green hydrogen, EV charging",
        "index": "Nifty India Green Energy",
        "examples": "Adani Green, Tata Power, SJVN, NTPC Green",
    },
    "Telecom & Media": {
        "icon": "📡", "color": "#0369a1",
        "desc": "Mobile, broadband, OTT, satellite, cable",
        "index": "Nifty Media",
        "examples": "Bharti Airtel, Reliance Jio, Vodafone Idea, Dish TV",
    },
    "Agri & Fertilisers": {
        "icon": "🌾", "color": "#4d7c0f",
        "desc": "Agri inputs, fertilisers, pesticides, food processing",
        "index": "Nifty Commodities",
        "examples": "Coromandel, Chambal Fertilisers, UPL, PI Industries",
    },
    "Aviation & Logistics": {
        "icon": "✈️", "color": "#0c4a6e",
        "desc": "Airlines, airports, shipping, freight, supply chain",
        "index": "Nifty India Transport",
        "examples": "IndiGo, SpiceJet, Adani Ports, Blue Dart, VRL",
    },
    "Cement & Construction Materials": {
        "icon": "🧱", "color": "#78350f",
        "desc": "Cement, steel pipes, tiles, paints",
        "index": "Nifty Commodities",
        "examples": "UltraTech, Ambuja, ACC, Shree Cement, Asian Paints",
    },
    "Consumer Tech & Startups": {
        "icon": "📱", "color": "#6d28d9",
        "desc": "Fintech, edtech, food delivery, e-commerce",
        "index": "Nifty India Digital",
        "examples": "Zomato, Paytm, Nykaa, PolicyBazaar, Swiggy",
    },
}

# ── Keyword → sector mapping ──────────────────────────────────────────────────
KEYWORD_SECTOR: dict[str, list[str]] = {
    # Banking & Finance
    "rbi":                  ["Banking & Finance"],
    "repo rate":            ["Banking & Finance"],
    "monetary policy":      ["Banking & Finance"],
    "interest rate":        ["Banking & Finance", "Real Estate"],
    "inflation":            ["Banking & Finance", "FMCG & Consumer"],
    "credit growth":        ["Banking & Finance"],
    "npa":                  ["Banking & Finance"],
    "bad loan":             ["Banking & Finance"],
    "bank":                 ["Banking & Finance"],
    "nbfc":                 ["Banking & Finance"],
    "microfinance":         ["Banking & Finance"],
    "insurance":            ["Banking & Finance"],
    "sebi":                 ["Banking & Finance"],
    "stock market":         ["Banking & Finance"],
    "sensex":               ["Banking & Finance"],
    "nifty":                ["Banking & Finance"],
    "fii":                  ["Banking & Finance"],
    "ipo":                  ["Banking & Finance"],
    "gdp":                  ["Banking & Finance", "Infrastructure & Capital Goods"],
    "budget":               ["Banking & Finance", "Infrastructure & Capital Goods", "FMCG & Consumer"],
    "union budget":         ["Banking & Finance", "Infrastructure & Capital Goods", "Defence & Aerospace"],
    "fiscal deficit":       ["Banking & Finance"],
    "gst":                  ["FMCG & Consumer", "Banking & Finance"],
    "disinvestment":        ["Banking & Finance", "Oil & Gas", "Metals & Mining"],

    # IT
    "it sector":            ["Information Technology"],
    "software":             ["Information Technology"],
    "h1b":                  ["Information Technology"],
    "visa":                 ["Information Technology"],
    "artificial intelligence": ["Information Technology"],
    "ai":                   ["Information Technology"],
    "cloud computing":      ["Information Technology"],
    "digital":              ["Information Technology", "Consumer Tech & Startups"],
    "cybersecurity":        ["Information Technology"],
    "outsourcing":          ["Information Technology"],
    "us recession":         ["Information Technology"],
    "dollar":               ["Information Technology", "Pharmaceuticals"],
    "rupee":                ["Information Technology", "Oil & Gas", "Pharmaceuticals"],

    # Oil & Gas
    "crude oil":            ["Oil & Gas", "Automobile & EV", "Aviation & Logistics"],
    "brent":                ["Oil & Gas"],
    "opec":                 ["Oil & Gas"],
    "natural gas":          ["Oil & Gas"],
    "petrol price":         ["Oil & Gas", "Automobile & EV"],
    "diesel price":         ["Oil & Gas", "Aviation & Logistics"],
    "fuel price":           ["Oil & Gas", "Aviation & Logistics"],
    "lpg":                  ["Oil & Gas"],
    "petroleum":            ["Oil & Gas"],

    # Pharma
    "usfda":                ["Pharmaceuticals"],
    "fda":                  ["Pharmaceuticals"],
    "drug":                 ["Pharmaceuticals"],
    "pharma":               ["Pharmaceuticals"],
    "medicine":             ["Pharmaceuticals"],
    "nlem":                 ["Pharmaceuticals"],
    "generic drug":         ["Pharmaceuticals"],
    "hospital":             ["Pharmaceuticals"],
    "health":               ["Pharmaceuticals"],
    "pandemic":             ["Pharmaceuticals"],
    "vaccine":              ["Pharmaceuticals"],

    # Auto
    "electric vehicle":     ["Automobile & EV", "Renewable Energy"],
    "ev":                   ["Automobile & EV", "Renewable Energy"],
    "automobile":           ["Automobile & EV"],
    "auto sales":           ["Automobile & EV"],
    "scrappage":            ["Automobile & EV"],
    "pli scheme":           ["Automobile & EV", "Pharmaceuticals", "Information Technology"],
    "vehicle":              ["Automobile & EV"],
    "two wheeler":          ["Automobile & EV"],

    # Metals
    "steel":                ["Metals & Mining"],
    "aluminium":            ["Metals & Mining"],
    "copper":               ["Metals & Mining"],
    "iron ore":             ["Metals & Mining"],
    "metal":                ["Metals & Mining"],
    "mining":               ["Metals & Mining"],
    "coal":                 ["Metals & Mining", "Renewable Energy"],
    "lithium":              ["Metals & Mining", "Automobile & EV"],

    # FMCG
    "fmcg":                 ["FMCG & Consumer"],
    "consumer":             ["FMCG & Consumer"],
    "rural demand":         ["FMCG & Consumer", "Agri & Fertilisers"],
    "retail":               ["FMCG & Consumer"],
    "fmcg sales":           ["FMCG & Consumer"],
    "food inflation":       ["FMCG & Consumer", "Agri & Fertilisers"],
    "edible oil":           ["FMCG & Consumer", "Agri & Fertilisers"],

    # Infrastructure
    "infrastructure":       ["Infrastructure & Capital Goods"],
    "capex":                ["Infrastructure & Capital Goods"],
    "power":                ["Infrastructure & Capital Goods", "Renewable Energy"],
    "electricity":          ["Infrastructure & Capital Goods", "Renewable Energy"],
    "railway":              ["Infrastructure & Capital Goods"],
    "road":                 ["Infrastructure & Capital Goods"],
    "port":                 ["Infrastructure & Capital Goods", "Aviation & Logistics"],
    "smart city":           ["Infrastructure & Capital Goods", "Real Estate"],
    "national highway":     ["Infrastructure & Capital Goods"],
    "water":                ["Infrastructure & Capital Goods"],

    # Defence
    "defence":              ["Defence & Aerospace"],
    "defense":              ["Defence & Aerospace"],
    "military":             ["Defence & Aerospace"],
    "border":               ["Defence & Aerospace"],
    "china":                ["Defence & Aerospace", "Information Technology"],
    "pakistan":             ["Defence & Aerospace"],
    "make in india":        ["Defence & Aerospace", "Infrastructure & Capital Goods"],
    "indigenisation":       ["Defence & Aerospace"],
    "war":                  ["Defence & Aerospace"],
    "arms":                 ["Defence & Aerospace"],

    # Real Estate
    "real estate":          ["Real Estate"],
    "housing":              ["Real Estate", "Banking & Finance"],
    "home loan":            ["Real Estate", "Banking & Finance"],
    "realty":               ["Real Estate"],
    "property":             ["Real Estate"],
    "stamp duty":           ["Real Estate"],
    "affordable housing":   ["Real Estate"],
    "reit":                 ["Real Estate"],

    # Renewables
    "solar":                ["Renewable Energy"],
    "wind energy":          ["Renewable Energy"],
    "green hydrogen":       ["Renewable Energy"],
    "renewable":            ["Renewable Energy"],
    "net zero":             ["Renewable Energy"],
    "carbon":               ["Renewable Energy"],
    "climate":              ["Renewable Energy", "Agri & Fertilisers"],
    "emission":             ["Renewable Energy"],

    # Telecom
    "telecom":              ["Telecom & Media"],
    "5g":                   ["Telecom & Media"],
    "spectrum":             ["Telecom & Media"],
    "broadband":            ["Telecom & Media"],
    "ott":                  ["Telecom & Media", "Consumer Tech & Startups"],
    "streaming":            ["Telecom & Media", "Consumer Tech & Startups"],

    # Agri
    "monsoon":              ["Agri & Fertilisers", "FMCG & Consumer"],
    "rainfall":             ["Agri & Fertilisers", "FMCG & Consumer"],
    "drought":              ["Agri & Fertilisers", "FMCG & Consumer"],
    "agri":                 ["Agri & Fertilisers"],
    "fertiliser":           ["Agri & Fertilisers"],
    "crop":                 ["Agri & Fertilisers"],
    "msp":                  ["Agri & Fertilisers", "FMCG & Consumer"],
    "kharif":               ["Agri & Fertilisers"],
    "rabi":                 ["Agri & Fertilisers"],
    "farmer":               ["Agri & Fertilisers"],

    # Aviation & Logistics
    "aviation":             ["Aviation & Logistics"],
    "airline":              ["Aviation & Logistics"],
    "airport":              ["Aviation & Logistics"],
    "shipping":             ["Aviation & Logistics"],
    "freight":              ["Aviation & Logistics"],
    "logistics":            ["Aviation & Logistics"],
    "supply chain":         ["Aviation & Logistics"],

    # Cement
    "cement":               ["Cement & Construction Materials"],
    "construction":         ["Cement & Construction Materials", "Infrastructure & Capital Goods"],
    "paint":                ["Cement & Construction Materials"],
    "tiles":                ["Cement & Construction Materials"],

    # Consumer Tech
    "startup":              ["Consumer Tech & Startups"],
    "fintech":              ["Consumer Tech & Startups", "Banking & Finance"],
    "ecommerce":            ["Consumer Tech & Startups"],
    "food delivery":        ["Consumer Tech & Startups"],
    "edtech":               ["Consumer Tech & Startups"],
    "upi":                  ["Consumer Tech & Startups", "Banking & Finance"],
    "digital payment":      ["Consumer Tech & Startups", "Banking & Finance"],
    "unicorn":              ["Consumer Tech & Startups"],
}


def tag_sectors(title: str, summary: str) -> list[str]:
    """Return unique sector names relevant to this article (max 4)."""
    text = (title + " " + summary).lower()
    matched: list[str] = []
    seen: set[str] = set()
    for keyword, sectors in KEYWORD_SECTOR.items():
        if keyword in text:
            for s in sectors:
                if s not in seen:
                    seen.add(s)
                    matched.append(s)
    return matched[:4]


def get_sector(name: str) -> dict:
    return SECTORS.get(name, {"icon": "📌", "color": "#6b7280",
                               "desc": name, "index": "—", "examples": "—"})
