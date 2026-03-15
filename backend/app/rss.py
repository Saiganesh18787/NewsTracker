import xml.etree.ElementTree as ET
import re
from datetime import datetime, timezone
from typing import Optional

NS = {
    "media":   "http://search.yahoo.com/mrss/",
    "atom":    "http://www.w3.org/2005/Atom",
    "yt":      "http://www.youtube.com/xml/schemas/2015",
    "dc":      "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}
for p, u in NS.items():
    ET.register_namespace(p, u)

def _t(ns, name): return f"{{{NS[ns]}}}{name}"
def _tx(el): return (el.text or "").strip() if el is not None else ""

def _strip(raw):
    c = re.sub(r"<[^>]+>", " ", raw or "")
    return re.sub(r"\s+", " ", c).strip()[:300]

def _date(raw):
    if not raw: return datetime.now(timezone.utc).isoformat()
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT",
                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f%z"):
        try: return datetime.strptime(raw.strip(), fmt).isoformat()
        except: pass
    return raw

def _img(el):
    t = el.find(_t("media","thumbnail"))
    if t is not None: return t.get("url")
    for mc in el.findall(_t("media","content")):
        if "image" in mc.get("type",""): return mc.get("url")
    enc = el.find("enclosure")
    if enc is not None and "image" in enc.get("type",""): return enc.get("url")
    return None

def parse_feed(xml_text: str, meta: dict) -> list[dict]:
    try: root = ET.fromstring(xml_text)
    except: return []
    is_atom = "atom" in root.tag.lower() or root.tag == "feed"
    out = []
    entries = (root.findall(_t("atom","entry")) or root.findall("entry")) if is_atom else \
              (root.find("channel") or root).findall("item")
    for e in entries[:15]:
        if is_atom:
            title = _tx(e.find(_t("atom","title")) or e.find("title"))
            link  = (e.find(_t("atom","link")) or e.find("link"))
            url   = link.get("href","") if link is not None else ""
            summ  = _strip(_tx(e.find(_t("atom","summary")) or e.find("summary") or e.find(_t("content","encoded"))))
            date  = _date(_tx(e.find(_t("atom","published")) or e.find("published") or e.find(_t("atom","updated"))))
        else:
            title = _tx(e.find("title"))
            url   = _tx(e.find("link"))
            summ  = _strip(_tx(e.find(_t("content","encoded")) or e.find("description")))
            date  = _date(_tx(e.find("pubDate") or e.find(_t("dc","date"))))
        if title:
            out.append({"id": url, "title": title, "summary": summ, "url": url,
                        "published": date, "source": meta["source"],
                        "category": meta["category"], "image": _img(e)})
    return out
