#!/usr/bin/env python3
"""Download small, local, attributed photographs so the site does not depend on external image CDNs."""
import io, json, re, time
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "images"
PHOTOS = IMG / "photos"
PLATFORM_LOGOS = IMG / "platforms"
HEADERS = {"User-Agent": "VAEZI-INDUSTRY/1.0 (tourism editorial site; image attribution retained)"}

SOURCES = {
    "isfahan": {
        "title": "Naqsh-e Jahan Square, Isfahan",
        "author": "Armin Dadvand",
        "source": "https://commons.wikimedia.org/wiki/File:Naqshe_jahan_SQ.jpg",
        "license": "CC BY-SA 4.0",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Naqshe_jahan_SQ.jpg/960px-Naqshe_jahan_SQ.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/66/Naqshe_jahan_SQ.jpg/960px-Naqshe_jahan_SQ.jpg",
        ],
    },
    "yazd": {
        "title": "Windcatchers in Yazd",
        "author": "Ms96",
        "source": "https://commons.wikimedia.org/wiki/File:Windcatchers_in_Yazd.jpg",
        "license": "CC BY-SA (see source page)",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Windcatchers_in_Yazd.jpg/960px-Windcatchers_in_Yazd.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/ce/Windcatchers_in_Yazd.jpg/960px-Windcatchers_in_Yazd.jpg",
        ],
    },
    "rasht": {
        "title": "Masuleh Village, Gilan",
        "author": "Mojtaba Matboyi",
        "source": "https://commons.wikimedia.org/wiki/File:Masuleh_Village.jpg",
        "license": "CC BY-SA 4.0",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Masuleh_Village.jpg/960px-Masuleh_Village.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e1/Masuleh_Village.jpg/960px-Masuleh_Village.jpg",
        ],
    },
    "shiraz": {
        "title": "Nasir al-Mulk Mosque, Shiraz",
        "author": "Faraz Ahanin",
        "source": "https://commons.wikimedia.org/wiki/File:Nasir_al-Mulk_Mosque_-_Shiraz.jpg",
        "license": "CC0 1.0",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Nasir_al-Mulk_Mosque_-_Shiraz.jpg/960px-Nasir_al-Mulk_Mosque_-_Shiraz.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/17/Nasir_al-Mulk_Mosque_-_Shiraz.jpg/960px-Nasir_al-Mulk_Mosque_-_Shiraz.jpg",
        ],
    },
    "kish": {
        "title": "Beach, Kish Island",
        "author": "Ivan Mlinaric",
        "source": "https://commons.wikimedia.org/wiki/File:Beach_Kish_Island_Iran.jpg",
        "license": "CC BY 2.0",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Beach_Kish_Island_Iran.jpg/960px-Beach_Kish_Island_Iran.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c5/Beach_Kish_Island_Iran.jpg/960px-Beach_Kish_Island_Iran.jpg",
        ],
    },
    "qeshm": {
        "title": "Star Valley, Qeshm Island",
        "author": "Qeshmnil",
        "source": "https://commons.wikimedia.org/wiki/File:Qeshm_Island_Star_Valley,_Iran.jpg",
        "license": "CC BY-SA 4.0",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Qeshm_Island_Star_Valley%2C_Iran.jpg/960px-Qeshm_Island_Star_Valley%2C_Iran.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/88/Qeshm_Island_Star_Valley%2C_Iran.jpg/960px-Qeshm_Island_Star_Valley%2C_Iran.jpg",
        ],
    },
    "tehran": {
        "title": "Azadi Tower, Tehran",
        "author": "Mostafa Meraji",
        "source": "https://commons.wikimedia.org/wiki/File:Azadi_Tower_In_Tehran.jpg",
        "license": "CC0 1.0",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Azadi_Tower_In_Tehran.jpg/960px-Azadi_Tower_In_Tehran.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b5/Azadi_Tower_In_Tehran.jpg/960px-Azadi_Tower_In_Tehran.jpg",
        ],
    },
    "persepolis": {
        "title": "Persepolis Columns",
        "author": "Abbas Sarhadi",
        "source": "https://commons.wikimedia.org/wiki/File:Persepolis_Columns.jpg",
        "license": "CC BY-SA 4.0",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Persepolis_Columns.jpg/960px-Persepolis_Columns.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1c/Persepolis_Columns.jpg/960px-Persepolis_Columns.jpg",
        ],
    },
    "desert": {
        "title": "Kaluts of Shahdad, Lut Desert",
        "author": "Salehi1990mohsen",
        "source": "https://commons.wikimedia.org/wiki/File:Kaluts_of_Shahdad.jpg",
        "license": "CC BY-SA 4.0",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Kaluts_of_Shahdad.jpg/960px-Kaluts_of_Shahdad.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/41/Kaluts_of_Shahdad.jpg/960px-Kaluts_of_Shahdad.jpg",
        ],
    },
    "guesthouse": {
        "title": "Traditional Hotel, Yazd",
        "author": "s1ingshot",
        "source": "https://commons.wikimedia.org/wiki/File:Traditional_hotel_Yazd.jpg",
        "license": "CC BY 2.0",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Traditional_hotel_Yazd.jpg/960px-Traditional_hotel_Yazd.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f0/Traditional_hotel_Yazd.jpg/960px-Traditional_hotel_Yazd.jpg",
        ],
    },
}
BRANDS = {
    "jabama": {"name": "جاباما", "domain": "www.jabama.com", "letter": "ج", "color": "#167764"},
    "mihmansho": {"name": "میهمان‌شو", "domain": "www.mihmansho.com", "letter": "م", "color": "#b88135"},
    "shab": {"name": "شب", "domain": "shab.ir", "letter": "ش", "color": "#c86142"},
    "jajiga": {"name": "جاجیگا", "domain": "www.jajiga.com", "letter": "ج", "color": "#317b85"},
    "otaghak": {"name": "اتاقک", "domain": "www.otaghak.com", "letter": "ا", "color": "#5266a1"},
}
PLATFORM_PHOTOS = {
    "jabama": "guesthouse",
    "mihmansho": "rasht",
    "shab": "kish",
    "jajiga": "qeshm",
    "otaghak": "yazd",
}

