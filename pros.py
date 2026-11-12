"""Local Pros On Call section of nearmesolutions.pro (everything under /pros/).

Homeowners call one number, a phone agent screens the call, and it is transferred
to the partner company for that service and area. Driven by pros.json:

  "active":   ["pest-control/tampa", ...]   areas with a signed partner (shows the call button)
  "partners": [{"name", "service", "metro", "blurb", "website"}]   shown as featured cards

An area that is not in "active" is published as "open": no consumer call button,
and the page pitches the area to local companies instead.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
PHONE_E164 = "+18509035014"
PHONE_SHOWN = "(850) 903-5014"
ADDRESS = "1862 US Hwy 27, Perry, FL 32347"
EMAIL = "stump@nearmesolutions.pro"
PRICE = 35
FREE_CALLS = 5
SB_URL = "https://cadnjasqqzvhfzabpzfj.supabase.co"
SB_KEY = "sb_publishable_TYy0guRi-pogd-rong7l0w__4mZTUdN"

SERVICES = {
    "pest-control": {"name": "Pest Control", "pro": "exterminator", "trade": "pest control",
        "blurb": "Roaches, ants, termites, bed bugs, rodents and wildlife.",
        "needs": ["General pests", "Termites", "Bed bugs", "Rodents or wildlife"]},
    "emergency-plumber": {"name": "Emergency Plumber", "pro": "plumber", "trade": "plumbing",
        "blurb": "Leaks, burst pipes, drain and sewer backups, water heaters.",
        "needs": ["Leak or burst pipe", "Drain or sewer backup", "Water heater", "Other plumbing"]},
}
METROS = {
    "tampa":        {"name": "Tampa Bay", "st": "FL", "area": "Tampa, St. Petersburg, Clearwater, Brandon and Land O' Lakes"},
    "orlando":      {"name": "Orlando", "st": "FL", "area": "Orlando, Kissimmee, Winter Park and Longwood"},
    "jacksonville": {"name": "Jacksonville", "st": "FL", "area": "Jacksonville, Orange Park, Fruit Cove and St. Augustine"},
    "atlanta":      {"name": "Atlanta", "st": "GA", "area": "Atlanta, Marietta, Alpharetta, Smyrna and Duluth"},
    "charlotte":    {"name": "Charlotte", "st": "NC", "area": "Charlotte, Matthews, Mint Hill and Monroe"},
    "fort-myers":   {"name": "Fort Myers", "st": "FL", "area": "Fort Myers, Cape Coral, Lehigh Acres and Estero"},
    "sarasota":     {"name": "Sarasota", "st": "FL", "area": "Sarasota, Bradenton, Parrish and Venice"},
    "lakeland":     {"name": "Lakeland", "st": "FL", "area": "Lakeland, Winter Haven, Bartow and Plant City"},
    "daytona":      {"name": "Daytona Beach", "st": "FL", "area": "Daytona Beach, Port Orange, Ormond Beach and South Daytona"},
    "melbourne":    {"name": "Melbourne", "st": "FL", "area": "Melbourne, Palm Bay, Viera and Rockledge"},
    "ocala":        {"name": "Ocala", "st": "FL", "area": "Ocala, Belleview, Silver Springs and Dunnellon"},
    "gainesville":  {"name": "Gainesville", "st": "FL", "area": "Gainesville, Alachua, Newberry and High Springs"},
    "tallahassee":  {"name": "Tallahassee", "st": "FL", "area": "Tallahassee, Crawfordville, Quincy and Havana"},
    "pensacola":    {"name": "Pensacola", "st": "FL", "area": "Pensacola, Gulf Breeze, Pace and Milton"},
}

STYLE = """<style>
.pros-call{display:flex;align-items:center;justify-content:center;gap:10px;background:var(--acc2);color:#17201a;text-decoration:none;font-weight:800;font-size:22px;padding:18px 22px;border-radius:14px;max-width:520px;box-shadow:var(--sh)}
.pros-call svg{width:22px;height:22px}
.pros-steps{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));padding:0;margin:0;list-style:none;counter-reset:s}
.pros-steps li{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:18px;counter-increment:s}
.pros-steps li:before{content:counter(s);display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;background:var(--acc);color:#fff;font-weight:700;margin-bottom:8px}
.pros-steps b{display:block;font-size:17px}
.pros-open{display:inline-block;background:#fff7e3;border:1px solid #f0d58c;border-radius:999px;padding:3px 12px;font-size:13px;font-weight:700}
.pros-live{display:inline-block;background:#e6f4ea;border:1px solid #b9dcc4;color:#174f2b;border-radius:999px;padding:3px 12px;font-size:13px;font-weight:700}
.pros-small{font-size:13px;color:var(--mut);max-width:640px}
.pros-consent{display:flex;gap:10px;align-items:flex-start;font-size:13px;color:var(--mut)}
.pros-consent input{width:auto;margin-top:3px}
.pros-terms li{margin:0 0 8px}
</style>"""

DISCLOSURE = (
    '<p class="pros-small">Local Pros On Call is a free referral service run by Near Me Solutions. '
    "We are not a contractor and do not perform services ourselves. We connect you with an independent, "
    "licensed company that pays us a fee for the connection. That company is responsible for its own "
    "licensing, pricing and work. Calls may be recorded. "
    '<a href="/pros/privacy/">Privacy</a> · <a href="/pros/terms/">Terms</a></p>'
)


def load():
    f = ROOT / "pros.json"
    data = json.loads(f.read_text()) if f.exists() else {}
    return set(data.get("active", [])), data.get("partners", [])


def pages(page, esc, phone_svg):
    """Return [(path, html)] for the whole /pros/ section."""
    active, partners = load()
    out = []
    call_btn = f'<a class="pros-call" href="tel:{PHONE_E164}">{phone_svg}Call {PHONE_SHOWN}</a>'
    call_mcta = (f"tel:{PHONE_E164}", f"Call a local pro — {PHONE_SHOWN}")
    biz_mcta = ("/pros/partners/", f"Get {FREE_CALLS} free calls for your company")

    def add(path, title, desc, body, mcta):
        out.append((path, page(title, desc, STYLE + body, path, mcta=mcta)))

    # ---- hub -------------------------------------------------------------
    tiles = ""
    for s, S in SERVICES.items():
        for m, M in METROS.items():
            live = f"{s}/{m}" in active
            badge = '<span class="pros-live">Taking calls</span>' if live else '<span class="pros-open">Area open for a partner</span>'
            tiles += (f'<a class="tile" href="/pros/{s}/{m}/"><h3>{esc(S["name"])} in {esc(M["name"])}</h3>'
                      f'<p>{esc(M["area"])}</p><p style="margin-top:10px">{badge}</p></a>')
    hub_call = (f'{call_btn}<p class="pros-small" style="margin-top:10px">Answered 7 days a week.</p>'
                if active else
                '<p class="note">We are signing up partner companies now. An area starts taking calls as soon as it has one.</p>')
    body = f"""<div class="crumbs"><a href="/">Home</a> › Local Pros On Call</div>
<div class="hero"><h1>Local Pros On Call</h1><p>One number for urgent pest control and plumbing. We ask a few quick questions, then put you straight through to a licensed local company that covers your ZIP code. Free to call, no obligation.</p>{hub_call}</div>
<h2>How it works</h2>
<ol class="pros-steps"><li><b>You call</b>Tell us what is wrong and your ZIP code. It takes about a minute.</li><li><b>We connect you</b>Your call goes to one local company that covers your area, not a list of five.</li><li><b>They quote and schedule</b>You deal with the company directly. We never charge homeowners.</li></ol>
<h2>Service areas</h2><div class="grid">{tiles}</div>
<h2>Own a pest control or plumbing company?</h2>
<p class="note">We send screened, live phone calls from homeowners in your ZIP codes. ${PRICE} per qualified call, first {FREE_CALLS} free, no contract. <a href="/pros/partners/">See how the partner program works</a>.</p>
{DISCLOSURE}"""
    add("/pros/", "Local Pros On Call — Urgent Pest Control & Plumbing | Near Me Solutions",
        "Call one number and get connected to a licensed local pest control or plumbing company that covers your ZIP code.",
        body, call_mcta if active else biz_mcta)

    # ---- service x metro -------------------------------------------------
    for s, S in SERVICES.items():
        for m, M in METROS.items():
            key = f"{s}/{m}"
            place = f'{M["name"]}, {M["st"]}'
            crumbs = f'<div class="crumbs"><a href="/">Home</a> › <a href="/pros/">Local Pros On Call</a> › {esc(S["name"])} in {esc(M["name"])}</div>'
            others = "".join(f'<a href="/pros/{s}/{o}/">{esc(O["name"])}</a>' for o, O in METROS.items() if o != m)
            other_s = "".join(f'<a href="/pros/{o}/{m}/">{esc(O["name"])}</a>' for o, O in SERVICES.items() if o != s)
            foot = (f'<h2>{esc(S["name"])} in other areas</h2><div class="chips">{others}</div>'
                    f'<h2>Other services in {esc(M["name"])}</h2><div class="chips">{other_s}</div>{DISCLOSURE}')
            if key in active:
                cards = "".join(
                    f'<div class="card feat"><h3>{esc(p["name"])}</h3><div class="meta">{esc(S["name"])} · Serves {esc(M["name"])}</div><p>{esc(p.get("blurb", ""))}</p>'
                    + (f'<div class="btns"><a class="alt" href="{esc(p["website"])}" rel="nofollow noopener" target="_blank">Website</a></div>' if p.get("website") else "")
                    + "</div>"
                    for p in partners if p.get("service") == s and p.get("metro") == m)
                opts = "".join(f"<option>{esc(n)}</option>" for n in S["needs"])
                body = f"""{crumbs}
<div class="hero"><h1>{esc(S["name"])} in {esc(place)}</h1><p>Need {('an ' if S['pro'][0] in 'aeiou' else 'a ')}{esc(S["pro"])} in {esc(M["area"])}? Call now and we will put you through to a licensed local company. {esc(S["blurb"])}</p>{call_btn}<p class="pros-small" style="margin-top:10px">Free to call. No obligation.</p></div>
{cards}
<h2>Prefer a call back?</h2>
<form id="pros-lead"><select name="service" required><option value="">What do you need?</option>{opts}</select>
<input name="zip" inputmode="numeric" pattern="\\d{{5}}" placeholder="ZIP code" required><input name="first_name" placeholder="First name" required><input name="phone" type="tel" placeholder="Phone number" required>
<label class="pros-consent"><input type="checkbox" required><span id="pros-consent-text">By checking this box and clicking "Request a call," I give my express written consent to be contacted by Local Pros On Call and its partner service provider for my area at the number provided, including by autodialed or prerecorded calls and text messages, about my service request. Consent is not a condition of purchase. Message and data rates may apply. Calls may be recorded.</span></label>
<button type="submit">Request a call</button></form>
<p id="pros-thanks" class="note" hidden>Thanks. A local pro will call you shortly.</p>
<script>
document.getElementById("pros-lead").addEventListener("submit",async function(ev){{
  ev.preventDefault();var f=new FormData(ev.target),q=new URLSearchParams(location.search);
  var body={{first_name:f.get("first_name"),zip:f.get("zip"),service:f.get("service"),phone:f.get("phone"),
    consent_text:document.getElementById("pros-consent-text").innerText,consent_ts:new Date().toISOString(),user_agent:navigator.userAgent,
    utm_source:q.get("utm_source")||"nearmesolutions",utm_campaign:q.get("utm_campaign")||"{key}",gclid:q.get("gclid")}};
  var r=await fetch("{SB_URL}/rest/v1/leads",{{method:"POST",headers:{{"Content-Type":"application/json",apikey:"{SB_KEY}",Authorization:"Bearer {SB_KEY}",Prefer:"return=minimal"}},body:JSON.stringify(body)}});
  if(r.ok){{ev.target.hidden=true;document.getElementById("pros-thanks").hidden=false;}}
  else{{document.getElementById("pros-thanks").textContent="Something went wrong. Please call us instead.";document.getElementById("pros-thanks").hidden=false;}}
}});
</script>
{foot}"""
                add(f"/pros/{s}/{m}/", f"{S['name']} in {place} — Call a Local Pro | Near Me Solutions",
                    f"Urgent {S['trade']} help in {M['area']}. One call connects you to a licensed local company.", body, call_mcta)
            else:
                body = f"""{crumbs}
<div class="hero"><h1>{esc(S["name"])} in {esc(place)}</h1><p><span class="pros-open">Area open for a partner</span></p><p>Local Pros On Call is not taking {esc(S["trade"])} calls in {esc(M["name"])} yet. We turn an area on as soon as a licensed local company signs up to answer its calls.</p></div>
<div class="card feat"><h3>Run a {esc(S["trade"])} company in {esc(M["name"])}?</h3><div class="meta">Covers {esc(M["area"])}</div>
<p>Claim this area and we will send you screened, live calls from homeowners in your ZIP codes who need {('an ' if S['pro'][0] in 'aeiou' else 'a ')}{esc(S["pro"])} this week. ${PRICE} per qualified call, first {FREE_CALLS} free, no contract, and the calls are exclusive to you in your ZIPs.</p>
<div class="btns"><a href="/pros/partners/?service={s}&metro={m}">Claim {esc(M["name"])} — first {FREE_CALLS} calls free</a><a class="alt" href="/pros/partners/">How it works</a></div></div>
{foot}"""
                add(f"/pros/{s}/{m}/", f"{S['name']} in {place} — Area Open | Near Me Solutions",
                    f"Local Pros On Call is opening {S['trade']} call service in {M['area']}. Local companies can claim the area.", body, biz_mcta)

    # ---- partner program -------------------------------------------------
    opts_s = "".join(f'<option value="{s}">{esc(S["name"])}</option>' for s, S in SERVICES.items())
    opts_m = "".join(f'<option value="{m}">{esc(M["name"])}, {M["st"]}</option>' for m, M in METROS.items())
    body = f"""<div class="crumbs"><a href="/">Home</a> › <a href="/pros/">Local Pros On Call</a> › Partner program</div>
<div class="hero"><h1>Live calls from homeowners in your ZIP codes</h1><p>Local Pros On Call is launching in Tampa Bay, Orlando, Jacksonville, Atlanta and Charlotte. Our ads reach homeowners who need a pest control company or a plumber now. We screen every caller by phone and transfer the live call to your line. ${PRICE} per qualified call. First {FREE_CALLS} free. No contract.</p></div>
<ol class="pros-steps"><li><b>We screen the caller</b>Real homeowner or decision-maker, inside your ZIP codes, needs service within 7 days.</li><li><b>You get the live call</b>Transferred to the number you choose while the caller is still on the line.</li><li><b>You pay only for qualified calls</b>Billed weekly. If the recording shows a call did not qualify, you do not pay for it.</li></ol>
<h2>The terms, in plain language</h2>
<ul class="pros-terms"><li><b>${PRICE} per qualified call.</b> Your first {FREE_CALLS} qualified calls are free.</li><li><b>Qualified means all three:</b> homeowner or authorized decision-maker, inside your service area, needs service within 7 days.</li><li><b>Exclusive.</b> While you are active, calls from your ZIP codes go to you and nobody else.</li><li><b>No contract and no minimum.</b> Cancel any time by email.</li><li><b>Disputes.</b> Tell us within 48 hours and we review the recording. If it did not qualify, it is not billed.</li><li><b>Your customers stay yours.</b> We do not share a caller's details with any other company.</li></ul>
<h2>Claim your area</h2>
<form action="https://formsubmit.co/{EMAIL}" method="POST">
<input type="hidden" name="_subject" value="Local Pros On Call — partner sign-up"><input type="hidden" name="_captcha" value="false"><input type="hidden" name="_next" value="https://nearmesolutions.pro/pros/partners/thanks/">
<input name="business" placeholder="Company name" required><input name="contact" placeholder="Your name" required><input name="email" type="email" placeholder="Email" required>
<input name="transfer_number" type="tel" placeholder="Phone number to send calls to" required>
<select name="service" id="pp-service" required><option value="">Service…</option>{opts_s}</select>
<select name="metro" id="pp-metro" required><option value="">Area…</option>{opts_m}</select>
<textarea name="zips" rows="2" placeholder="ZIP codes you cover" required></textarea>
<input name="license" placeholder="State license number (optional)">
<button type="submit">Claim my area — first {FREE_CALLS} calls free</button></form>
<p class="pros-small" style="margin-top:12px">We confirm your start date by email once your area is live. Questions: <a href="mailto:{EMAIL}">{EMAIL}</a>. Local Pros On Call, {ADDRESS}.</p>
<script>(function(){{var q=new URLSearchParams(location.search),s=q.get("service"),m=q.get("metro");if(s)document.getElementById("pp-service").value=s;if(m)document.getElementById("pp-metro").value=m;}})();</script>"""
    add("/pros/partners/", "Partner Program — Live Homeowner Calls for Pest & Plumbing Companies | Near Me Solutions",
        f"Screened, live calls from homeowners in your ZIP codes. ${PRICE} per qualified call, first {FREE_CALLS} free, no contract.", body, biz_mcta)
    add("/pros/partners/thanks/", "Thanks | Local Pros On Call", "Partner sign-up received.",
        '<div class="hero"><h1>Got it.</h1><p>We review every sign-up by hand and will email you to confirm your ZIP codes and start date.</p><p><a href="/pros/">← Back to Local Pros On Call</a></p></div>', biz_mcta)

    # ---- legal -----------------------------------------------------------
    add("/pros/privacy/", "Privacy | Local Pros On Call", "How Local Pros On Call handles caller and form information.",
        f"""<div class="crumbs"><a href="/pros/">Local Pros On Call</a> › Privacy</div><div class="hero"><h1>Privacy</h1></div>
<p>When you call or request a call back, Local Pros On Call collects the service you need, your ZIP code, first name and phone number, along with your consent record, the time, and your browser details. Calls may be recorded.</p>
<p>We use this only to connect you with the partner company that covers your area, and we share it with that company alone. We do not sell it for any other purpose.</p>
<p>We keep consent records for five years. To have your information deleted, email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<p>Local Pros On Call is operated by Near Me Solutions, {ADDRESS}.</p>""", call_mcta if active else biz_mcta)
    add("/pros/terms/", "Terms | Local Pros On Call", "Terms of use for the Local Pros On Call referral service.",
        f"""<div class="crumbs"><a href="/pros/">Local Pros On Call</a> › Terms</div><div class="hero"><h1>Terms</h1></div>
<p>Local Pros On Call is a free referral service for homeowners, operated by Near Me Solutions. We are not a contractor, and we do not perform, supervise or guarantee any work.</p>
<p>We connect you with an independent company that pays us a referral fee. That company is solely responsible for its licensing, insurance, pricing, scheduling and workmanship. Check a company's license with your state before hiring.</p>
<p>For a gas smell, flooding near electrical hazards, or any other emergency that threatens safety, call 911 or your utility first.</p>
<p>The service is intended for U.S. residents. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>, {ADDRESS}.</p>""", call_mcta if active else biz_mcta)
    return out
