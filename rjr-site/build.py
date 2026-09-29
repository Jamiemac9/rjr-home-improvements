#!/usr/bin/env python3
"""Build the RJR Home Improvements static site into ./site

    pip install pillow
    python3 build.py

Content lives in content.py. Styles in static/assets/site.css. Photos in /images.
Every internal URL is written relative, so pages work from any host, sub-folder or file://.
"""
import hashlib
import json
import os
import re
import shutil
from html import escape as e
from pathlib import Path
from urllib.parse import quote

from content import (SITE, ABOUT, TRADES, REVIEWS, QUOTES, IMG, PROJECTS, FEATURES, FEATURE_NOTES,
                     SERVICES, GROUPS, AREAS)
from tools.optimise_images import optimise

ROOT = Path(__file__).parent
OUT = ROOT / "site"
BASE = SITE["url"].rstrip("/")
BIZ = BASE + "/#business"
# DEMO=1 (set in netlify.toml / Cloudflare env) hides every page from search engines. Remove it at launch.
DEMO = os.environ.get("DEMO", "").lower() in ("1", "true", "yes")

SVC = {s["slug"]: s for s in SERVICES + GROUPS}
MATRIX = [s for s in SERVICES if s.get("matrix")]
AREA = {a["slug"]: a for a in AREAS}
ORDER = ["edgbaston", "kings-heath", "moseley", "solihull", "shirley", "hall-green", "harborne", "selly-oak", "stirchley", "northfield"]
AREAS_O = [AREA[s] for s in ORDER]
REV = {r["id"]: r for r in REVIEWS}
PAGES = []
MANIFEST = {}
VERSION = ""
TEL = "tel:" + SITE["phone_intl"]
FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,800..900"
         "&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap")
PROJECT_ROTA = ["chimney", "fascias", "velux", "reroof"]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def fill(s, area="Birmingham", council="Birmingham City Council or Solihull Metropolitan Borough Council"):
    return s.replace("{area}", area).replace("{council}", council)


def pcs(a):
    return ", ".join(a["pcs"])


def ext(url, text, cls=""):
    c = ' class="%s"' % cls if cls else ""
    return '<a%s href="%s" rel="noopener">%s</a>' % (c, e(url), text)


def wa(msg):
    return "https://wa.me/%s?text=%s" % (SITE["whatsapp"], quote(msg))


def quote_btn(label="Get a quote", cls="btn btn--neon", urgency=""):
    """Jumps to the on-page quote form (which then opens WhatsApp pre-filled)."""
    u = ' data-set-urgency="%s"' % urgency if urgency else ""
    return '<a class="%s" href="#quote"%s>%s</a>' % (cls, u, label)


URGENCY = [("emergency", "Emergency: water getting in, or something could fall"), ("urgent", "Urgent: this week"),
           ("soon", "Soon: within a month"), ("quote", "Planning or quote only")]
PROPERTY = ["Terraced", "Semi-detached", "Detached", "Bungalow", "Flat or maisonette", "Commercial", "Other"]
REPLY = ["WhatsApp message", "Phone call"]
WHEN = ["Any time", "Morning", "Afternoon", "Evening"]


def _options(pairs, selected="", placeholder=None):
    out = ['<option value="" disabled%s>%s</option>' % ("" if selected else " selected", placeholder)] if placeholder else []
    for val, label in pairs:
        out.append('<option value="%s"%s>%s</option>' % (e(label), " selected" if val == selected else "", e(label)))
    return "".join(out)


def quote_form(ctx=None, path="/"):
    """Quote form: nothing is submitted to a server. quote.js turns the answers into a
    WhatsApp message on the visitor's own device. Inputs have no name attributes, so a
    no-JavaScript submit sends no personal data anywhere."""
    ctx = ctx or {}
    areas = [(a["slug"], "%s (%s)" % (a["name"], pcs(a))) for a in AREAS_O] + [("other", "Elsewhere in Birmingham / West Midlands")]
    services = [(x["slug"], x["name"]) for x in SERVICES + GROUPS] + [("not-sure", "Not sure / something else")]
    f = lambda label, fid, control, hint="": '<div class="field"><label for="%s">%s</label>%s%s</div>' % (fid, label, control, '<p class="hint">%s</p>' % hint if hint else "")
    fields = [
        f("Your name", "q-name", '<input id="q-name" type="text" autocomplete="name" required maxlength="80">'),
        f("Postcode", "q-postcode", '<input id="q-postcode" type="text" autocomplete="postal-code" required maxlength="8" '
          'pattern="^[A-Za-z]{1,2}[0-9][0-9A-Za-z]?( ?[0-9][A-Za-z]{2})?$" title="A UK postcode, e.g. B13 9AB (or just B13)">'),
        f("What do you need?", "q-service", '<select id="q-service" required>%s</select>' % _options(services, ctx.get("service", ""), "Choose a service")),
        f("How urgent is it?", "q-urgency", '<select id="q-urgency" required>%s</select>' % _options(URGENCY, ctx.get("urgency", ""), "Choose one")),
        f("Area", "q-area", '<select id="q-area" required>%s</select>' % _options(areas, ctx.get("area", ""), "Choose your area")),
        f("Property type", "q-property", '<select id="q-property">%s</select>' % _options([(x, x) for x in PROPERTY], "", "Choose (optional)")),
        f("How should we reply?", "q-reply", '<select id="q-reply">%s</select>' % _options([(x, x) for x in REPLY], "WhatsApp message")),
        f("Best time", "q-when", '<select id="q-when">%s</select>' % _options([(x, x) for x in WHEN], "Any time")),
    ]
    details = f("What's happening?", "q-details", '<textarea id="q-details" rows="4" required maxlength="800" '
                'placeholder="e.g. Water coming through the bedroom ceiling when it rains. Tiles missing at the back."></textarea>')
    return """<form class="qform" id="quote" action="#quote" data-wa="%s" data-page="%s" novalidate>
  <div class="qgrid">%s</div>
  %s
  <label class="check"><input id="q-photos" type="checkbox" checked> I&rsquo;ll attach photos in WhatsApp before sending</label>
  <p class="hint">Nothing is sent or stored by this website. Pressing the button opens WhatsApp with your answers written in; you check it, add photos and press send.</p>
  <div class="cta-row"><button class="btn" type="submit">Continue to WhatsApp</button>%s</div>
  <p class="qstatus" role="status" aria-live="polite"></p>
  <noscript><p class="hint">This form needs JavaScript. You can <a href="https://wa.me/%s">message us on WhatsApp</a> directly or call %s.</p></noscript>
</form>""" % (SITE["whatsapp"], e(path), "".join(fields), details, call_link("Or call " + SITE["phone"]), SITE["whatsapp"], SITE["phone"])


def call_link(label=None):
    return '<a class="textlink" href="%s">%s</a>' % (TEL, label or "Call " + SITE["phone"])


def asset(name):
    return "/assets/img/" + name


def img(key, sizes="(min-width: 64rem) 50vw, 100vw", cls="", lazy=True, alt=None):
    m = MANIFEST[key]
    src_set = ", ".join("%s %dw" % (asset("%s-%d.webp" % (m["stem"], t)), w) for t, w, h in m["sizes"])
    t, w, h = m["sizes"][-1]
    a = IMG[key][1] if alt is None else alt
    pos = IMG[key][2]
    load = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    c = ' class="%s"' % cls if cls else ""
    return ('<img%s src="%s" srcset="%s" sizes="%s" width="%d" height="%d" alt="%s" style="object-position:%s"%s decoding="async">'
            % (c, asset("%s-%d.webp" % (m["stem"], t)), src_set, sizes, w, h, e(a), pos, load))


def thumb(key):
    return '<img class="th" src="%s" width="320" height="320" alt="" loading="lazy" decoding="async">' % asset(MANIFEST[key]["stem"] + "-sq.webp")


def hero_bg(key):
    return ('<div class="hero-bg" aria-hidden="true"><img src="%s" width="960" height="720" alt="" fetchpriority="high" style="object-position:%s"></div>'
            % (asset(MANIFEST[key]["stem"] + "-blur.webp"), IMG[key][2]))


def svc_title(s):
    return e(s["name"]) + ('<span class="tag">Urgent</span>' if s.get("emergency") else "")


def svc_hero(s):
    return s.get("hero", "chim_a")


