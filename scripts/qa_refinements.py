#!/usr/bin/env python3
"""Automated user-approved Phase 4 refinement QA, no real emails are sent."""
from __future__ import annotations
import json, re, socket, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROUTES=["","about-us/","contact/","gallery/","services/","specials/",
"services/wood-privacy-fences/","services/ornamental-iron-fences/","services/chain-link-fences/",
"services/ranch-style-fences/","services/vinyl-fences/","services/fence-staining/",
"services/fence-repairs/","services/driveway-gates/","services/gate-operators/"]
ROOT=Path(__file__).resolve().parents[1]
issues=[]
tests=[]
def check(ok, label):
    (tests if ok else issues).append(label)
    if not ok: print("FAIL:",label,flush=True)

def main():
    for route in ROUTES:
        text=(ROOT/route/"index.html").read_text(encoding="utf-8")
        check("refinements.css" in text and "refinements.js" in text, route+" new styles and script")
        check("noindex" in text, route+" remains noindex")
        check(not re.search(r"[\u2190-\u21ff]",text), route+" without arrow-text glyphs")
        if route=="contact/":
            check("form.jotform.com" not in text and "<iframe" not in text,"legacy Jotform removed")
            check("formsubmit.co/atrezzostudiosv@gmail.com" in text,"real fallback form action to Atrezzo")
    class QuietHandler(SimpleHTTPRequestHandler):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,directory=str(ROOT),**kwargs)
        def log_message(self,*args):pass
    http=ThreadingHTTPServer(("127.0.0.1",0),QuietHandler)
    thread=threading.Thread(target=http.serve_forever,daemon=True)
    thread.start()
    base="http://127.0.0.1:"+str(http.server_address[1])+"/"
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
            for width in [375,768,1024,1440]:
                ctx=browser.new_context(viewport={"width":width,"height":900},reduced_motion="no-preference")
                for route in ROUTES:
                    page=ctx.new_page()
                    errors=[]
                    page.on("pageerror",lambda e:errors.append(str(e)))
                    response=page.goto(base+route,wait_until="networkidle",timeout=30000)
                    result=page.evaluate("""() => ({
                      h1:document.querySelectorAll('h1').length,
                      sw:document.documentElement.scrollWidth,
                      noindex:!!document.querySelector('meta[name="robots"][content*="noindex"]'),
                      broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth&&i.getAttribute('src')).map(i=>i.src)
                    })""")
                    check(response.status==200 and result["h1"]==1 and result["noindex"],str(width)+" "+route+" H1/noindex/HTTP")
                    check(result["sw"]<=width+2,str(width)+" "+route+" no horizontal overflow "+str(result["sw"]))
                    check(not result["broken"],str(width)+" "+route+" original images decode")
                    check(not errors,str(width)+" "+route+" JS no errors "+str(errors[:2]))
                    page.close()
                ctx.close()
            # A complete quote can open from Home and Contact without navigating away.
            ctx=browser.new_context(viewport={"width":375,"height":812})
            page=ctx.new_page()
            page.goto(base,wait_until="networkidle")
            page.locator(".header-cta").click()
            dlg=page.locator(".quote-modal")
            check(dlg.evaluate("(d)=>d.open"),"Home header CTA opens native modal")
            check(page.locator(".quote-modal .quote-form [name=email]").count()==1,"One modal form email field")
            check(page.locator(".quote-modal .quote-form").get_attribute("action").endswith("atrezzostudiosv@gmail.com"),"Modal targets Atrezzo")
            page.keyboard.press("Escape")
            check(not dlg.evaluate("(d)=>d.open"),"Modal closes by Escape")
            page.goto(base+"contact/",wait_until="networkidle")
            check(page.locator("form.quote-form").count()==1,"Contact has original Atrezzo-built inline form")
            check(page.locator("form.quote-form [name=service] option").count()==11,"Nine services and two guidance choices")
            check(page.locator("iframe").count()==0,"No old iframe")
            check("rgba(0, 0, 0" in page.locator(".inner-quote").evaluate("(e)=>getComputedStyle(e,'::after').backgroundImage"),"CTA photo black overlay")
            page.locator(".header-cta").click()
            check(page.locator(".quote-modal").evaluate("(e)=>e.open"),"Contact page CTA opens popup")
            page.locator(".quote-modal-close").click()
            # All form submissions are intercepted in browser; no email is sent.
            page.route("https://formsubmit.co/ajax/**",lambda r:r.fulfill(status=200,content_type="application/json",body='{"success":"true","message":"Accepted"}'))
            page.locator("#inline-name").fill("Atrezzo QA test")
            page.locator("#inline-email").fill("test@example.com")
            page.locator("#inline-service").select_option("wood-privacy-fences")
            page.locator("#inline-message").fill("Synthetic message for browser-only QA, no real mail.")
            page.locator(".form-frame .quote-privacy input").check()
            page.locator(".form-frame .quote-submit").click()
            page.wait_for_timeout(300)
            status=page.locator(".form-frame .quote-status").inner_text()
            check("provider accepted" in status.lower() and "confirm delivery" in status.lower(),"Provider acknowledgement does not falsely assert inbox receipt")
            # Gallery still works after refinements.
            page.goto(base+"gallery/",wait_until="networkidle")
            page.locator('[data-filter="wood"]').click()
            check(page.locator(".project:visible").count()==10,"Gallery filter displays ten original wood projects")
            page.locator(".project:visible .project-open").first.click()
            check(page.locator(".gallery-dialog").evaluate("(e)=>e.open"),"Gallery lightbox opens")
            page.keyboard.press("Escape")
            check(not page.locator(".gallery-dialog").evaluate("(e)=>e.open"),"Gallery lightbox keyboard close")
            ctx.close()
            # Responsive scroll zoom is an actual changing transform, not disabled on tablet/mob.
            for width in [375,768,1024]:
                ctx=browser.new_context(viewport={"width":width,"height":840},reduced_motion="no-preference")
                page=ctx.new_page()
                page.goto(base,wait_until="networkidle")
                section=page.locator(".chapter").first
                section.scroll_into_view_if_needed()
                page.wait_for_timeout(160)
                value1=float(section.evaluate("(e)=>getComputedStyle(e).getPropertyValue('--photo-scale')||1"))
                page.evaluate("window.scrollBy(0,230)")
                page.wait_for_timeout(200)
                value2=float(section.evaluate("(e)=>getComputedStyle(e).getPropertyValue('--photo-scale')||1"))
                photo_transform=section.locator("img").evaluate("(e)=>getComputedStyle(e).transform")
                check(abs(value2-value1)>.0004 and photo_transform!="none",str(width)+" scroll drives photo scale "+str([value1,value2]))
                ctx.close()
            # Reduced motion must stop image transform.
            ctx=browser.new_context(viewport={"width":375,"height":800},reduced_motion="reduce")
            page=ctx.new_page()
            page.goto(base,wait_until="networkidle")
            check(page.locator(".chapter-photo").first.evaluate("(e)=>getComputedStyle(e).transform")=="none","Reduced motion keeps photos static")
            ctx.close()
            browser.close()
    finally:
        http.shutdown()
    report={"checks":len(tests)+len(issues),"passed":len(tests),"failed":len(issues),"errors":issues}
    Path("qa-refinement-results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2),flush=True)
    if issues:raise SystemExit(1)

if __name__=="__main__":
    main()
