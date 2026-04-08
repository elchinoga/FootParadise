import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path

RSS_URL      = os.environ["RSS_URL"]
UPDATES_FILE = Path("updates.json")
IMAGES_DIR   = Path("imagenes")
TWITTER_HANDLE = "FootParadiseArt"

def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read()
    raw = raw.decode("utf-8", errors="replace")
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)
    return raw.encode("utf-8")

def parse_rss(xml_bytes):
      from urllib.parse import unquote
      try:
          root = ET.fromstring(xml_bytes)
      except ET.ParseError:
          text = xml_bytes.decode("utf-8", errors="replace")
          text = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[\da-fA-F]+;)', '&amp;', text)
          root = ET.fromstring(text.encode("utf-8"))

      items = []

      for item in root.findall(".//item"):
          link = item.findtext("link") or ""

          # Solo posts propios de FootParadiseArt
          if "/FootParadiseArt/" not in link:
              continue

          # Saltar retweets
          title = item.findtext("title") or ""
          if title.startswith("RT @"):
              continue

          # Extraer tweet ID
          id_match = re.search(r'/status/(\d+)', link)
          if not id_match:
              continue
          tweet_id = id_match.group(1)

          # Convertir link de nitter a x.com
          twitter_url = f"https://x.com/FootParadiseArt/status/{tweet_id}"

          # Extraer imagen del HTML de description
          img_url = ""
          description = item.findtext("description") or ""
          img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', description)
          if img_match:
              nitter_img = img_match.group(1)
              # Convertir https://nitter.net/pic/media%2FXXX.jpg → https://pbs.twimg.com/media/XXX.jpg
              if "/pic/" in nitter_img:
                  pic_path = nitter_img.split("/pic/")[-1]
                  img_url = "https://pbs.twimg.com/" + unquote(pic_path)

          items.append({"id": tweet_id, "text": title, "img_url": img_url, "link": twitter_url})

      return items

def load_updates():
    if UPDATES_FILE.exists():
        return json.loads(UPDATES_FILE.read_text(encoding="utf-8"))
    return {"updates": []}

def existing_ids(data):
    ids = set()
    for u in data["updates"]:
        url = u.get("twitter", "")
        ids.add(url.split("/")[-1])
    return ids

def download_image(img_url, tweet_id):
    if not img_url:
        return ""
    IMAGES_DIR.mkdir(exist_ok=True)

    ext = "jpg"
    for candidate in [".png", ".gif", ".webp", ".jfif", ".jpeg"]:
        if candidate in img_url.lower():
            ext = candidate.lstrip(".")
            break

    filename = f"{tweet_id}.{ext}"
    dest = IMAGES_DIR / filename
    try:
        req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            dest.write_bytes(r.read())
        print(f"  Imagen: {dest}")
        return f"imagenes/{filename}"
    except Exception as e:
        print(f"  Sin imagen: {e}")
        return ""

def main():
    print("Obteniendo RSS...")
    xml_bytes = fetch_url(RSS_URL)
    items = parse_rss(xml_bytes)
    print(f"Posts encontrados: {len(items)}")

    data = load_updates()
    known = existing_ids(data)
    max_id = max((u["id"] for u in data["updates"]), default=0)

    added = 0
    for item in items:
        if item["id"] in known:
            continue

        max_id += 1
        today = datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d")
        image_path = download_image(item["img_url"], item["id"])

        entry = {
            "id": max_id,
            "date": today,
            "title": item["text"][:60] + ("..." if len(item["text"]) > 60 else ""),
            "description": item["text"],
            "image": image_path,
            "twitter": item["link"],
        }

        data["updates"].insert(0, entry)
        print(f"  + {item['id']}: {entry['title']}")
        added += 1

    if added == 0:
        print("Sin novedades.")
        return

    UPDATES_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"✓ updates.json actualizado con {added} entrada(s).")

if __name__ == "__main__":
    main()