# --------------------------------------------------------------------------
# structured data
# --------------------------------------------------------------------------
def business_node():
    node = {
        "@type": ["RoofingContractor", "GeneralContractor"], "@id": BIZ,
        "name": SITE["name"], "legalName": SITE["legal_name"], "url": BASE + "/",
        "telephone": SITE["phone_intl"], "description": " ".join(ABOUT),
        "image": BASE + asset(MANIFEST["chim_a"]["stem"] + "-og.jpg"), "hasMap": SITE["gbp"],
        "knowsAbout": [s["name"] for s in SERVICES] + sorted({t for ts in TRADES.values() for t in ts}),
        "areaServed": [{"@type": "City", "name": "Birmingham"}, {"@type": "AdministrativeArea", "name": "West Midlands"}]
        + [{"@type": "Place", "name": "%s (%s)" % (a["name"], pcs(a))} for a in AREAS_O],
        "contactPoint": {"@type": "ContactPoint", "telephone": SITE["phone_intl"], "contactType": "customer service",
                         "areaServed": "GB", "availableLanguage": "en-GB"},
        "sameAs": [SITE["gbp"], SITE["rated_people"].split("#")[0]],
    }
    if SITE["email"]:
        node["email"] = SITE["email"]
    if SITE["company_number"]:
        node["identifier"] = {"@type": "PropertyValue", "propertyID": "Companies House company number", "value": SITE["company_number"]}
    return node


