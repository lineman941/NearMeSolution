#!/usr/bin/env python3
"""Static site generator for nearmesolutions.pro — a North Florida local-services directory.
Usage: python3 build.py   (reads listings.json next to this file, writes ./dist)
"""
import json, os, shutil, html, datetime
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
DOMAIN = "https://nearmesolutions.pro"
CONTACT_EMAIL = "stump@nearmesolutions.pro"
SITE = "Near Me Solutions"
TAGLINE = "Vetted local pros in Perry, Tallahassee & North Florida"

SERVICES = {
    "stump-grinding": {"name": "Stump Grinding", "verb": "grind stumps",
        "blurb": "Fast, affordable stump removal after a tree comes down — yard-safe equipment, cleaned up when we leave."},
    "tree-removal":   {"name": "Tree Removal", "verb": "remove trees",
        "blurb": "Storm damage, dead pines, leaning oaks — local crews that drop, cut and haul."},
    "mobile-mechanic":{"name": "Mobile Mechanic", "verb": "fix your vehicle on-site",
        "blurb": "Repairs at your driveway or job site: brakes, batteries, starters, diagnostics, no tow needed."},
    "handyman":       {"name": "Handyman", "verb": "handle the small jobs",
        "blurb": "Repairs, installs, pressure washing and the punch-list nobody else will come out for."},
}
TOWNS = {
    "perry":       {"name": "Perry", "county": "Taylor County"},
    "tallahassee": {"name": "Tallahassee", "county": "Leon County"},
    "madison":     {"name": "Madison", "county": "Madison County"},
    "live-oak":    {"name": "Live Oak", "county": "Suwannee County"},
    "monticello":  {"name": "Monticello", "county": "Jefferson County"},
}

FEATURED = {
    "name": "Need A Hand Mobile (Stump Knockers)",
    "services": list(SERVICES), "towns": list(TOWNS),
    "email": CONTACT_EMAIL,
    "phone": "(850) 295-3235",
    "facebook": "https://www.facebook.com/share/1C7qi4wj4y/",
    "blurb": "Perry-based mobile crew: stump grinding, tree work, mobile auto repair and handyman jobs within 50 miles. Text-first, same-week scheduling, FSU/TCC student discounts.",
    "featured": True,
}

CSS = """
:root{--bg:#f7f6f2;--ink:#1c1f1a;--mut:#5c6358;--card:#fff;--line:#e3e1d8;--acc:#2f6b3a;--acc2:#e4a11b;--r:14px}
*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
a{color:var(--acc)}.wrap{max-width:1040px;margin:0 auto;padding:0 18px}
header{background:#fff;border-bottom:1px solid var(--line)}header .wrap{display:flex;align-items:center;justify-content:space-between;height:60px}
.logo{font-weight:800;text-decoration:none;color:var(--ink);font-size:18px}.logo span{color:var(--acc)}
nav a{margin-left:16px;text-decoration:none;color:var(--mut);font-size:15px}nav a.cta{background:var(--acc2);color:#1c1f1a;padding:8px 14px;border-radius:999px;font-weight:700}
.hero{padding:44px 0 28px}.hero h1{font-size:clamp(28px,5vw,44px);line-height:1.1;margin:0 0 10px}.hero p{font-size:18px;color:var(--mut);max-width:620px;margin:0 0 20px}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.tile{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:18px;text-decoration:none;color:var(--ink);display:block}.tile:hover{border-color:var(--acc)}
.tile h3{margin:0 0 6px;font-size:18px}.tile p{margin:0;color:var(--mut);font-size:14px}
h2{font-size:22px;margin:34px 0 12px}.chips a{display:inline-block;margin:0 8px 8px 0;padding:6px 12px;background:#fff;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--ink);font-size:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;margin:0 0 14px}
.card.feat{border:2px solid var(--acc2);position:relative}.card.feat:before{content:"Featured local pro";position:absolute;top:-11px;left:16px;background:var(--acc2);color:#1c1f1a;font-size:12px;font-weight:700;padding:2px 10px;border-radius:999px}
.card h3{margin:0 0 4px;font-size:19px}.card .meta{color:var(--mut);font-size:14px;margin:0 0 8px}.card p{margin:0 0 10px}
.btns a{display:inline-block;margin:0 8px 6px 0;padding:9px 14px;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;background:var(--acc);color:#fff}.btns a.alt{background:#fff;color:var(--acc);border:1px solid var(--acc)}
.note{background:#fff8e6;border:1px solid #f1d58a;border-radius:var(--r);padding:14px 16px;font-size:15px}
form{display:grid;gap:10px;max-width:520px}input,select,textarea{font:inherit;padding:10px;border:1px solid var(--line);border-radius:8px;width:100%}button{font:inherit;font-weight:700;padding:12px;border:0;border-radius:8px;background:var(--acc);color:#fff;cursor:pointer}
footer{margin-top:50px;padding:26px 0;border-top:1px solid var(--line);color:var(--mut);font-size:14px}footer a{color:var(--mut)}
.crumbs{font-size:14px;color:var(--mut);margin:18px 0 0}.crumbs a{color:var(--mut)}
@media(max-width:600px){nav a:not(.cta){display:none}}
"""