def download(url):
    with urlopen(Request(url, headers=HEADERS), timeout=25) as response:
        return response.read(8_000_000)

def save_jpeg(key, data, output):
    im = Image.open(io.BytesIO(data))
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((960, 720), Image.Resampling.LANCZOS)
    output.parent.mkdir(parents=True, exist_ok=True)
    im.save(output, "JPEG", quality=76, optimize=True, progressive=True)
    if output.stat().st_size > 260_000:
        im.save(output, "JPEG", quality=68, optimize=True, progressive=True)
    if output.stat().st_size > 320_000:
        im.thumbnail((800, 600), Image.Resampling.LANCZOS)
        im.save(output, "JPEG", quality=64, optimize=True, progressive=True)
    if output.stat().st_size < 7_000:
        raise RuntimeError("Downloaded image is suspiciously small: " + key)

def write_fallback_logo(key, brand):
    out = PLATFORM_LOGOS / (key + ".svg")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 100"><rect width="240" height="100" rx="18" fill="{brand["color"]}"/><circle cx="55" cy="50" r="28" fill="#ffffff" fill-opacity=".16"/><text x="55" y="61" font-family="Arial,sans-serif" font-weight="700" font-size="32" text-anchor="middle" fill="#ffffff">{brand["letter"]}</text><text x="201" y="57" font-family="Arial,sans-serif" font-weight="700" font-size="21" text-anchor="end" fill="#ffffff">{brand["name"]}</text></svg>'''
    out.write_text(svg, encoding="utf-8")

def download_logo(key, brand):
    PLATFORM_LOGOS.mkdir(parents=True, exist_ok=True)
    output = PLATFORM_LOGOS / (key + ".png")
    candidates = [
        "https://" + brand["domain"] + "/favicon.ico",
        "https://" + brand["domain"] + "/favicon.png",
        "https://" + brand["domain"] + "/favicon-32x32.png",
    ]
    for url in candidates:
        try:
            data = download(url)
            im = Image.open(io.BytesIO(data)).convert("RGBA")
            im.thumbnail((128, 128), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (128, 128), (255, 255, 255, 0))
            canvas.alpha_composite(im, ((128 - im.width) // 2, (128 - im.height) // 2))
            canvas.save(output, "PNG", optimize=True)
            if output.stat().st_size > 80_000:
                output.unlink(missing_ok=True)
                continue
            print("Logo downloaded:", key, url)
            write_fallback_logo(key, brand)
            return
        except Exception as exc:
            print("Logo fallback:", key, url, exc)
    write_fallback_logo(key, brand)

def main():
    PHOTOS.mkdir(parents=True, exist_ok=True)
    credits = {"licenseNote": "Image credits and license links are shown on the destination page. Photographs were resized for web delivery.", "photos": {}}
    for key, meta in SOURCES.items():
        output = PHOTOS / (key + ".jpg")
        if not output.exists() or output.stat().st_size < 7_000:
            last = None
            for url in meta["urls"]:
                try:
                    save_jpeg(key, download(url), output)
                    last = None
                    break
                except Exception as exc:
                    last = exc
                    print("Photo source failed:", key, url, exc)
            if last is not None:
                raise RuntimeError("Could not download licensed photo for " + key + ": " + str(last))
        credits["photos"][key] = {
            "title": meta["title"], "author": meta["author"], "source": meta["source"], "license": meta["license"],
            "localFile": "assets/images/photos/" + key + ".jpg",
        }
        print("Photo ready:", key, output.stat().st_size, "bytes")
        time.sleep(.1)
    for key, brand in BRANDS.items():
        download_logo(key, brand)
    # Prepare wide, locally served platform imagery from already-compressed city/accommodation photographs.
    for brand, photo in PLATFORM_PHOTOS.items():
        target = PLATFORM_LOGOS / (brand + "-cover.jpg")
        source = PHOTOS / (photo + ".jpg")
        im = Image.open(source).convert("RGB")
        im = ImageOps.fit(im, (960, 420), method=Image.Resampling.LANCZOS, centering=(.5, .46))
        im.save(target, "JPEG", quality=72, optimize=True, progressive=True)
        credits["photos"]["platform-" + brand] = {
            "title": "Illustrative accommodation/travel photograph: " + SOURCES[photo]["title"],
            "author": SOURCES[photo]["author"], "source": SOURCES[photo]["source"],
            "license": SOURCES[photo]["license"], "localFile": "assets/images/platforms/" + brand + "-cover.jpg",
            "note": "Illustrative editorial image, not an official listing or endorsement from the platform."
        }
    (IMG / "credits.json").write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Photo and license manifest ready.")

if __name__ == "__main__":
    main()
