#!/usr/bin/env python3
"""Live, non-destructive browser smoke QA for Denton Fence's GitHub Pages DEMO.

Does not submit forms, edit files, or authorize production launch.
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

BASE = "https://atrezzostudiosv-spec.github.io/denton-fence/"
ROUTES = [
    "", "about-us/", "services/", "specials/", "gallery/", "contact/",
    "services/wood-privacy-fences/", "services/ornamental-iron-fences/",
    "services/chain-link-fences/", "services/ranch-style-fences/",
    "services/vinyl-fences/", "services/fence-staining/",
    "services/fence-repairs/", "services/driveway-gates/",
    "services/gate-operators/",
]
WIDTHS = [375, 768, 1024, 1440]
FAILURES = []
REPORT = {"base": BASE, "pages": [], "image_assets_checked": 0, "interaction_checks": [], "failures": FAILURES}

def record(msg):
    FAILURES.append(msg)
    print("FAIL:", msg, flush=True)

def get(url, limit=40, attempts=3):
    err = None
    for attempt in range(attempts):
        try:
            request=Request(url,headers={"User-Agent":"AtrezzoDemo-QA/1.0"})
            with urlopen(request, timeout=25) as response:
                return response.status, response.headers.get("content-type",""), response.read(limit)
        except Exception as exc:
            err=exc
            if attempt < attempts-1:
                time.sleep(3)
    raise RuntimeError(f"Cannot access {url}: {err}")

def main():
    # HTTP: 15 entrypoints plus all 54 assets, without downloading each file.
    for route in ROUTES:
        url=BASE+route
        try:
            status,kind,opening=get(url,1024)
            if status!=200 or "text/html" not in kind:
                record(f"HTTP {status} {kind} at {url}")
        except Exception as e:
            record(str(e))
    root=Path(__file__).resolve().parents[1]
    assets=sorted((root/"assets/images").iterdir())
    if len(assets)!=54:
        record(f"Expected 54 tracked original image assets, found {len(assets)}")
    for file in assets:
        url=BASE+"assets/images/"+file.name
        try:
            status,kind,opening=get(url,24)
            if status!=200 or not ("image/webp" in kind if file.suffix==".webp" else "image/png" in kind):
                record(f"Asset HTTP/content-type unexpected: {file.name} {status} {kind}")
            else:
                REPORT["image_assets_checked"]+=1
        except Exception as e:
            record(str(e))
    if FAILURES:
        print("HTTP/image check has errors; stopping browser QA for truthful triage")
        finish()

    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,args=["--no-sandbox"])
        for width in WIDTHS:
            context=browser.new_context(viewport={"width":width,"height":900},device_scale_factor=1)
            for route in ROUTES:
                path=BASE+route
                page=context.new_page()
                crashes=[]
                page.on("pageerror",lambda error: crashes.append(str(error)))
                try:
                    response=page.goto(path,wait_until="domcontentloaded",timeout=35000)
                    page.wait_for_selector("h1",timeout=10000)
                    page.wait_for_timeout(150)
                    result=page.evaluate("""() => ({
                      width:innerWidth,
                      documentWidth:document.documentElement.scrollWidth,
                      h1:document.querySelectorAll('h1').length,
                      noindex:!!document.querySelector('meta[name="robots"][content*="noindex"]'),
                      loadedImages:[...document.images].filter(i=>i.complete&&i.naturalWidth>0).length,
                      brokenImages:[...document.images].filter(i=>i.complete&&i.naturalWidth===0&&i.getAttribute('src')).map(i=>i.getAttribute('src'))
                    })""")
                    if not response or response.status!=200:
                        record(f"Browser response not 200: {width} {route}")
                    if result["documentWidth"]>width+3:
                        record(f"Horizontal overflow: {width} {route} {result['documentWidth']}")
                    if result["h1"]!=1 or not result["noindex"]:
                        record(f"Headings or noindex invalid: {width} {route} {result}")
                    if result["brokenImages"]:
                        record(f"Browser broken images: {width} {route}: {result['brokenImages'][:3]}")
                    if crashes:
                        record(f"Page JS exceptions at {width} {route}: {crashes[:3]}")
                    REPORT["pages"].append({"path":route or "/", "width":width,**result})
                except Exception as e:
                    record(f"Browser test {width} {route}: {e}")
                finally:
                    page.close()
            context.close()
        # Keyboard menu (mobile)
        context=browser.new_context(viewport={"width":375,"height":850})
        page=context.new_page()
        try:
            page.goto(BASE,wait_until="domcontentloaded",timeout=35000)
            page.locator(".menu-toggle").click()
            if page.locator(".menu-toggle").get_attribute("aria-expanded")!="true":
                record("Mobile menu did not open")
            page.keyboard.press("Escape")
            if page.locator(".menu-toggle").get_attribute("aria-expanded")!="false":
                record("Mobile menu did not close on Escape")
            else:
                REPORT["interaction_checks"].append("mobile menu open / Escape close")
            page.goto(BASE+"gallery/",wait_until="domcontentloaded",timeout=35000)
            page.locator('[data-filter="wood"]').click()
            count=page.locator(".project:visible").count()
            if count!=10:record(f"Wood gallery filter expected 10, got {count}")
            else:REPORT["interaction_checks"].append("wood gallery filter 10")
            page.locator(".project:visible .project-open").first.click()
            if not page.locator(".gallery-dialog").evaluate("(d)=>d.open"):
                record("Gallery photo dialog did not open")
            page.keyboard.press("Escape")
            if page.locator(".gallery-dialog").evaluate("(d)=>d.open"):
                record("Gallery dialog did not close on Escape")
            else:REPORT["interaction_checks"].append("gallery dialog open / Escape close")
        except Exception as e:
            record(f"Interactions: {e}")
        page.close()
        context.close()
        browser.close()
    finish()

def finish():
    path=Path("qa-live-results.json")
    path.write_text(json.dumps(REPORT,indent=2)+"\n",encoding="utf8")
    print("Pages rendered:",len(REPORT["pages"]),"of",len(ROUTES)*len(WIDTHS))
    print("Image endpoints verified:",REPORT["image_assets_checked"],"of 54")
    print("Interactive checks:",REPORT["interaction_checks"])
    print("Failures:",len(FAILURES))
    if FAILURES: raise SystemExit(1)

if __name__=="__main__":
    main()