def esc(s): return html.escape(str(s), quote=True)

def page(title, desc, body, path, schema=None):
    url = DOMAIN + path
    ld = f'<script type="application/ld+json">{json.dumps(schema)}</script>' if schema else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="website">
<link rel="stylesheet" href="/style.css">{ld}</head><body>
<header><div class="wrap"><a class="logo" href="/">Near<span>Me</span>Solutions</a><nav><a href="/stump-grinding/">Stumps</a><a href="/tree-removal/">Trees</a><a href="/mobile-mechanic/">Mechanic</a><a href="/handyman/">Handyman</a><a class="cta" href="/get-listed/">Get listed</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">© {datetime.date.today().year} {SITE} · Perry, FL · <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> · <a href="/get-listed/">List your business</a><br><small>Listings are compiled from public sources. Own one of these businesses? <a href="/get-listed/">Claim or correct it</a>.</small></div></footer>
</body></html>"""

def listing_card(b, town=None):
    feat = b.get("featured")
    meta = []
    if town: meta.append(f"Serves {TOWNS[town]['name']}")
    meta.append(", ".join(SERVICES[s]["name"] for s in b["services"] if s in SERVICES))
    btns = []
    if b.get("phone"): btns.append(f'<a href="tel:{esc(b["phone"].replace(" ","").replace("(","").replace(")","").replace("-",""))}">Call {esc(b["phone"])}</a>')
    if b.get("email"): btns.append(f'<a href="mailto:{esc(b["email"])}?subject=Quote request via NearMeSolutions">Email for a quote</a>')
    if b.get("website"): btns.append(f'<a class="alt" href="{esc(b["website"])}" rel="nofollow noopener" target="_blank">Website</a>')
    if b.get("facebook"): btns.append(f'<a class="alt" href="{esc(b["facebook"])}" rel="nofollow noopener" target="_blank">Facebook</a>')
    return f'<div class="card{" feat" if feat else ""}"><h3>{esc(b["name"])}</h3><div class="meta">{esc(" · ".join(meta))}</div><p>{esc(b.get("blurb",""))}</p><div class="btns">{"".join(btns)}</div></div>'

def service_town_body(s, t, biz):
    S, T = SERVICES[s], TOWNS[t]
    cards = "".join(listing_card(b, t) for b in biz)
    others = "".join(f'<a href="/{s}/{o}/">{TOWNS[o]["name"]}</a>' for o in TOWNS if o != t)
    svcs = "".join(f'<a href="/{o}/{t}/">{SERVICES[o]["name"]}</a>' for o in SERVICES if o != s)
    return f"""<div class="crumbs"><a href="/">Home</a> › <a href="/{s}/">{esc(S['name'])}</a> › {esc(T['name'])}</div>
<div class="hero"><h1>{esc(S['name'])} in {esc(T['name'])}, FL</h1><p>Local pros who {esc(S['verb'])} in {esc(T['name'])} and {esc(T['county'])}. {esc(S['blurb'])}</p></div>
{cards}
<p class="note">Don't see your business? <a href="/get-listed/">Get listed free</a> — it takes two minutes.</p>
<h2>{esc(S['name'])} in nearby towns</h2><div class="chips">{others}</div>
<h2>Other services in {esc(T['name'])}</h2><div class="chips">{svcs}</div>"""

def build():
    data = json.loads((ROOT / "listings.json").read_text())["listings"]
    all_biz = [FEATURED] + data
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / "style.css").write_text(CSS)
    urls = ["/"]

    def write(path, content):
        p = DIST / path.strip("/") / "index.html" if path != "/" else DIST / "index.html"
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content)
        if path not in urls: urls.append(path)

    # home
    tiles = "".join(f'<a class="tile" href="/{s}/"><h3>{esc(v["name"])}</h3><p>{esc(v["blurb"])}</p></a>' for s, v in SERVICES.items())
    towns = "".join(f'<a href="/{"stump-grinding"}/{t}/">{esc(v["name"])}</a>' for t, v in TOWNS.items())
    body = f"""<div class="hero"><h1>Find a local pro near you.</h1><p>{TAGLINE}. Real businesses, real phone numbers, no middleman fees.</p></div>
