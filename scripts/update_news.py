import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
import urllib.request

TWITTER_HANDLE = "FootParadiseArt"
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.lucabased.xyz",
]
UPDATES_FILE = Path("updates.json")
IMAGES_DIR   = Path("imagenes")

def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", errors="replace")

def try_nitter():
    for base in NITTER_INSTANCES:
        url = f"{base}/{TWITTER_HANDLE}"
        try:
            print(f"Probando {url}...")
            html = fetch_url(url)
            if TWITTER_HANDLE.lower() in html.lower():
                print(f"  ✓ OK")
                return html, base
        except Exception as e:
            print(f"  ✗ {e}")
    raise RuntimeError("Ninguna instancia de Nitter disponible")

def parse_tweets(html, nitter_base):
    tweets = []
    blocks = re.split(r'<div class="timeline-item\s*">', html)[1:]

    for block in blocks:
        if 'class="retweet-header"' in block or 'Retweeted' in block:
            continue

        id_match = re.search(r'/status/(\d+)', block)
        if not id_match:
            continue
        tweet_id = id_match.group(1)

        text_match = re.search(
            r'<div class="tweet-content[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL
        )
        text = ""
        if text_match:
            text = re.sub(r'<[^>]+>', '', text_match.group(1)).strip()
            text = re.sub(r'\s+', ' ', text)

        img_match = re.search(r'<img[^>]+src="([^"]+/pic/[^"]+)"', block) \
                 or re.search(r'<a[^>]+href="(/pic/[^"]+)"', block)
        img_url = ""
        if img_match:
            raw = img_match.group(1)
            if raw.startswith("/"):
                raw = nitter_base + raw
            img_url = raw

        tweets.append({"id": tweet_id, "text": text, "img_url": img_url})

    return tweets

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
    html, nitter_base = try_nitter()
    tweets = parse_tweets(html, nitter_base)
    print(f"Tweets encontrados: {len(tweets)}")

    data = load_updates()
    known = existing_ids(data)
    max_id = max((u["id"] for u in data["updates"]), default=0)

    added = 0
    for tweet in tweets:
        if tweet["id"] in known:
            continue

        max_id += 1
        today = datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d")
        twitter_url = f"https://x.com/{TWITTER_HANDLE}/status/{tweet['id']}"
        image_path = download_image(tweet["img_url"], tweet["id"])

        # Orden exacto de claves como en el JSON original
        entry = {
            "id": max_id,
            "date": today,
            "title": tweet["text"][:60] + ("..." if len(tweet["text"]) > 60 else ""),
            "description": tweet["text"],
            "image": image_path,
            "twitter": twitter_url,
        }

        data["updates"].insert(0, entry)
        print(f"  + {tweet['id']}: {entry['title']}")
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