def crumbs_node(url, crumbs):
    return {"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + p} for i, (n, p) in enumerate(crumbs)]}


def faq_node(url, faqs):
    return {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def service_node(url, name, stype, desc, area=None):
    served = ({"@type": "Place", "name": area["name"], "address": {"@type": "PostalAddress", "addressLocality": area["name"],
               "postalCode": area["pcs"][0], "addressRegion": "West Midlands", "addressCountry": "GB"}}
              if area else [{"@type": "City", "name": "Birmingham"}] + [{"@type": "Place", "name": a["name"]} for a in AREAS_O])
    return {"@type": "Service", "@id": url + "#service", "name": name, "serviceType": stype, "provider": {"@id": BIZ},
            "areaServed": served, "description": desc}


# --------------------------------------------------------------------------
# chrome
# --------------------------------------------------------------------------
NAV = [("emergency", "Emergency", "/services/emergency-roof-repairs/"), ("services", "Services", "/services/"),
       ("areas", "Areas", "/areas/"), ("work", "Before &amp; after", "/our-work/"), ("reviews", "Reviews", "/reviews/"),
       ("about", "About", "/about/"), ("contact", "Contact", "/contact/")]


def header(key, msg):
    items = []
    for k, t, u in NAV:
        cls = ' class="em"' if k == "emergency" else ""
        cur = ' aria-current="page"' if k == key else ""
        items.append('<li><a href="%s"%s%s>%s</a></li>' % (u, cls, cur, t))
    return """<a class="skip" href="#main">Skip to content</a>
<div class="mast" data-mast>
<div class="topbar"><div class="wrap">
  <p><span class="dot" aria-hidden="true"></span>Leak or storm damage? <a href="#quote" data-set-urgency="emergency">Tell us here</a></p>
  <p><a href="%s">%s</a></p>
</div></div>
<header class="site-head"><div class="wrap">
  <a class="brand" href="/">RJR Home Improvements<small>Emergency roofing &middot; Brickwork &middot; Building &middot; Birmingham</small></a>
  <button type="button" class="nav-toggle" aria-expanded="false" aria-controls="site-nav"><span class="when-closed">Menu</span><span class="when-open">Close</span></button>
  <nav class="nav" id="site-nav" aria-label="Main"><ul>%s</ul></nav>
  <div class="head-cta">%s</div>
</div></header>
</div>""" % (TEL, SITE["phone"], "".join(items), quote_btn())


def crumbs_html(crumbs):
    lis = []
    for i, (n, p) in enumerate(crumbs):
        lis.append('<li aria-current="page">%s</li>' % e(n) if i == len(crumbs) - 1 else '<li><a href="%s">%s</a></li>' % (p, e(n)))
    return '<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap"><ol>%s</ol></div></nav>' % "".join(lis)


def cta_band(msg, headline, form=None, path="/"):
    return """<section class="cta" aria-labelledby="cta-h"><div class="wrap">
  <div class="flow cta-intro">
    <h2 id="cta-h">%s</h2>
    <p>Fill this in and it opens WhatsApp with everything written for you. Add your photos, press send, and we&rsquo;ll come back to you.</p>
    <a class="num" href="%s">%s</a>
    <p class="hint">Prefer to type it yourself? <a href="%s" rel="noopener">Open WhatsApp directly</a>.</p>
  </div>
  %s
</div></section>""" % (e(headline), TEL, SITE["phone"], e(wa(msg)), quote_form(form, path))


def footer():
    roof = "".join('<li><a href="/services/%s/">%s</a></li>' % (s["slug"], e(s["name"])) for s in SERVICES)
    other = "".join('<li><a href="/services/%s/">%s</a></li>' % (g["slug"], e(g["name"])) for g in GROUPS)
    areas = "".join('<li><a href="/areas/%s/">%s &middot; %s</a></li>' % (a["slug"], e(a["name"]), pcs(a)) for a in AREAS_O)
    reg = []
    if SITE["company_number"]:
        reg.append("Company no. %s" % e(SITE["company_number"]))
    reg_line = (" &middot; " + " &middot; ".join(reg)) if reg else ""
    email = '<li><a href="mailto:%s">%s</a></li>' % (e(SITE["email"]), e(SITE["email"])) if SITE["email"] else ""
    return """<footer class="site-foot"><div class="wrap">
  <div class="foot-cols">
    <div><h2>Roofing</h2><ul>%s</ul></div>
    <div><h2>More trades</h2><ul>%s</ul><h2 style="padding-top:var(--s-1)">Company</h2><ul>
      <li><a href="/about/">About RJR</a></li><li><a href="/our-work/">Before &amp; after</a></li><li><a href="/reviews/">Reviews</a></li></ul></div>
    <div><h2>Areas</h2><ul><li><a href="/areas/">All areas</a></li>%s</ul></div>
    <div><h2>Contact</h2><ul>
      <li><a href="/contact/">Get a quote</a></li>
      <li><a href="%s" rel="noopener">WhatsApp %s</a></li><li><a href="%s">Call %s</a></li>%s
      <li>%s</li><li>%s</li></ul>
      <h2 style="padding-top:var(--s-1)">Legal</h2><ul>
      <li><a href="/privacy-policy/">Privacy policy</a></li><li><a href="/cookie-policy/">Cookie policy</a></li><li><a href="/sitemap/">Sitemap</a></li></ul></div>
  </div>
  <p class="foot-mark" aria-hidden="true">RJR</p>
  <div class="foot-base">
    <p>&copy; 2026 %s%s</p>
    <p><button type="button" data-consent-open>Cookie settings</button></p>
    <p class="credit">Website by <a href="%s" rel="noopener">%s</a></p>
  </div>
</div></footer>""" % (roof, other, areas, e(wa("Hi RJR, I need help with my roof. Postcode: ")), SITE["phone"], TEL, SITE["phone"], email,
                      ext(SITE["gbp"], "Google Business Profile"), ext(SITE["rated_people"], "Rated People profile"),
                      e(SITE["legal_name"]), reg_line, e(SITE["credit_url"]), e(SITE["credit_name"]))


def consent_html():
    return """<div class="consent" id="consent" role="region" aria-label="Cookie consent" hidden><div class="wrap">
  <p>We don&rsquo;t use tracking cookies unless you allow them. With your permission we&rsquo;d use anonymous analytics to see which pages help people. <a href="/cookie-policy/">Cookie policy</a></p>
  <div class="row"><button type="button" class="btn" data-choice="accept">Accept analytics</button><button type="button" class="btn" data-choice="reject">Reject</button></div>
</div></div>"""


def mbar(msg):
    return '<nav class="mbar" aria-label="Quick contact"><a class="wa" href="#quote">Get a quote</a><a class="call" href="%s">Call</a></nav>' % TEL


def page(path, title, desc, body, key="", crumbs=None, schema=None, og="chim_a", msg=None, cta=None, preload=None, noindex=False, form=None):
    msg = msg or "Hi RJR, I need help with my roof. Postcode: "
    url = BASE + path
    graph = [business_node(),
             {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": SITE["name"], "publisher": {"@id": BIZ}, "inLanguage": "en-GB"},
             dict({"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": title, "description": desc,
                   "isPartOf": {"@id": BASE + "/#website"}, "about": {"@id": BIZ}, "inLanguage": "en-GB", "dateModified": SITE["lastmod"],
                   "primaryImageOfPage": BASE + asset(MANIFEST[og]["stem"] + "-og.jpg"),
                   "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".answer", "h1"]}},
                  **({"breadcrumb": {"@id": url + "#breadcrumb"}} if crumbs else {}))]
    if crumbs:
        graph.append(crumbs_node(url, crumbs))
    graph += schema or []
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pre = '<link rel="preload" as="image" href="%s" fetchpriority="high">\n' % asset(MANIFEST[preload]["stem"] + "-blur.webp") if preload else ""
    analytics = ""
    if SITE.get("analytics_html"):
        analytics = re.sub(r"<script", '<script type="text/plain" data-consent="analytics"', SITE["analytics_html"])
    html = """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(url)s">
<meta name="robots" content="%(robots)s">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_GB">
<meta property="og:site_name" content="%(site)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(url)s">
<meta property="og:image" content="%(ogimg)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="GB-BIR">
<meta name="geo.placename" content="Birmingham">
<meta name="theme-color" content="#0d0d0c">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
%(pre)s<link rel="stylesheet" href="/assets/site.css?v=%(v)s">
<noscript><style>@media (max-width:63.99rem){.nav{display:block !important}.nav-toggle{display:none !important}}</style></noscript>
<link rel="preload" as="style" href="%(fonts)s" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="%(fonts)s"></noscript>
<script type="application/ld+json">%(ld)s</script>
%(analytics)s
</head>
<body>
%(header)s
%(crumbs)s
<main id="main">
%(body)s
%(cta)s
</main>
%(footer)s
%(mbar)s
%(consent)s
<script src="/assets/consent.js?v=%(v)s" defer></script>
<script src="/assets/quote.js?v=%(v)s" defer></script>
</body>
</html>
""" % {"title": e(title), "desc": e(desc), "url": url, "robots": "noindex,nofollow" if DEMO else ("noindex,follow" if noindex else "index,follow,max-image-preview:large,max-snippet:-1"),
       "site": e(SITE["name"]), "ogimg": BASE + asset(MANIFEST[og]["stem"] + "-og.jpg"), "pre": pre, "v": VERSION, "fonts": FONTS,
       "ld": ld, "analytics": analytics, "header": header(key, msg), "crumbs": crumbs_html(crumbs) if crumbs else "", "body": body,
       "cta": cta_band(msg, cta or "Tell us what\u2019s wrong with the roof.", form, path), "footer": footer(), "mbar": mbar(msg), "consent": consent_html()}
    if not path.endswith(".html"):
        html = relativise(html, path)
    f = OUT / path.lstrip("/") / "index.html" if path.endswith("/") else OUT / path.lstrip("/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html, encoding="utf-8")
    if not noindex:
        PAGES.append((path, "core" if not path.startswith(("/areas/", "/services/")) else path.split("/")[1]))


def relativise(html, path):
    """Rewrite root-relative href/src/srcset URLs to relative ones for this page's depth."""
    depth = 0 if not path.endswith("/") else path.strip("/").count("/") + (1 if path.strip("/") else 0)
    prefix = "../" * depth
    html = re.sub(r'(href|src)="/(?!/)', lambda m: '%s="%s' % (m.group(1), prefix), html)
    html = re.sub(r'(srcset="[^"]*")', lambda m: m.group(1).replace("/assets/", prefix + "assets/"), html)
    return html.replace('href=""', 'href="./"')


# --------------------------------------------------------------------------
# components
# --------------------------------------------------------------------------
def band(idx, title, inner, hid, cls="", colour="var(--orange)"):
    return """<section class="band %s" id="%s" aria-labelledby="%s-h"><div class="wrap grid">
  <div class="col-idx idx"><p>%s</p><span class="sw" style="--c:%s"></span></div>
  <div class="col-main flow-2"><h2 id="%s-h">%s</h2>%s</div>
</div></section>""" % (cls, hid, hid, idx, colour, hid, title, inner)


def toc(items):
    return '<nav class="toc" aria-label="On this page"><div class="wrap"><ol>%s</ol></div></nav>' % "".join(
        '<li><a href="#%s">%s</a></li>' % (i, e(t)) for i, t in items)


def kv(rows):
    return '<dl class="kv">%s</dl>' % "".join("<dt>%s</dt><dd>%s</dd>" % r for r in rows)


def ruled(items):
    return '<ul class="ruled">%s</ul>' % "".join("<li>%s</li>" % e(i) for i in items)


def defs(pairs):
    return '<dl class="defs">%s</dl>' % "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), e(b)) for a, b in pairs)


def steps(pairs):
    return '<ol class="steps">%s</ol>' % "".join("<li><div><b>%s</b><p>%s</p></div></li>" % (e(a), e(b)) for a, b in pairs)


def spec(rows, head=("Option", "Suits", "What to know")):
    th = "".join('<th scope="col">%s</th>' % h for h in head)
    tr = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % e(c) for c in r) for r in rows)
    return '<table class="spec"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (th, tr)


def callout(label, text):
    return '<div class="callout"><p class="label"><span>%s</span></p><p>%s</p></div>' % (label, e(text))


def qa_list(pairs):
    return '<div class="qa">%s</div>' % "".join("<div><h3>%s</h3><p>%s</p></div>" % (e(q), e(a)) for q, a in pairs)


def faq_html(faqs, title="Questions, answered.", idx="FAQ", cls="band--alt"):
    if not faqs:
        return ""
    rows = "".join('<details><summary>%s</summary><div class="a"><p>%s</p></div></details>' % (e(q), e(a)) for q, a in faqs)
    return band(idx, title, '<div class="faq">%s</div>' % rows, "faq", cls, "var(--neon)")


def pull(key):
    text, rid = QUOTES[key]
    r = REV[rid]
    return ('<figure class="pull"><blockquote><p>%s</p></blockquote><figcaption class="cite">%s, %s &middot; Verified &middot; %s &middot; %s</figcaption></figure>'
            % (e(text), e(r["name"]), r["pc"], r["disp"], ext(SITE["rated_people"], "Rated People")))


def figure(kind, key, cap, n):
    cls = {"After": "after", "Completed": "after", "During": "during"}.get(kind, "")
    sizes = {1: "(min-width: 64rem) 40vw, 100vw", 2: "(min-width: 64rem) 32vw, 50vw"}.get(n, "(min-width: 64rem) 21vw, 50vw")
    return '<figure><div class="frame">%s<span class="tag %s">%s</span></div><figcaption>%s</figcaption></figure>' % (
        img(key, sizes), cls, kind, e(cap))


def project_html(key, n=None):
    p = PROJECTS[key]
    s = SVC.get(p["service"])
    more = '<a class="textlink" href="/services/%s/">%s &rarr;</a>' % (s["slug"], e(s["name"])) if s else ""
    kinds = [k for k, _, _ in p["seq"]]
    seq = ("%s &middot; %d views" % (kinds[0], len(kinds))) if len(set(kinds)) == 1 and len(kinds) > 1 else " &rarr; ".join(kinds)
    num = "<span>Job %02d</span>" % n if n else ""
    figs = "".join(figure(k, i, c, len(kinds)) for k, i, c in p["seq"])
    return """<div class="ba%s">
  <div class="ba-head"><p class="label">%s<span>%s</span></p><h3>%s</h3><p>%s</p>%s</div>
  <div class="ba-row" style="--n:%d;--ar:%s">%s</div>
</div>""" % (" ba--solo" if len(kinds) == 1 else "", num, seq, e(p["title"]), e(p["intro"]), more, len(kinds), p["ratio"], figs)


def review_html(r, first=False):
    body = '<blockquote><p>%s</p></blockquote>' % e(r["text"]) if r["text"] else "<p>Verified rating, left without a written comment.</p>"
    return """<article class="review%s">
  <div class="flow-h"><p class="pc">%s</p><p class="meta"><span>%s</span><span>Verified</span><time datetime="%s">%s</time></p></div>
  <div class="flow-h">%s<p class="meta"><span>via Rated People</span></p></div>
</article>""" % (" review--first" if first else "", r["pc"], e(r["name"]), r["date"], r["disp"], body)


def score_html():
    return """<div class="score">
  <p class="big">%s</p>
  <p><strong>%d ratings on Rated People.</strong> The most recent are below, word for word. %s</p>
  <div class="g"><p><strong>On Google?</strong> Read or leave a review on our Business Profile.</p>%s</div>
</div>""" % (SITE["rating_label"], SITE["rating_count"], ext(SITE["rated_people"], "See them all &rarr;", "textlink"), ext(SITE["gbp"], "Google reviews", "btn"))


def index_list(rows, sm=False, thumbs=None):
    lis = []
    for i, (t, d, u) in enumerate(rows):
        th = thumbs[i] if thumbs else ""
        dd = '<span class="d">%s</span>' % e(d) if d else ""
        lis.append('<li><a href="%s">%s<span class="t">%s</span>%s</a></li>' % (u, th, t, dd))
    cls = "index-list" + (" index-list--sm" if sm else "") + (" index-list--thumbs" if thumbs else "")
    return '<ol class="%s">%s</ol>' % (cls, "".join(lis))


def areas_list(rows):
    return '<div class="areas">%s</div>' % "".join('<a href="%s"><span class="n">%s</span><span class="p">%s</span></a>' % (u, e(n), p) for n, p, u in rows)


def page_hero(bg, labels, h1, answer_paras, facts, msg, buttons=True):
    spans = "".join("<span>%s</span>" % s for s in labels)
    ans = "".join("<p>%s</p>" % p for p in answer_paras)
    cta = '<div class="cta-row">%s%s</div>' % (quote_btn(), call_link()) if buttons else ""
    panel = '<div class="panel"><p class="label"><span>Key facts</span></p>%s</div>' % kv(facts) if facts else "<div></div>"
    return """<section class="hero hero--page">%s<div class="wrap">
  <p class="label">%s</p>
  <h1>%s</h1>
  <div class="hero-foot"><div class="flow"><div class="answer">%s</div>%s</div>%s</div>
</div></section>""" % (hero_bg(bg) if bg else "", spans, h1, ans, cta, panel)


def base_facts():
    return [("Business", "Family run"), ("Experience", "%d years combined" % SITE["experience_years"]),
            ("Rating", "%s &middot; %d ratings" % (SITE["rating_label"], SITE["rating_count"])),
            ("Reviews", "%s &middot; %s" % (ext(SITE["gbp"], "Google"), ext(SITE["rated_people"], "Rated People"))),
            ("WhatsApp", '<a href="%s" rel="noopener">%s</a>' % (e(wa("Hi RJR, I need help with my roof. Postcode: ")), SITE["phone"]))]


def ticker():
    words = ["Emergency roof repairs", "Storm damage", "Roof leaks", "Chimneys", "Flat roofs", "Guttering", "Birmingham &amp; Solihull"]
    line = "".join("<span>%s</span><span>&#9632;</span>" % w for w in words)
    return '<div class="ticker" aria-hidden="true"><div class="ticker-track"><p>%s</p><p>%s</p></div></div>' % (line, line)


def emergency_block(area=None, idx="Urgent", full=True):
    where = " in " + e(area) if area else ""
    s = SVC["emergency-roof-repairs"]
    urgent = '<ul class="urgent">%s</ul>' % "".join("<li>%s</li>" % e(x) for x in s["signs"])
    wait = [("Contain the water.", "Bucket under the drip, furniture and valuables moved. If water is near light fittings or sockets, switch that circuit off at the consumer unit."),
            ("Keep clear.", "Stay out from under a bulging ceiling and away from anywhere a loose chimney or tiles could fall. Don't go up on the roof. Immediate danger: call 999."),
            ("Photograph it.", "The ceiling, the roof from the ground, anything that has fallen. It helps us, and it helps an insurance claim."),
            ("WhatsApp us.", "Send the photos with your postcode and we'll come back to you about getting there and what it needs.")]
    return (band(idx, "Is it urgent%s?" % where,
                 '<p class="lede">These need looking at quickly. Anything else can wait for a normal quote.</p>%s<div class="cta-row">%s%s</div>'
                 % (urgent, quote_btn("Report an emergency", "btn", "emergency"), call_link()),
                 "urgent", "band--neon", "var(--ink)")
            + ("" if not full else band("While you wait", "What to do right now.", steps(wait) + pull("fast"), "wait", "band--ink", "var(--neon)")))


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------
def build_home():
    faqs = [
        ("Do you do emergency roof repairs in Birmingham?", "Yes. RJR Home Improvements repairs roof leaks, storm damage, slipped and missing tiles, damaged chimneys and failed flashing across Birmingham and the West Midlands. WhatsApp a photo and your postcode to %s." % SITE["phone"]),
        ("What should I do if my roof is leaking right now?", SVC["emergency-roof-repairs"]["faqs"][0][1]),
        ("Which areas do you cover?", "Birmingham and the West Midlands, including Edgbaston, Kings Heath, Moseley, Solihull, Shirley, Hall Green, Harborne, Selly Oak, Stirchley and Northfield. Recent reviews come from B17, B30, B31, B90 and WV4."),
        ("Should I repair my roof or replace it?", SVC["roof-repairs"]["repair_or_replace"]),
        ("Is it a leak or condensation?", SVC["roof-leaks"]["leak_vs_condensation"]),
        ("Do you take on small jobs?", "Yes, from odd jobs as small as garden and gutter clearances to full refurbishments and replacements."),
        ("Where can I read reviews?", "On Google, through the RJR Business Profile, and on Rated People, where RJR is rated “Excellent” from %d ratings." % SITE["rating_count"]),
    ]
    hero = """<section class="hero">%s<div class="wrap">
  <p class="label"><span>Emergency roofers</span><span>Birmingham &amp; West Midlands</span><span>Family run</span></p>
  <h1>Roof leak? Storm damage? <span class="hl">Emergency roof repairs</span> in Birmingham.</h1>
  <div class="hero-foot">
    <div class="flow"><p class="lede">WhatsApp a photo of the problem and your postcode. A family-run team with 45 years&rsquo; combined experience, from leaks and storm damage to full re-roofs.</p>
      <div class="cta-row">%s%s%s</div></div>
  </div>
</div></section>""" % (hero_bg(SITE["home_hero"]),
                       quote_btn(), call_link(), ext(SITE["gbp"], "Google reviews &rarr;", "textlink"))
    rows = [(svc_title(s), s["summary"], "/services/%s/" % s["slug"]) for s in SERVICES]
    services = band("01 &middot; Services", "Roofing first. Then everything else.",
                    index_list(rows, thumbs=[thumb(svc_hero(s)) for s in SERVICES]) + "<h3>Brickwork, stonework &amp; building</h3>"
                    + index_list([(e(g["name"]), g["summary"], "/services/%s/" % g["slug"]) for g in GROUPS], thumbs=[thumb(g["hero"]) for g in GROUPS]), "services")
    work = band("02 &middot; Before &amp; after", "Same roof. Before, then after.",
                project_html("chimney", 1) + project_html("fascias", 2) + project_html("velux", 3)
                + '<p><a class="btn" href="/our-work/">All before &amp; after photos</a></p>', "work", "band--alt")
    about = """<section class="band band--orange" id="about" aria-labelledby="about-h"><div class="wrap grid">
  <div class="col-idx idx"><p>03 &middot; About</p><span class="sw" style="--c:var(--ink)"></span></div>
  <div class="col-main flow-2">
    <div class="stat"><p class="stat-n">45</p><p class="label"><span>Years&rsquo; combined experience in the trade</span></p></div>
    <h2 id="about-h">Family run. Top to bottom of your home.</h2>
    <div class="flow">%s</div>
    <p><a class="btn" href="/about/">About RJR</a></p>
  </div>
</div></section>""" % "".join("<p>%s</p>" % e(p) for p in ABOUT)
    arts = "".join(review_html(r, i == 0) for i, r in enumerate(REVIEWS))
    reviews = band("04 &middot; Reviews", "Reviews, word for word.", score_html() + '<div class="reviews">%s</div>' % arts, "reviews")
    areas = band("05 &middot; Areas", "Where we work.",
                 "<p>Birmingham and the West Midlands. Each area page covers its housing, what goes wrong with its roofs, and the questions local owners ask.</p>"
                 + areas_list([(a["name"], pcs(a), "/areas/%s/" % a["slug"]) for a in AREAS_O]), "areas", "band--alt")
    page("/", "Emergency Roofers in Birmingham | Leaks & Storm Damage | RJR",
         "Emergency roof repairs in Birmingham: leaks, storm damage, slipped tiles, chimneys. Family run, 45 years' combined experience. WhatsApp %s." % SITE["phone"],
         hero + ticker() + emergency_block() + services + work + about + reviews + areas + faq_html(faqs, "Short answers.", "06 &middot; FAQ", ""),
         key="home", schema=[faq_node(BASE + "/", faqs)], og="fascia_a", preload=SITE["home_hero"])


def service_body(s, area=None):
    """Sections shared by service pages; area pages pass area for filled tokens."""
    A = area["name"] if area else "Birmingham"
    C = area["council"] if area else "Birmingham City Council or Solihull Metropolitan Borough Council"
    parts, items = [], []
    intro = "".join("<p>%s</p>" % e(fill(p, A, C)) for p in s.get("intro", []))
    cols = '<div class="flow-h"><h3>What&rsquo;s included</h3>%s</div>' % ruled(s["includes"])
    if s.get("signs"):
        cols += '<div class="flow-h"><h3>%s</h3>%s</div>' % ("When it&rsquo;s urgent" if s.get("emergency") else "Signs you need it", ruled(s["signs"]))
    parts.append(band("Overview", "What it covers.", '<div class="flow">%s</div><div class="cols-2">%s</div>' % (intro, cols), "overview"))
    items.append(("overview", "Overview"))
    if s.get("causes"):
        extra = callout("Leak or condensation?", s["leak_vs_condensation"]) if s.get("leak_vs_condensation") else ""
        parts.append(band("Causes", "What usually goes wrong.", defs(s["causes"]) + extra, "causes", "band--alt"))
        items.append(("causes", "Causes"))
    if s.get("anatomy"):
        parts.append(band("Anatomy", "The parts of a chimney.", defs(s["anatomy"]), "anatomy", "band--alt"))
        items.append(("anatomy", "Anatomy"))
    if s.get("options"):
        extra = callout("Warm roof or cold roof?", s["warm_cold"]) if s.get("warm_cold") else ""
        parts.append(band("Options", "Materials &amp; options.", spec(s["options"]) + extra, "options"))
        items.append(("options", "Options"))
    if s.get("process"):
        q = pull(s["quote"]) if s.get("quote") else ""
        parts.append(band("Process", "How we do it.", steps(s["process"]) + q, "process", "band--ink", "var(--neon)"))
        items.append(("process", "Process"))
    if s.get("projects"):
        parts.append(band("Proof", "Before &amp; after.", "".join(project_html(k, i + 1) for i, k in enumerate(s["projects"])), "proof"))
        items.append(("proof", "Photos"))
    money = ""
    if s.get("repair_or_replace"):
        money += callout("Repair or replace?", s["repair_or_replace"])
    blocks = ""
    if s.get("cost_factors"):
        blocks += '<div class="flow-h"><h3>What affects the price</h3>%s</div>' % ruled(s["cost_factors"])
    if s.get("prevent"):
        blocks += '<div class="flow-h"><h3>Keeping it from happening again</h3>%s</div>' % ruled(s["prevent"])
    if money or blocks:
        parts.append(band("Planning", "Cost, repair &amp; prevention.", money + '<div class="cols-2">%s</div>' % blocks, "planning", "band--alt"))
        items.append(("planning", "Cost &amp; prevention"))
    return parts, items


def build_service(s):
    path = "/services/%s/" % s["slug"]
    crumbs = [("Home", "/"), ("Services", "/services/"), (s["name"], path)]
    msg = "Hi RJR, I need help with %s. Postcode: " % s["name"].lower()
    facts = [("Service", e(s["name"])), ("Area", "Birmingham &amp; West Midlands")] + base_facts()
    head = page_hero(svc_hero(s), [s["trade"], "Birmingham &amp; West Midlands"] + (["Urgent"] if s.get("emergency") else []),
                     "%s in Birmingham" % e(s["h1"]), [e(fill(s["answer"]))], facts, msg)
    parts, items = service_body(s)
    body = "".join(parts)
    if s["slug"] == "emergency-roof-repairs":
        body = emergency_block() + body
        items = [("urgent", "Is it urgent?"), ("wait", "What to do")] + items
    if s.get("matrix"):
        body += band("Areas", "%s by area." % e(s["name"]),
                     areas_list([(a["name"], pcs(a), "/areas/%s/%s/" % (a["slug"], s["slug"])) for a in AREAS_O]), "by-area")
        items.append(("by-area", "Areas"))
    faqs = [(fill(q), fill(a)) for q, a in s["faqs"]]
    body += faq_html(faqs)
    items.append(("faq", "FAQ"))
    related = [x for x in SERVICES if x["slug"] != s["slug"]][:6]
    body += band("Related", "Related work.", index_list([(svc_title(x), x["summary"], "/services/%s/" % x["slug"]) for x in related], sm=True), "related")
    schema = [service_node(BASE + path, "%s in Birmingham" % s["name"], s["name"], fill(s["answer"])), faq_node(BASE + path, faqs)]
    ans = fill(s["answer"])
    page(path, "%s in Birmingham | RJR" % s["kw"], ans[:152].rsplit(" ", 1)[0] + "…", head + toc(items) + body,
         key="emergency" if s["slug"] == "emergency-roof-repairs" else "services", crumbs=crumbs, schema=schema,
         og=svc_hero(s), msg=msg, cta=s["cta"], preload=svc_hero(s),
         form={"service": s["slug"], "urgency": "emergency" if s.get("emergency") else ""})


def build_group(g):
    path = "/services/%s/" % g["slug"]
    crumbs = [("Home", "/"), ("Services", "/services/"), (g["name"], path)]
    msg = "Hi RJR, I'd like a quote for %s. Postcode: " % g["name"].lower()
    facts = [("Trade", g["trade"]), ("Area", "Birmingham &amp; West Midlands")] + base_facts()
    head = page_hero(g["hero"], [g["trade"], "Birmingham &amp; West Midlands"], "%s in Birmingham" % e(g["h1"]), [e(fill(g["answer"]))], facts, msg)
    body, items = "", []
    for i, (h, paras, bullets) in enumerate(g["sections"]):
        hid = "s%d" % (i + 1)
        inner = '<div class="flow">%s</div>%s' % ("".join("<p>%s</p>" % e(p) for p in paras), ruled(bullets) if bullets else "")
        body += band(g["trade"], e(h) + ".", inner, hid, "band--alt" if i % 2 else "")
        items.append((hid, h))
    for k in g.get("projects", []):
        body += band("Proof", "Photos.", project_html(k, 1), "proof")
        items.append(("proof", "Photos"))
    faqs = g["faqs"]
    body += faq_html(faqs)
    items.append(("faq", "FAQ"))
    schema = [service_node(BASE + path, g["name"], g["name"], fill(g["answer"])), faq_node(BASE + path, faqs)]
    page(path, "%s in Birmingham | RJR" % g["kw"], fill(g["answer"])[:152].rsplit(" ", 1)[0] + "…",
         head + toc(items) + body, key="services", crumbs=crumbs, schema=schema, og=g["hero"], msg=msg, cta=g["cta"], preload=g["hero"],
         form={"service": g["slug"]})


def build_services_index():
    head = page_hero("tile_a", ["Services", "Roofer &middot; Bricklayer &middot; Builder"], "Everything we do.",
                     ["Emergency roof repairs, storm damage and leaks first. Beyond that, our skills cover the whole building sector, from gutter clearances to full refurbishments."],
                     base_facts(), "Hi RJR, I'd like a quote. Postcode: ")
    rows = [(svc_title(s), s["summary"], "/services/%s/" % s["slug"]) for s in SERVICES]
    body = band("Roofing", "Roofing services.", index_list(rows, thumbs=[thumb(svc_hero(s)) for s in SERVICES]), "roofing")
    body += band("More trades", "Brickwork, stonework &amp; building.",
                 index_list([(e(g["name"]), g["summary"], "/services/%s/" % g["slug"]) for g in GROUPS], thumbs=[thumb(g["hero"]) for g in GROUPS]), "more", "band--alt")
    items = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": "%s/services/%s/" % (BASE, s["slug"]), "name": s["name"]}
                                                      for i, s in enumerate(SERVICES + GROUPS)]}
    page("/services/", "Roofing, Brickwork & Building Services in Birmingham | RJR",
         "Emergency roof repairs, storm damage, leaks, re-roofing, chimneys, flat roofs, guttering, fascias, Velux, brickwork and building work across Birmingham.",
         head + body, key="services", crumbs=[("Home", "/"), ("Services", "/services/")], schema=[items], og="tile_a", preload="tile_a")


def area_notes(a, s):
    notes = FEATURE_NOTES.get(s["slug"], {})
    return [notes[f] for f in a["features"] if f in notes]


def build_area(a, i):
    path = "/areas/%s/" % a["slug"]
    crumbs = [("Home", "/"), ("Areas", "/areas/"), (a["name"], path)]
    msg = "Hi RJR, I'm in %s (%s) and need help with my roof." % (a["name"], a["pcs"][0])
    facts = [("Area", a["name"]), ("Postcodes", pcs(a)), ("Council", a["council"])] + base_facts()
    head = page_hero(a["hero"], [pcs(a), a["name"], "Emergency roofers"], "Roofers in %s" % e(a["name"]),
                     ["RJR Home Improvements is a family-run roofing and building business working in %s (%s), with 45 years&rsquo; combined experience. Leaks and storm damage first; roofs, chimneys, gutters, fascias and roof windows too." % (e(a["name"]), pcs(a)),
                      e(a["stock"])], facts, msg)
    feats = '<dl class="features">%s</dl>' % "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(FEATURES[f][0]), e(FEATURES[f][1])) for f in a["features"])
    body = band("Local", "The houses in %s." % e(a["name"]), '<div class="flow"><p class="lede">%s</p><p>%s</p></div>' % (e(a["stock"]), e(a["planning"])), "local")
    body += band("Roofs", "What we see on %s roofs." % e(a["name"]), feats, "roofs", "band--alt")
    rows = [(svc_title(s), s["summary"], "%s%s/" % (path, s["slug"])) for s in MATRIX]
    body += band("Services", "Roofing in %s." % e(a["name"]),
                 index_list(rows, thumbs=[thumb(svc_hero(s)) for s in MATRIX])
                 + '<p>Plus guttering, fascias and soffits, Velux windows, leadwork, brickwork and building work across %s. <a class="textlink" href="/services/">All services &rarr;</a></p>' % e(a["name"]),
                 "services")
    body += emergency_block(a["name"])
    body += band("Proof", "Before &amp; after.", project_html(PROJECT_ROTA[i % len(PROJECT_ROTA)], 1), "proof")
    faqs = a["faqs"] + [("Do you cover %s for emergency roof repairs?" % a["name"],
                         "Yes. We work across %s (%s) and nearby areas including %s. For leaks or storm damage, WhatsApp a photo and your postcode to %s."
                         % (a["name"], pcs(a), ", ".join(AREA[n]["name"] for n in a["near"]), SITE["phone"]))]
    body += faq_html(faqs, "%s questions." % e(a["name"]))
    body += band("Nearby", "Nearby areas.", areas_list([(AREA[n]["name"], pcs(AREA[n]), "/areas/%s/" % n) for n in a["near"]]), "nearby")
    items = [("local", "Housing"), ("roofs", "Roof types"), ("services", "Services"), ("urgent", "Is it urgent?"), ("proof", "Photos"), ("faq", "FAQ"), ("nearby", "Nearby")]
    schema = [faq_node(BASE + path, faqs), {"@type": "Place", "@id": BASE + path + "#place", "name": a["name"],
              "address": {"@type": "PostalAddress", "addressLocality": a["name"], "postalCode": a["pcs"][0], "addressRegion": "West Midlands", "addressCountry": "GB"}}]
    page(path, "Roofers in %s (%s) | Emergency Roof Repairs | RJR" % (a["name"], pcs(a)),
         "Family-run roofers in %s, %s: emergency roof repairs, leaks, storm damage, chimneys and flat roofs, with local advice for %s homes. WhatsApp %s." % (a["name"], pcs(a), a["name"], SITE["phone"]),
         head + toc(items) + body, key="areas", crumbs=crumbs, schema=schema, og=a["hero"], msg=msg,
         cta="Roof problem in %s? Tell us here." % a["name"], preload=a["hero"], form={"area": a["slug"]})


def build_area_service(a, s, i):
    path = "/areas/%s/%s/" % (a["slug"], s["slug"])
    crumbs = [("Home", "/"), ("Areas", "/areas/"), (a["name"], "/areas/%s/" % a["slug"]), (s["name"], path)]
    msg = "Hi RJR, I'm in %s (%s) and need help with %s." % (a["name"], a["pcs"][0], s["name"].lower())
    notes = area_notes(a, s)
    facts = [("Service", e(s["name"])), ("Area", a["name"]), ("Postcodes", pcs(a)), ("Council", a["council"])] + base_facts()
    head = page_hero(svc_hero(s), [pcs(a), a["name"], e(s["name"])] + (["Urgent"] if s.get("emergency") else []),
                     "%s in %s" % (e(s["h1"]), e(a["name"])), [e(fill(s["answer"], a["name"], a["council"])), e(a["stock"])], facts, msg)
    local = qa_list(notes)
    feats = ", ".join(FEATURES[f][0].lower() for f in a["features"])
    body = band("Local", "%s on %s&rsquo;s roofs." % (e(s["name"]), e(a["name"])),
                '<p class="lede">Typical in %s: %s. That shapes what goes wrong and how it&rsquo;s repaired.</p>%s' % (e(a["name"]), e(feats), local), "local")
    items = [("local", "On %s roofs" % a["name"])]
    if s.get("emergency"):
        body += emergency_block(a["name"], full=False)
        items.append(("urgent", "Is it urgent?"))
    hub = "/services/%s/" % s["slug"]
    q = pull(a["quote"])
    body += band("Process", "How we do it.",
                 '<ol class="index-list index-list--sm">%s</ol>' % "".join('<li><a href="%s#process"><span class="t">%s</span></a></li>' % (hub, e(t)) for t, _ in s["process"])
                 + q, "process", "band--ink", "var(--neon)")
    items.append(("process", "Process"))
    if s.get("projects"):
        body += band("Proof", "Before &amp; after.", project_html(s["projects"][i % len(s["projects"])], 1), "proof", "band--alt")
        items.append(("proof", "Photos"))
    body += band("Planning", "Permissions in %s." % e(a["name"]),
                 '<div class="flow"><p class="lede">%s</p><p>What affects the price, and how to stop it happening again, is covered on our main <a class="textlink" href="%s#planning">%s page</a>.</p></div>'
                 % (e(a["planning"]), hub, e(s["name"].lower())), "planning")
    items.append(("planning", "Permissions"))
    svc_faqs = [(fill(x, a["name"], a["council"]), fill(y, a["name"], a["council"])) for x, y in s["faqs"]]
    rot = [svc_faqs[(i + k) % len(svc_faqs)] for k in range(min(3, len(svc_faqs)))]
    faqs = rot + [a["faqs"][i % len(a["faqs"])]]
    body += faq_html(faqs, "More %s questions." % e(a["name"]))
    items.append(("faq", "FAQ"))
    same = [(AREA[n]["name"], pcs(AREA[n]), "/areas/%s/%s/" % (n, s["slug"])) for n in a["near"]]
    others = [(svc_title(x), x["summary"], "/areas/%s/%s/" % (a["slug"], x["slug"])) for x in MATRIX if x["slug"] != s["slug"]]
    body += band("Nearby", "%s nearby." % e(s["name"]), areas_list(same) + "<h3>More in %s</h3>" % e(a["name"]) + index_list(others, sm=True), "nearby", "band--alt")
    items.append(("nearby", "Nearby"))
    schema = [service_node(BASE + path, "%s in %s" % (s["name"], a["name"]), s["name"], fill(s["answer"], a["name"], a["council"]), a),
              faq_node(BASE + path, notes + faqs)]
    lead = notes[0][1] if notes else a["stock"]
    desc = "%s in %s (%s). %s" % (s["name"], a["name"], pcs(a), lead)
    page(path, "%s in %s (%s) | RJR" % (s["kw"], a["name"], a["pcs"][0]), desc[:155].rsplit(" ", 1)[0] + "…",
         head + toc(items) + body, key="areas", crumbs=crumbs, schema=schema, og=svc_hero(s), msg=msg,
         cta="%s in %s? Tell us here." % (s["name"], a["name"]), preload=svc_hero(s),
         form={"area": a["slug"], "service": s["slug"], "urgency": "emergency" if s.get("emergency") else ""})


def build_areas_index():
    head = page_hero("fascia_a", ["Areas", "Birmingham &amp; West Midlands"], "Roofers across Birmingham.",
                     ["We work across Birmingham and the West Midlands. Recent verified reviews come from B17, B30, B31, B90 and WV4."],
                     [("Region", "West Midlands"), ("Councils", "Birmingham &middot; Solihull")] + base_facts(), "Hi RJR, I need help with my roof. Postcode: ")
    body = band("Areas", "Pick your area.", areas_list([(a["name"], pcs(a), "/areas/%s/" % a["slug"]) for a in AREAS_O]), "areas")
    matrix = "".join('<div class="flow-h"><h3><a href="/areas/%s/">%s</a> &middot; %s</h3>%s</div>' % (
        a["slug"], e(a["name"]), pcs(a), index_list([(svc_title(s), "", "/areas/%s/%s/" % (a["slug"], s["slug"])) for s in MATRIX], sm=True)) for a in AREAS_O)
    body += band("Directory", "Every service, every area.", '<div class="cols-2">%s</div>' % matrix, "directory", "band--alt")
    page("/areas/", "Roofers in Birmingham & Solihull: Areas Covered | RJR",
         "Areas covered by RJR Home Improvements: Edgbaston, Kings Heath, Moseley, Solihull, Shirley, Hall Green, Harborne, Selly Oak, Stirchley and Northfield.",
         head + body, key="areas", crumbs=[("Home", "/"), ("Areas", "/areas/")], og="fascia_a", preload="fascia_a")


def build_work():
    head = page_hero("velux_a", ["Before &amp; after", "Company photos"], "Same roof. Before, then after.",
                     ["Every sequence below is one job: the same building, matched by its windows, stack, tiles and surroundings. Each frame in a row uses the same crop so before and after line up."],
                     base_facts(), "Hi RJR, I've seen your before and after photos and need a quote. Postcode: ")
    order = ["chimney", "fascias", "velux", "reroof", "canopy", "leanto"]
    body = band("Jobs", "Before, during, after.", "".join(project_html(k, i + 1) for i, k in enumerate(order)), "jobs")
    page("/our-work/", "Before & After Roofing Photos, Birmingham | RJR",
         "Before and after photos of RJR Home Improvements jobs: chimney rebuild, gable fascias and guttering, Velux extension roof and re-roofing.",
         head + body, key="work", crumbs=[("Home", "/"), ("Before & after", "/our-work/")], og="velux_a", preload="velux_a",
         cta="Want the same for your roof? Tell us here.")


def build_reviews():
    head = page_hero("fascia_a", ["Reviews", "%d ratings" % SITE["rating_count"]], "Rated %s." % SITE["rating_label"],
                     ["Rated &ldquo;%s&rdquo; from %d ratings on Rated People. Reviews below are copied word for word. More on our Google Business Profile." % (SITE["rating_label"], SITE["rating_count"])],
                     base_facts(), "Hi RJR, I've read your reviews and need help with my roof. Postcode: ")
    arts = "".join(review_html(r, i == 0) for i, r in enumerate(REVIEWS))
    body = band("Reviews", "Recent reviews.", score_html() + '<div class="reviews">%s</div>' % arts, "reviews")
    body += band("Google", "Had work done by RJR?",
                 '<p class="lede">A review on our Google Business Profile helps neighbours find a roofer they can trust.</p><p>%s</p>' % ext(SITE["gbp"], "Review us on Google", "btn"),
                 "google", "band--neon", "var(--ink)")
    page("/reviews/", "Reviews | RJR Home Improvements, Birmingham Roofers",
         "RJR Home Improvements is rated Excellent from %d ratings on Rated People. Read verified reviews from B17, B30, B31, B90 and WV4, and see us on Google." % SITE["rating_count"],
         head + body, key="reviews", crumbs=[("Home", "/"), ("Reviews", "/reviews/")], og="fascia_a", preload="fascia_a")


def build_about():
    head = page_hero("chim_b2", ["About", "Family run"], "Family run. 45 years in the trade.", [e(ABOUT[0])], base_facts(), "Hi RJR, I'd like a quote. Postcode: ")
    body = """<section class="band band--orange" id="story" aria-labelledby="story-h"><div class="wrap grid">
  <div class="col-idx idx"><p>Story</p><span class="sw" style="--c:var(--ink)"></span></div>
  <div class="col-main flow-2"><div class="stat"><p class="stat-n">45</p><p class="label"><span>Years&rsquo; combined experience</span></p></div>
  <h2 id="story-h">About RJR.</h2><div class="flow">%s</div></div>
</div></section>""" % "".join("<p>%s</p>" % e(p) for p in ABOUT)
    trades = "".join('<div class="flow-h"><h3>%s</h3>%s</div>' % (e(t), ruled(items)) for t, items in TRADES.items())
    body += band("Trades", "Trades &amp; services.", '<div class="cols-2">%s</div>' % trades, "trades")
    body += band("Reviews", "In customers&rsquo; words.", pull("diagnosis") + pull("roofing"), "words", "band--ink", "var(--neon)")
    page("/about/", "About RJR Home Improvements | Family-Run Birmingham Roofers",
         "RJR Home Improvements is a family-run business with 45 years' combined experience, covering emergency roofing, bricklaying and building across Birmingham.",
         head + body, key="about", crumbs=[("Home", "/"), ("About", "/about/")], og="chim_b2", preload="chim_b2")


def legal_page(path, title, h1, intro, sections, desc):
    parts = []
    for h, paras in sections:
        parts.append("<h2>%s</h2>" % e(h))
        for p in paras:
            if isinstance(p, list):
                parts.append("<ul>%s</ul>" % "".join("<li>%s</li>" % x for x in p))
            else:
                parts.append("<p>%s</p>" % p)
    head = page_hero(None, ["Legal", "Updated %s" % SITE["updated_human"]], h1, [intro], None, "", buttons=False)
    body = '<section class="band"><div class="wrap"><div class="prose">%s</div></div></section>' % "".join(parts)
    page(path, title, desc, head + body, crumbs=[("Home", "/"), (h1, path)], cta="Questions about your data? Message us.")


def build_legal():
    who = "%s (trading as %s)" % (e(SITE["legal_name"]), e(SITE["name"]))
    if SITE["company_number"]:
        who += ", registered in England and Wales, company number %s" % e(SITE["company_number"])
    if SITE["registered_office"]:
        who += ", registered office: %s" % e(SITE["registered_office"])
    contact = 'WhatsApp or phone <a href="%s">%s</a>' % (TEL, SITE["phone"])
    if SITE["email"]:
        contact += ', or email <a href="mailto:%s">%s</a>' % (e(SITE["email"]), e(SITE["email"]))
    ico = " Our ICO registration number is %s." % e(SITE["ico_number"]) if SITE["ico_number"] else ""
    legal_page("/privacy-policy/", "Privacy Policy | RJR Home Improvements", "Privacy policy",
               "How %s collects, uses and protects your personal information." % e(SITE["name"]), [
        ("Who we are", ["This website is run by %s. We are the controller of the personal information described here.%s" % (who, ico),
                        "To contact us about your data: %s." % contact]),
        ("What we collect", ["When you contact us or we carry out work, we may hold:",
                             ["your name, phone number and, if you give it, your email address",
                              "the address or postcode of the property",
                              "details and photos of the job that you send us",
                              "records of quotes, invoices and payments",
                              "messages between us, including on WhatsApp"],
                             "The quote form on this website does not send or store anything. When you press \u201cContinue to WhatsApp\u201d, it writes your answers into a WhatsApp message on your own device. Nothing reaches us unless you choose to send that message. The website has no accounts and does not collect personal information unless you contact us."]),
        ("How we use it and why", [["<b>To reply to you and give a quote</b>: taking steps at your request before entering a contract.",
                                    "<b>To carry out and manage the work</b>: performing our contract with you.",
                                    "<b>To keep financial records</b>: complying with our legal obligations, including tax law.",
                                    "<b>To handle questions or complaints about our work</b>: our legitimate interests in running the business properly.",
                                    "<b>Optional website analytics</b>: only with your consent, which you can withdraw at any time."]]),
        ("Who we share it with", ["We do not sell your information. We share it only where needed to run the business, for example with our accountant, payment providers, and suppliers or scaffolding firms involved in your job, or where the law requires it.",
                                  "If you message us on WhatsApp, WhatsApp (Meta) processes those messages under its own privacy policy. Reviews you leave on Google or Rated People are handled by those platforms under their own policies."]),
        ("International transfers", ["Some services we use, such as WhatsApp and Google, may process data outside the UK. Where they do, they rely on legal safeguards such as UK adequacy regulations or approved contract terms."]),
        ("How long we keep it", ["We keep enquiry details for as long as needed to deal with your enquiry. For customers, we keep job and financial records for as long as the law requires, generally six years after the end of the financial year they relate to, and then delete them."]),
        ("Your rights", ["Under UK data protection law you can ask to access, correct or delete your personal information, to restrict or object to how we use it, and to receive a copy in a portable format. Where we rely on consent, you can withdraw it at any time.",
                         "To use any of these rights, contact us as above. If you're unhappy with how we handle your data, you can complain to the Information Commissioner's Office at %s." % ext("https://ico.org.uk/make-a-complaint/", "ico.org.uk")]),
        ("This website", ["The site is hosted by a web hosting provider, which may keep standard server logs (such as IP address, browser type and pages requested) for security and to keep the site running.",
                          "Fonts are loaded from Google Fonts, which means your browser connects to Google's servers and shares your IP address with Google.",
                          "Links to WhatsApp, Google Maps and Rated People take you to those services, which have their own privacy policies.",
                          'We use no tracking cookies unless you accept analytics. See our <a href="/cookie-policy/">cookie policy</a>.']),
        ("Changes", ["We may update this policy. The date at the top shows when it was last changed."]),
    ], "Privacy policy for RJR Home Improvements (R.J.R Home Improvements Ltd): what we collect, why, how long we keep it and your rights.")
    legal_page("/cookie-policy/", "Cookie Policy | RJR Home Improvements", "Cookie policy",
               "Which cookies and similar technologies this website uses, and how to change your choice.", [
        ("The short version", ["This website sets no cookies of its own by default. Optional analytics run only if you choose <b>Accept analytics</b>."]),
        ("Strictly necessary storage", ["When you make a choice on the cookie banner, we store it in your browser's local storage under the name <b>rjr-consent</b>, so we don't ask again on every page. It holds only your choice and the date, and is kept for 180 days. It is not shared with anyone."]),
        ("Analytics (optional, off by default)", ["If analytics are switched on for this site and you accept them, an analytics service may set cookies to count visits and see which pages are used. We only use this in aggregate to improve the site. If you reject, no analytics scripts load."]),
        ("Third-party services", ["Fonts are loaded from Google Fonts; this doesn't set cookies but does connect your browser to Google. Links to WhatsApp, Google Maps and Rated People take you to those sites, which set their own cookies under their own policies."]),
        ("Changing your choice", ['Use the <button type="button" data-consent-open style="text-decoration:underline">cookie settings</button> button, also in the footer of every page, to change your choice at any time. You can also clear site data in your browser settings.']),
    ], "Cookie policy for RJR Home Improvements: no tracking cookies by default, optional analytics only with consent.")


def build_contact():
    head = page_hero("velux_a", ["Contact", "Birmingham &amp; West Midlands"], "Get a quote.",
                     ["Fill in the form below. It opens WhatsApp with your answers written in, so you can add photos and send. For emergencies, you can also call %s." % SITE["phone"]],
                     base_facts(), "", buttons=True)
    nxt = [("Fill in the form", "Choose the service, how urgent it is and your area, and tell us what's happening."),
           ("Add photos in WhatsApp", "WhatsApp opens with your message ready. Attach photos of the problem, inside and out, then press send."),
           ("We come back to you", "We reply by WhatsApp or phone, whichever you chose, about what it needs and when we can get there.")]
    body = band("How it works", "Three steps.", steps(nxt) + pull("fast"), "how", "band--ink", "var(--neon)")
    schema = [{"@type": "ContactPage", "@id": BASE + "/contact/#contact", "url": BASE + "/contact/", "name": "Get a quote", "about": {"@id": BIZ}}]
    page("/contact/", "Contact & Quotes | RJR Home Improvements, Birmingham Roofers",
         "Get a roofing quote from RJR Home Improvements: fill in the form and it opens WhatsApp ready to send with your photos. Or call %s." % SITE["phone"],
         head + body, key="contact", crumbs=[("Home", "/"), ("Contact", "/contact/")], schema=schema, og="velux_a", preload="velux_a",
         cta="Tell us what\u2019s wrong with the roof.")


def build_sitemap_page():
    ul = lambda rows: '<ul class="ruled">%s</ul>' % "".join('<li><a href="%s">%s</a></li>' % (u, e(n)) for n, u in rows)
    core = [("Home", "/"), ("Contact", "/contact/"), ("Services", "/services/"), ("Areas", "/areas/"), ("Before & after", "/our-work/"), ("Reviews", "/reviews/"),
            ("About", "/about/"), ("Privacy policy", "/privacy-policy/"), ("Cookie policy", "/cookie-policy/")]
    blocks = ['<div class="flow-h"><h3>Pages</h3>%s</div>' % ul(core),
              '<div class="flow-h"><h3>Services</h3>%s</div>' % ul([(s["name"], "/services/%s/" % s["slug"]) for s in SERVICES + GROUPS])]
    for a in AREAS_O:
        rows = [(a["name"] + " overview", "/areas/%s/" % a["slug"])] + [(s["name"], "/areas/%s/%s/" % (a["slug"], s["slug"])) for s in MATRIX]
        blocks.append('<div class="flow-h"><h3>%s &middot; %s</h3>%s</div>' % (e(a["name"]), pcs(a), ul(rows)))
    head = page_hero(None, ["Sitemap"], "Every page.", ["All pages on the RJR Home Improvements website."], None, "", buttons=False)
    page("/sitemap/", "Sitemap | RJR Home Improvements", "Every page on the RJR Home Improvements website.",
         head + '<section class="band"><div class="wrap"><div class="cols-2">%s</div></div></section>' % "".join(blocks),
         crumbs=[("Home", "/"), ("Sitemap", "/sitemap/")])


def build_404():
    head = page_hero("canopy_d", ["404"], "That page has slipped.", ["The page you were looking for isn&rsquo;t here. Try the links below, or send us a message."], None,
                     "Hi RJR, I need help with my roof. Postcode: ")
    body = band("Try", "Popular pages.", index_list([("Emergency roof repairs", "", "/services/emergency-roof-repairs/"), ("All services", "", "/services/"),
                                                     ("Areas", "", "/areas/"), ("Home", "", "/")], sm=True), "try")
    page("/404.html", "Page not found | RJR Home Improvements", "Page not found.", head + body, noindex=True)


def write_meta():
    groups = {}
    for p, g in PAGES:
        groups.setdefault(g, []).append(p)
    names = []
    for g, paths in groups.items():
        urls = "".join("<url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n" % (BASE, p, SITE["lastmod"]) for p in sorted(paths))
        (OUT / ("sitemap-%s.xml" % g)).write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls)
        names.append("sitemap-%s.xml" % g)
    idx = "".join("<sitemap><loc>%s/%s</loc><lastmod>%s</lastmod></sitemap>\n" % (BASE, n, SITE["lastmod"]) for n in names)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</sitemapindex>\n' % idx)
    if DEMO:
        (OUT / "robots.txt").write_text("# Demo build: not for search engines. Rebuild without DEMO=1 at launch.\nUser-agent: *\nDisallow: /\n")
    else:
        (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASE)
    svc = "\n".join("- [%s](%s/services/%s/): %s" % (s["name"], BASE, s["slug"], s["summary"]) for s in SERVICES + GROUPS)
    ars = "\n".join("- [%s (%s)](%s/areas/%s/): %s" % (a["name"], pcs(a), BASE, a["slug"], a["stock"]) for a in AREAS_O)
    revs = "\n".join("- %s, %s, %s (verified): %s" % (r["name"], r["pc"], r["disp"], '"%s"' % r["text"] if r["text"] else "rating without written comment") for r in REVIEWS)
    (OUT / "llms.txt").write_text("""# %(name)s

> Family-run roofing, bricklaying and building business (%(legal)s) serving Birmingham and the West Midlands, focused on emergency roof repairs, storm damage and roof leaks. %(yrs)d years' combined experience. Rated "%(label)s" from %(count)d ratings on Rated People.

## Key facts
- Legal name: %(legal)s
- Companies House number: %(cn)s
- Business type: family run
- Lead services: emergency roof repairs, storm damage repairs, roof leak repairs
- Trades: roofer, bricklayer, builder, blacksmith / metal worker
- Experience: %(yrs)d years combined in the trade
- Rating: %(label)s, %(count)d ratings on Rated People (%(rp)s)
- Google Business Profile: %(gbp)s
- Service area: Birmingham and the West Midlands, including Edgbaston, Kings Heath, Moseley, Solihull, Shirley, Hall Green, Harborne, Selly Oak, Stirchley and Northfield
- Contact: WhatsApp https://wa.me/%(wa)s · phone %(phone)s

## About
%(about)s

## Services
%(svc)s

## Areas
%(areas)s

## Recent reviews (verbatim, Rated People)
%(revs)s
""" % {"name": SITE["name"], "legal": SITE["legal_name"], "yrs": SITE["experience_years"], "label": SITE["rating_label"], "count": SITE["rating_count"],
       "rp": SITE["rated_people"], "cn": SITE["company_number"] or "not listed", "gbp": SITE["gbp"], "wa": SITE["whatsapp"], "phone": SITE["phone"], "about": " ".join(ABOUT),
       "svc": svc, "areas": ars, "revs": revs}, encoding="utf-8")


def main():
    global MANIFEST, VERSION
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    MANIFEST = optimise(IMG, ROOT / "images", OUT / "assets" / "img")
    h = hashlib.md5()
    for f in ("site.css", "consent.js", "quote.js"):
        h.update((OUT / "assets" / f).read_bytes())
    VERSION = h.hexdigest()[:8]
    build_home()
    build_services_index()
    for s in SERVICES:
        build_service(s)
    for g in GROUPS:
        build_group(g)
    build_areas_index()
    for i, a in enumerate(AREAS_O):
        build_area(a, i)
        for s in MATRIX:
            build_area_service(a, s, i)
    build_work()
    build_reviews()
    build_about()
    build_legal()
    build_contact()
    build_sitemap_page()
    build_404()
    write_meta()
    print("Built %d pages into %s" % (len(PAGES), OUT))
    print("DEMO MODE: every page is noindex and robots.txt blocks crawlers. Remove DEMO=1 at launch." if DEMO
          else "LIVE MODE: pages are indexable at %s" % BASE)


if __name__ == "__main__":
    main()
