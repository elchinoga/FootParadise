import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TWITTER_HANDLE = "FootParadiseArt"
TWITTER_COOKIES = os.environ["TWITTER_COOKIES"]
UPDATES_FILE = Path("updates.json")
IMAGES_DIR = Path("imagenes")

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_tweets(cookies_path, limit=30):
    cmd = [
        sys.executable, "-m", "gallery_dl",
        "--dump-json",
        "-o", f"cookies={cookies_path}",
        "-o", "twitter.retweets=false",
        "-o", "twitter.replies=false",
        "-o", "twitter.quoted=false",
        "-o", "twitter.text-tweets=true",
        "--range", f"1-{limit}",
        f"https://x.com/{TWITTER_HANDLE}/timeline",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=180)
    if result.returncode != 0:
        raise RuntimeError(f"gallery-dl fallo (code {result.returncode}):\n{result.stderr[-3000:]}")

    data = json.loads(result.stdout)

    items = {}
    for entry in data:
        if entry[0] != 3:
            continue
        media_url, meta = entry[1], entry[2]

        if meta.get("retweet_id") or meta.get("reply_id"):
            continue

        tweet_id = str(meta.get("tweet_id", ""))
        if not tweet_id or tweet_id in items:
            continue  # solo la primera imagen por tweet

        items[tweet_id] = {
            "id": tweet_id,
            "text": meta.get("content", ""),
            "img_url": media_url if isinstance(media_url, str) else "",
            "link": f"https://x.com/{TWITTER_HANDLE}/status/{tweet_id}",
        }

    return list(items.values())

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
        req = urllib.request.Request(img_url, headers=REQUEST_HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            dest.write_bytes(r.read())
        print(f"  Imagen: {dest}")
        return f"imagenes/{filename}"
    except Exception as e:
        print(f"  Sin imagen: {e}")
        return ""

def main():
    print("Obteniendo tweets via gallery-dl...")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(TWITTER_COOKIES)
        cookies_path = f.name

    try:
        items = fetch_tweets(cookies_path)
    finally:
        os.remove(cookies_path)

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
