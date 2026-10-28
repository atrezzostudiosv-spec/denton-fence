#!/usr/bin/env python3
"""Denton Fence original-gallery import. Run only with user authorization.

Source: https://dentonfence.net/gallery/ and https://dentonfence.net/
Uses the project's checked image-manifest. Images are not synthetic.
"""
from __future__ import annotations

import io
import json
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "images"
GALLERY = "https://dentonfence.net/gallery/"
HOME = "https://dentonfence.net/"
MEDIA_BASE = "https://dentonfence.net/wp-content/uploads/2021/03/"
MANIFEST = ROOT / "assets" / "image-manifest.json"
# Design-approved Home V1 image roles. Preserve their exact output filenames.
HOME_IMAGES = {
    "denton-tx-cedar-privacy-fence-hero.webp": "047.jpg",
    "denton-wood-privacy-fence-detail.webp": "board-on-board-with-cap.jpg",
    "denton-ornamental-iron-fencing.webp": "2012-07-31-10.27.36_gallery.jpg",
    "north-texas-ranch-style-wood-fence.webp": "191_gallery.jpg",
    "denton-wood-fence-installation.webp": "112.jpg",
    "denton-black-ornamental-iron-fence.webp": "045_gallery.jpg",
    "texas-white-ranch-fence.webp": "2005-08-26-14.20.53_gallery.jpg",
    "denton-cedar-wood-gate-gallery.webp": "097.jpg",
    "denton-ranch-wood-gate.webp": "5-15-2013-022_gallery.jpg",
}
HEADERS = {"User-Agent": "AtrezzoStudios-DentonFence-AssetImporter/1.0 (image reproduction authorized for design preview)"}
MAX_DOWNLOAD = 18_000_000

class MediaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        if tag not in {"a", "img", "source"}:
            return
        vals = dict(attrs)
        for key in ("href", "src", "data-src", "data-full-url", "data-large-file"):
            if vals.get(key):
                self.urls.append(vals[key])
        if vals.get("srcset"):
            self.urls.extend(x.strip().split(" ")[0] for x in vals["srcset"].split(",") if x.strip())

def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers=HEADERS)
    with urlopen(request, timeout=35) as response:
        kind = response.headers.get("content-type", "")
        if not any(t in kind.lower() for t in ("image/", "text/html", "application/octet-stream")):
            raise RuntimeError(f"Unexpected content-type {kind}: {url}")
        body = response.read(MAX_DOWNLOAD + 1)
        if len(body) > MAX_DOWNLOAD:
            raise RuntimeError(f"Source too large: {url}")
        return body

def discover(page: str) -> dict[str, str]:
    parser = MediaParser()
    parser.feed(fetch_bytes(page).decode("utf-8", "replace"))
    paths = {}
    for href in parser.urls:
        absolute = urljoin(page, href)
        filename = unquote(urlparse(absolute).path).split("/")[-1]
        if filename:
            paths.setdefault(filename.casefold(), absolute)
    return paths

def get_picture(name: str, discovered: dict[str, str]) -> Image.Image:
    target = discovered.get(name.casefold())
    urls = [x for x in [target, MEDIA_BASE + quote(name)] if x]
    errors = []
    for url in dict.fromkeys(urls):
        try:
            img = Image.open(io.BytesIO(fetch_bytes(url)))
            img.verify()
            img = Image.open(io.BytesIO(fetch_bytes(url)))
            img.load()
            if img.width < 200 or img.height < 100:
                raise RuntimeError("Image too small")
            print(f"OK source {name}: {url} [{img.width}x{img.height}]")
            return img
        except (OSError, ValueError, RuntimeError, UnidentifiedImageError) as ex:
            errors.append(f"{url}: {ex}")
    raise RuntimeError("Unable to obtain approved source image " + name + "\n" + "\n".join(errors))

def encode_webp(img: Image.Image, dest: Path, width: int = 1600):
    photo = ImageOps.exif_transpose(img)
    if photo.mode not in ("RGB", "RGBA"):
        photo = photo.convert("RGB")
    photo.thumbnail((width, 1500), Image.Resampling.LANCZOS)
    photo.save(dest, "WEBP", quality=82, method=6)
    if dest.stat().st_size < 500:
        raise RuntimeError(f"Encoded image unexpectedly small: {dest}")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    specs = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert len(specs) == 44, "Gallery manifest unexpectedly changed"
    gallery_urls = discover(GALLERY)
    home_urls = discover(HOME)
    cache: dict[str, Image.Image] = {}
    for spec in specs:
        name = spec["name"]
        if name.casefold() not in cache:
            cache[name.casefold()] = get_picture(name, gallery_urls)
        encode_webp(cache[name.casefold()], OUT / spec["file"], int(spec["width"]))
        print("Wrote", spec["file"])
    for output, original in HOME_IMAGES.items():
        if original.casefold() not in cache:
            cache[original.casefold()] = get_picture(original, gallery_urls)
        encode_webp(cache[original.casefold()], OUT / output)
        print("Wrote", output)

    # Original logo (no regeneration or changing its identity).
    logo = "webLogo1.png"
    logo_url = home_urls.get(logo.casefold(), MEDIA_BASE + quote(logo))
    png = fetch_bytes(logo_url)
    im = Image.open(io.BytesIO(png))
    im.verify()
    im = Image.open(io.BytesIO(png))
    im.load()
    if im.width < 50 or im.height < 20:
        raise RuntimeError("Source logo dimensions are not credible")
    im.save(OUT / "denton-fence-original-logo.png", optimize=True)
    print("Wrote original logo", im.size, "from", logo_url)
    expected = 44 + len(HOME_IMAGES) + 1
    all_files = [x for x in OUT.iterdir() if x.suffix.lower() in (".webp", ".png")]
    if len(all_files) < expected:
        raise RuntimeError(f"Incomplete assets {len(all_files)} < {expected}")
    print("COMPLETE", len(all_files), "assets; total", sum(x.stat().st_size for x in all_files), "bytes")

if __name__ == "__main__":
    main()