<div class="grid">{tiles}</div>
<h2>Browse by town</h2><div class="chips">{towns}</div>
<h2>Featured local pro</h2>{listing_card(FEATURED)}
<p class="note">Run a service business in North Florida? <a href="/get-listed/">List it free</a>.</p>"""
    write("/", page(f"{SITE} — Local Pros Near Me in Perry & Tallahassee, FL", f"{TAGLINE}: stump grinding, tree removal, mobile mechanics and handymen with real phone numbers.", body, "/",
        {"@context":"https://schema.org","@type":"WebSite","name":SITE,"url":DOMAIN}))

    # service hubs
    for s, S in SERVICES.items():
        chips = "".join(f'<a class="tile" href="/{s}/{t}/"><h3>{esc(S["name"])} in {esc(T["name"])}</h3><p>{esc(T["county"])}</p></a>' for t, T in TOWNS.items())
        body = f'<div class="crumbs"><a href="/">Home</a> › {esc(S["name"])}</div><div class="hero"><h1>{esc(S["name"])} near me — North Florida</h1><p>{esc(S["blurb"])} Pick your town:</p></div><div class="grid">{chips}</div>'
        write(f"/{s}/", page(f"{S['name']} Near Me — Perry, Tallahassee & North FL | {SITE}", f"Local {S['name'].lower()} pros across Taylor, Leon, Madison, Suwannee and Jefferson counties.", body, f"/{s}/"))

    # service × town
    for s, S in SERVICES.items():
        for t, T in TOWNS.items():
            biz = [b for b in all_biz if s in b["services"] and t in b["towns"]]
            schema = {"@context":"https://schema.org","@type":"ItemList","name":f"{S['name']} in {T['name']}, FL","itemListElement":[
                {"@type":"ListItem","position":i+1,"item":{"@type":"LocalBusiness","name":b["name"],**({"telephone":b["phone"]} if b.get("phone") else {}),**({"url":b["website"]} if b.get("website") else {}),"areaServed":T["name"]}} for i,b in enumerate(biz)]}
            write(f"/{s}/{t}/", page(f"{S['name']} in {T['name']}, FL — {len(biz)} Local Pros | {SITE}", f"{S['name']} near {T['name']}, {T['county']}: {len(biz)} local businesses with phone numbers and websites. Free quotes.", service_town_body(s, t, biz), f"/{s}/{t}/", schema))

    # get listed
    opts_s = "".join(f'<option value="{s}">{esc(v["name"])}</option>' for s, v in SERVICES.items())
    opts_t = "".join(f'<option value="{t}">{esc(v["name"])}</option>' for t, v in TOWNS.items())
    body = f"""<div class="hero"><h1>Get listed — free.</h1><p>Add or claim your business. Featured placement (top of page, highlighted) is available for a small monthly fee once your listing is live.</p></div>
<form action="https://formsubmit.co/{CONTACT_EMAIL}" method="POST">
<input type="hidden" name="_subject" value="New listing request — NearMeSolutions"><input type="hidden" name="_captcha" value="false"><input type="hidden" name="_next" value="{DOMAIN}/get-listed/thanks/">
<input name="business" placeholder="Business name" required><input name="phone" placeholder="Phone" required><input name="email" type="email" placeholder="Email" required>
<input name="website" placeholder="Website or Facebook page (optional)">
<select name="service" required><option value="">Main service…</option>{opts_s}</select>
<select name="town" required><option value="">Home town…</option>{opts_t}</select>
<textarea name="details" rows="3" placeholder="What you do, in a sentence or two"></textarea>
<button type="submit">Submit listing</button></form>
<p class="note">Already listed and something's wrong? Use the same form and say "correction".</p>"""
    write("/get-listed/", page(f"Get Listed Free | {SITE}", "Add your North Florida service business to the Near Me Solutions directory — free basic listing, optional featured placement.", body, "/get-listed/"))
    write("/get-listed/thanks/", page(f"Thanks | {SITE}", "Listing request received.", '<div class="hero"><h1>Got it.</h1><p>We review every listing by hand and will email you when it\'s live, usually within a couple of days.</p><p><a href="/">← Back home</a></p></div>', "/get-listed/thanks/"))

    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{DOMAIN}{u}</loc></url>" for u in urls) + "</urlset>")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    (DIST / ".htaccess").write_text("ErrorDocument 404 /index.html\nOptions -Indexes\n")
    print(f"built {len(urls)} pages, {len(all_biz)} businesses")

if __name__ == "__main__":
    build()
