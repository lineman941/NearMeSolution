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
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500;700&display=swap');
:root{--bg:#f6f4ee;--ink:#17201a;--mut:#5a6457;--card:#fff;--line:#e4e1d6;--acc:#1f6b3a;--acc-d:#174f2b;--acc2:#f2a81d;--r:16px;--sh:0 1px 2px rgba(20,30,20,.06),0 8px 24px -12px rgba(20,30,20,.18)}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;font:16px/1.55 Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
a{color:var(--acc)}.wrap{max-width:1040px;margin:0 auto;padding:0 18px}
h1,h2,h3,.logo{font-family:"Barlow Condensed",Impact,"Arial Narrow",sans-serif;letter-spacing:.01em}
header{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}header .wrap{display:flex;align-items:center;justify-content:space-between;height:62px}
.logo{display:flex;align-items:center;gap:9px;font-weight:800;text-decoration:none;color:var(--ink);font-size:24px;text-transform:uppercase}.logo svg{width:30px;height:30px}.logo span{color:var(--acc)}
nav{display:flex;align-items:center;gap:4px}nav a{text-decoration:none;color:var(--mut);font-size:15px;font-weight:500;padding:8px 10px;border-radius:8px}nav a:hover{background:var(--bg);color:var(--ink)}nav a.cta{background:var(--acc2);color:#17201a;padding:9px 16px;border-radius:999px;font-weight:700;margin-left:6px}
.hero{padding:40px 0 26px}.hero h1{font-size:clamp(34px,6vw,58px);line-height:.98;margin:0 0 12px;text-transform:uppercase;font-weight:800}.hero p{font-size:18px;color:var(--mut);max-width:640px;margin:0 0 20px}
.hero.home{position:relative;color:#fff;margin:0 0 30px;padding:0}.hero.home .bg{position:absolute;inset:0;background:#1a2a1e url(/img/crew.jpg) center/cover;}.hero.home .bg:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,20,12,.35),rgba(10,20,12,.78))}
.hero.home .wrap{position:relative;padding-top:clamp(70px,14vw,130px);padding-bottom:clamp(40px,8vw,70px)}.hero.home h1{color:#fff;text-shadow:0 2px 14px rgba(0,0,0,.4)}.hero.home p{color:#e9eee6}
.hero.home .actions a{display:inline-block;margin:6px 10px 0 0;padding:14px 22px;border-radius:12px;font-weight:700;text-decoration:none;font-size:17px;background:var(--acc2);color:#17201a}.hero.home .actions a.ghost{background:rgba(255,255,255,.14);color:#fff;border:1px solid rgba(255,255,255,.45);backdrop-filter:blur(4px)}
.trust{display:flex;gap:18px 28px;flex-wrap:wrap;margin:22px 0 0;padding:0;list-style:none;font-size:14px;color:#dfe6dc}.trust li:before{content:"✓ ";color:var(--acc2);font-weight:700}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.tile{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;text-decoration:none;color:var(--ink);display:block;box-shadow:var(--sh);transition:transform .15s,border-color .15s}.tile:hover{border-color:var(--acc);transform:translateY(-2px)}
.tile h3{margin:0 0 6px;font-size:24px;text-transform:uppercase}.tile p{margin:0;color:var(--mut);font-size:14px}.tile .ic{width:36px;height:36px;margin:0 0 12px;color:var(--acc)}
h2{font-size:30px;margin:38px 0 14px;text-transform:uppercase}.chips a{display:inline-block;margin:0 8px 8px 0;padding:8px 14px;background:#fff;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--ink);font-size:14px;font-weight:500}.chips a:hover{border-color:var(--acc)}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:22px;margin:0 0 14px;box-shadow:var(--sh)}
.card.feat{border:2px solid var(--acc2);position:relative;background:linear-gradient(180deg,#fffbf0,#fff)}.card.feat:before{content:"★ Featured local pro";position:absolute;top:-12px;left:16px;background:var(--acc2);color:#17201a;font-size:12px;font-weight:700;padding:3px 11px;border-radius:999px;letter-spacing:.03em}
.card h3{margin:0 0 4px;font-size:26px}.card .meta{color:var(--mut);font-size:14px;margin:0 0 8px}.card p{margin:0 0 14px}
.btns{display:flex;flex-wrap:wrap;gap:8px}.btns a{display:inline-flex;align-items:center;gap:8px;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:700;font-size:16px;background:var(--acc);color:#fff;min-height:46px}.btns a:hover{background:var(--acc-d)}.btns a.alt{background:#fff;color:var(--acc);border:1px solid #cfd8cf;font-weight:600}
.btns a svg{width:18px;height:18px;flex:none}
.note{background:#fff7e3;border:1px solid #f0d58c;border-radius:var(--r);padding:14px 16px;font-size:15px}
form{display:grid;gap:10px;max-width:520px}input,select,textarea{font:inherit;padding:12px;border:1px solid var(--line);border-radius:10px;width:100%;background:#fff}button{font:inherit;font-weight:700;padding:14px;border:0;border-radius:10px;background:var(--acc);color:#fff;cursor:pointer;font-size:16px}
footer{margin-top:60px;padding:28px 0 90px;border-top:1px solid var(--line);color:var(--mut);font-size:14px}footer a{color:var(--mut)}
.crumbs{font-size:14px;color:var(--mut);margin:18px 0 0}.crumbs a{color:var(--mut)}
.mcta{display:none}
@media(max-width:640px){nav a:not(.cta){display:none}.hero{padding:30px 0 20px}.card{padding:18px}.btns a{flex:1 1 auto;justify-content:center}
.mcta{display:block;position:fixed;left:12px;right:12px;bottom:12px;z-index:20;background:var(--acc2);color:#17201a;text-align:center;padding:14px;border-radius:12px;font-weight:700;text-decoration:none;box-shadow:0 8px 24px rgba(0,0,0,.2)}}
"""

LOGO_SVG = '<svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M16 2C10 2 5.5 6.6 5.5 12.4 5.5 20 16 30 16 30s10.5-10 10.5-17.6C26.5 6.6 22 2 16 2z" fill="#1f6b3a"/><path d="M11.5 15.5l3.2-3.2a3.2 3.2 0 014.4-3.9l-2.1 2.1 1.5 1.5 2.1-2.1a3.2 3.2 0 01-3.9 4.4l-3.2 3.2-2-2z" fill="#f2a81d"/></svg>'
PHONE_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 006.6 6.6l2.2-2.2a1 1 0 011-.25c1.1.37 2.3.57 3.6.57a1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.25.2 2.45.57 3.57a1 1 0 01-.25 1L6.6 10.8z"/></svg>'
ICONS = {
 "stump-grinding": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="7" rx="8" ry="3"/><path d="M4 7v9c0 1.7 3.6 3 8 3s8-1.3 8-3V7"/><path d="M9 7.5c1 1 1 2 0 3M14 8c1 1 1 2 0 3"/></svg>',
 "tree-removal": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l5 7h-3l4 6h-5v7h-2v-7H6l4-6H7z"/></svg>',
 "mobile-mechanic": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 00-5.3 5.3L3 18l3 3 6.4-6.4a4 4 0 005.3-5.3l-2.5 2.5-2.1-.4-.4-2.1z"/></svg>',
 "handyman": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21l6-6M14 4l6 6-9 9-6-6zM14 4l3-3 6 6-3 3"/></svg>',
}

def esc(s): return html.escape(str(s), quote=True)

def page(title, desc, body, path, schema=None, mcta=("/get-listed/","List your business free")):
    url = DOMAIN + path
    mcta_href, mcta_text = mcta
    if not body.startswith('<div class="hero home">'): body = f'<main class="wrap">{body}</main>'
    ld = f'<script type="application/ld+json">{json.dumps(schema)}</script>' if schema else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="website"><meta property="og:image" content="{DOMAIN}/img/og.jpg"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/img/favicon.svg" type="image/svg+xml"><meta name="theme-color" content="#1f6b3a">
<link rel="stylesheet" href="/style.css">{ld}</head><body>
<header><div class="wrap"><a class="logo" href="/">{LOGO_SVG}Near<span>Me</span>Solutions</a><nav><a href="/stump-grinding/">Stumps</a><a href="/tree-removal/">Trees</a><a href="/mobile-mechanic/">Mechanic</a><a href="/handyman/">Handyman</a><a class="cta" href="/get-listed/">Get listed</a></nav></div></header>
{body}
<footer><div class="wrap">© {datetime.date.today().year} {SITE} · Perry, FL · <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> · <a href="/get-listed/">List your business</a><br><small>Listings are compiled from public sources. Own one of these businesses? <a href="/get-listed/">Claim or correct it</a>.</small></div></footer><a class="mcta" href="{mcta_href}">{mcta_text}</a>
</body></html>"""

def listing_card(b, town=None):
    feat = b.get("featured")
    meta = []
    if town: meta.append(f"Serves {TOWNS[town]['name']}")
    meta.append(", ".join(SERVICES[s]["name"] for s in b["services"] if s in SERVICES))
    btns = []
    if b.get("phone"): btns.append(f'<a href="tel:{esc(b["phone"].replace(" ","").replace("(","").replace(")","").replace("-",""))}">{PHONE_SVG}Call {esc(b["phone"])}</a>')
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
<div class="hero"><h1>{esc(S['name'])} in {esc(T['name'])},&nbsp;FL</h1><p>Local pros who {esc(S['verb'])} in {esc(T['name'])} and {esc(T['county'])}. {esc(S['blurb'])}</p></div>
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
    if (ROOT / "img").exists(): shutil.copytree(ROOT / "img", DIST / "img")
    urls = ["/"]

    def write(path, content):
        p = DIST / path.strip("/") / "index.html" if path != "/" else DIST / "index.html"
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content)
        if path not in urls: urls.append(path)

    # home
    tiles = "".join(f'<a class="tile" href="/{s}/">{ICONS[s]}<h3>{esc(v["name"])}</h3><p>{esc(v["blurb"])}</p></a>' for s, v in SERVICES.items())
    towns = "".join(f'<a href="/{"stump-grinding"}/{t}/">{esc(v["name"])}</a>' for t, v in TOWNS.items())
    body = f"""<div class="hero home"><div class="bg"></div><div class="wrap"><h1>Find a local pro<br>who shows up.</h1><p>Stump grinding, tree removal, mobile mechanics and handymen across Perry, Tallahassee and North Florida. Real businesses, real phone numbers, no middleman fees.</p>
<div class="actions"><a href="/stump-grinding/perry/">Browse Perry pros</a><a class="ghost" href="/get-listed/">List your business free</a></div>
<ul class="trust"><li>47 local businesses</li><li>5 towns, 5 counties</li><li>Free to use, free to list</li></ul></div></div>
<main class="wrap"><div class="grid">{tiles}</div>
<h2>Browse by town</h2><div class="chips">{towns}</div>
<h2>Featured local pro</h2>{listing_card(FEATURED)}
<p class="note">Run a service business in North Florida? <a href="/get-listed/">List it free</a>.</p></main>"""
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
            write(f"/{s}/{t}/", page(f"{S['name']} in {T['name']}, FL — {len(biz)} Local Pros | {SITE}", f"{S['name']} near {T['name']}, {T['county']}: {len(biz)} local businesses with phone numbers and websites. Free quotes.", service_town_body(s, t, biz), f"/{s}/{t}/", schema, mcta=("tel:8502953235","Call Need A Hand — (850) 295-3235")))

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
