"""Builds the OnceMore Digital static site.
Each page gets its own title, meta description, canonical, Open Graph,
Twitter card and JSON-LD schema. GTM and the og:image path are preserved
exactly from the original markup. Output is plain static HTML for GitHub Pages.
"""
import os, json, html, re
from content import SERVICE_CONTENT, RESOURCES

SITE = "/home/claude/site"
URL = "https://oncemoredigital.com"
EMAIL = "walter@oncemoredigital.com"
GTM = "GTM-MJ5WCPR6"
UPDATED = "June 2026"
OG_IMAGE = URL + "/oncemoredigial-seo-marketing-logo.jpg"  # the user's real logo already in the repo
ADDRESS = {
    "@type": "PostalAddress",
    "streetAddress": "BO1-A-9, Menara 2, KL Eco City, 3, Jln Bangsar",
    "addressLocality": "Kuala Lumpur",
    "postalCode": "59200",
    "addressCountry": "MY",
}

# ---------------------------------------------------------------- shared parts
GTM_HEAD = (
    "<!-- Google Tag Manager -->\n"
    "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\n"
    "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\n"
    "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
    "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n"
    "})(window,document,'script','dataLayer','" + GTM + "');</script>\n"
    "<!-- End Google Tag Manager -->"
)
GTM_BODY = (
    "<!-- Google Tag Manager (noscript) -->\n"
    "<noscript><iframe src=\"https://www.googletagmanager.com/ns.html?id=" + GTM + "\"\n"
    "height=\"0\" width=\"0\" style=\"display:none;visibility:hidden\"></iframe></noscript>\n"
    "<!-- End Google Tag Manager (noscript) -->"
)

NAV = """<header class="site-header"><div class="container"><nav class="nav" aria-label="Primary">
  <a class="brand" href="/"><img src="/assets/img/logo-wordmark.png" alt="OnceMore Digital" class="brand-logo"></a>
  <button class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="nav-links">&#9776;</button>
  <ul class="nav-links" id="nav-links">
    <li><a href="/"{home}>Home</a></li>
    <li class="nav-item has-dropdown">
      <a href="/services/"{services}>Services</a>
      <ul class="dropdown">
        <li><a href="/services/seo/">SEO</a></li>
        <li><a href="/services/geo/">GEO</a></li>
        <li><a href="/services/ai-optimisation/">AI Optimisation</a></li>
        <li><a href="/services/content-writing/">Content Writing</a></li>
        <li><a href="/services/google-ads/">Google Ads</a></li>
      </ul>
    </li>
    <li><a href="/resources/"{resources}>Resources</a></li>
    <li><a href="/about/"{about}>About</a></li>
    <li><a href="/contact/"{contact}>Contact</a></li>
    <li><a class="nav-cta" href="mailto:%s">Get in Touch</a></li>
  </ul>
</nav></div></header>""" % EMAIL

FOOTER = """<footer class="site-footer"><div class="container">
  <div class="footer-grid">
    <div class="footer-brand">
      <a class="brand" href="/"><img src="/assets/img/logo-wordmark.png" alt="OnceMore Digital" class="brand-logo footer-logo"></a>
      <p>SEO, GEO, AI optimisation, content and Google Ads for businesses in Malaysia.</p>
      <address class="footer-address">BO1-A-9, Menara 2, KL Eco City,<br>3, Jln Bangsar, 59200 Kuala Lumpur, Malaysia</address>
      <p class="footer-ssm">SSM: 202604001053 (LLP0046284-LGN)</p>
    </div>
    <div>
      <h4>Services</h4>
      <ul>
        <li><a href="/services/seo/">SEO</a></li>
        <li><a href="/services/geo/">GEO</a></li>
        <li><a href="/services/ai-optimisation/">AI Optimisation</a></li>
        <li><a href="/services/content-writing/">Content Writing</a></li>
        <li><a href="/services/google-ads/">Google Ads</a></li>
      </ul>
    </div>
    <div>
      <h4>Resources</h4>
      <ul>
        <li><a href="/resources/">All guides</a></li>
        <li><a href="/resources/seo-guide-malaysia/">SEO guide for Malaysia</a></li>
        <li><a href="/resources/what-is-geo/">What is GEO?</a></li>
        <li><a href="/resources/seo-cost-malaysia/">SEO cost in Malaysia</a></li>
      </ul>
    </div>
    <div>
      <h4>Company</h4>
      <ul>
        <li><a href="/about/">About</a></li>
        <li><a href="/contact/">Contact</a></li>
        <li><a href="mailto:%s">Email us</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">&copy; 2026 OnceMore Digital Services. All rights reserved.</div>
</div></footer>""" % EMAIL


def nav_for(active):
    cur = ' aria-current="page"'
    return NAV.format(
        home=cur if active == "home" else "",
        services=cur if active == "services" else "",
        resources=cur if active == "resources" else "",
        about=cur if active == "about" else "",
        contact=cur if active == "contact" else "",
    )


def jsonld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, indent=2) + "\n</script>"


def breadcrumb(items):
    return jsonld({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": URL + p}
            for i, (n, p) in enumerate(items)
        ],
    })


def faq_block(items):
    """Returns (html, jsonld) for a FAQ section."""
    rows = "".join(
        "<details><summary>%s</summary><p>%s</p></details>" % (html.escape(q), html.escape(a))
        for q, a in items
    )
    block = ('<section class="section-sm"><div class="container">'
             '<span class="eyebrow">FAQ</span><h2>Common questions</h2>'
             '<div class="faq">%s</div></div></section>' % rows)
    schema = jsonld({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in items
        ],
    })
    return block, schema


def page(path, title, desc, body, extra_head="", active="", schema_blocks=None):
    canonical = URL + path
    head_schema = "\n".join(schema_blocks or [])
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">

<link rel="icon" type="image/png" sizes="256x256" href="/assets/img/favicon.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">

<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="OnceMore Digital">
<meta property="og:locale" content="en_MY">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:alt" content="OnceMore Digital">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{OG_IMAGE}">

<link rel="preconnect" href="https://api.fontshare.com" crossorigin>
<link rel="preconnect" href="https://cdn.fontshare.com" crossorigin>
<link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=satoshi@300,400,500,700,900&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=satoshi@300,400,500,700,900&display=swap"></noscript>
<link rel="stylesheet" href="/assets/css/style.css">

{GTM_HEAD}

{head_schema}
</head>
<body>
{GTM_BODY}
<div class="wrap">
{nav_for(active)}
<main id="main">
{body}
</main>
{FOOTER}
</div>
<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""
    full = os.path.join(SITE, path.strip("/"), "index.html") if path != "/" else os.path.join(SITE, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(doc)
    return full


# ---------------------------------------------------------------- service data
SERVICES = [
    ("seo", "SEO", "Search Engine Optimisation",
     "Rank higher on Google for the searches your customers actually make.",
     "We map the keywords that bring qualified traffic, fix the technical issues holding your site back, and build content and links that earn rankings over time. The focus is steady organic growth, not quick wins that fade.",
     ["Keyword research and content mapping",
      "Technical audits and site health fixes",
      "On-page optimisation for target pages",
      "Local SEO and Google Business Profile",
      "Monthly reporting you can actually read"],
     [("How long does SEO take to show results?",
       "Most sites see early movement within three to six months. Competitive terms and newer domains take longer. We report progress monthly so you always know where things stand."),
      ("Do you guarantee a number one ranking?",
       "No honest provider can guarantee a specific position, because Google decides rankings. We focus on the work that reliably improves visibility and the traffic that follows.")]),
    ("geo", "GEO", "Generative Engine Optimisation",
     "Get your business cited in AI search and answer engines.",
     "Generative engines like Google AI Overviews summarise the web and cite a handful of sources. GEO structures your content and entity signals so those tools can find, trust and quote your pages when people ask questions in your space.",
     ["Content structured for AI extraction",
      "Entity and topical authority signals",
      "Schema markup that machines can read",
      "Clear, quotable answers on key pages",
      "Tracking where you appear in AI results"],
     [("Is GEO different from SEO?",
       "They overlap but are not the same. SEO targets the classic results list. GEO targets the AI generated summaries that increasingly sit above it, where being cited matters more than ranking."),
      ("Can you control what AI says about a business?",
       "Not fully. You influence it by publishing clear, accurate, well structured content that answer engines can read and trust. That is the work we focus on.")]),
    ("ai-optimisation", "AI Optimisation", "AI Optimisation (AIO)",
     "Make your content easy for AI tools to read, trust and recommend.",
     "AI optimisation is the practical layer underneath GEO. We make sure your pages are clean, well structured and marked up so assistants such as ChatGPT, Gemini and Perplexity can parse them correctly and surface your business in their answers.",
     ["FAQ and how-to structure on key pages",
      "Structured data and schema markup",
      "Clear headings and scannable formatting",
      "Accurate, source-worthy content",
      "Auditing how AI tools read your site"],
     [("Which AI tools does this help with?",
       "The same fundamentals help across ChatGPT, Gemini, Perplexity, Copilot and Google AI Overviews. Clean structure and trustworthy content travel well between them."),
      ("Do I need this if I already do SEO?",
       "If people in your market are starting to ask AI tools instead of searching, yes. AI optimisation protects your visibility as search habits shift.")]),
    ("content-writing", "Content Writing", "Content Writing",
     "Content that reads well for people and ranks well for search.",
     "We write content that answers real questions, fits your brand voice and supports your wider SEO and GEO goals. Every piece is mapped to search intent and the customer journey, so it does a job rather than just filling a page.",
     ["Blog posts and articles mapped to intent",
      "Landing and service page copy",
      "Localised copy for Malaysian audiences",
      "Multilingual options where needed",
      "Briefs built from keyword research"],
     [("Is the content original?",
       "Yes. Everything is written for your brand and your audience, then checked for accuracy and clarity before it reaches you."),
      ("Can you match our tone of voice?",
       "We work from your existing material and a short brief, so new content sounds like you rather than a generic template.")]),
    ("google-ads", "Google Ads", "Google Ads",
     "Reach customers the moment they are searching, with budget under control.",
     "Paid search gives you visibility while your organic work builds. We set up and manage campaigns around clear goals, tight targeting and honest reporting, so you can see what every ringgit is doing.",
     ["Search and performance campaign setup",
      "Keyword and audience targeting",
      "Conversion tracking and clean attribution",
      "Budget management and bid strategy",
      "Reporting tied to real outcomes"],
     [("How much should I budget for Google Ads?",
       "It depends on your market and goals. We start with a sensible test budget, measure what converts, then scale what works rather than guessing up front."),
      ("Do ads help my SEO?",
       "Ads do not directly improve organic rankings, but they bring fast traffic and useful data that can sharpen your SEO and content decisions.")]),
]

SERVICE_BY_SLUG = {s[0]: s for s in SERVICES}

# ---------------------------------------------------------------- inline icons
_S = ('<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6" '
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">')
ICONS = {
    "seo": _S + '<circle cx="14" cy="14" r="8"/><line x1="20" y1="20" x2="27" y2="27"/>'
                '<path d="M11 17v-3M14 17v-5M17 17v-7"/></svg>',
    "geo": _S + '<path d="M5 8a3 3 0 0 1 3-3h16a3 3 0 0 1 3 3v9a3 3 0 0 1-3 3H14l-6 5v-5a3 3 0 0 1-3-3z"/>'
                '<path d="M18 9l1.3 3.2 3.2 1.3-3.2 1.3L18 18l-1.3-3.2L13.5 13.5l3.2-1.3z"/></svg>',
    "ai-optimisation": _S + '<path d="M14 4l2.4 6.6L23 13l-6.6 2.4L14 22l-2.4-6.6L5 13l6.6-2.4z"/>'
                            '<path d="M24 18l1.1 3L28 22l-2.9 1.1L24 26l-1.1-2.9L20 22l2.9-1.1z"/></svg>',
    "content-writing": _S + '<line x1="6" y1="10" x2="20" y2="10"/><line x1="6" y1="16" x2="16" y2="16"/>'
                            '<line x1="6" y1="22" x2="13" y2="22"/><path d="M20 24l6-6 3 3-6 6-4 1z"/></svg>',
    "google-ads": _S + '<path d="M12 9l13 5.5-5.6 1.9-1.9 5.6z"/><path d="M8 8 6 6M7 13H4M13 7V4"/></svg>',
}

def card_html(slug, name, tagline, featured=False):
    cls = "card featured" if featured else "card"
    return ('<a class="%s" href="/services/%s/"><span class="icon">%s</span>'
            '<h3>%s</h3><p>%s</p><span class="more">Learn more &rarr;</span></a>'
            % (cls, slug, ICONS[slug], name, tagline))

# Stylized search + AI answer illustration (original artwork, no third-party logos)
HERO_SVG = '''<svg class="hero-illustration" viewBox="0 0 560 380" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A search results page next to an AI answer panel">
  <rect x="20" y="24" width="520" height="312" rx="14" fill="rgba(77,101,175,0.05)" stroke="rgba(122,144,199,0.45)" stroke-width="1.5"/>
  <line x1="20" y1="62" x2="540" y2="62" stroke="rgba(122,144,199,0.3)" stroke-width="1.5"/>
  <circle cx="44" cy="43" r="4" fill="#4d65af"/><circle cx="60" cy="43" r="4" fill="rgba(122,144,199,0.5)"/><circle cx="76" cy="43" r="4" fill="rgba(122,144,199,0.3)"/>
  <rect x="60" y="86" width="440" height="44" rx="22" fill="rgba(255,255,255,0.03)" stroke="rgba(122,144,199,0.6)" stroke-width="1.5"/>
  <circle cx="92" cy="108" r="9" stroke="#7a90c7" stroke-width="2"/><line x1="99" y1="115" x2="108" y2="124" stroke="#7a90c7" stroke-width="2" stroke-linecap="round"/>
  <rect x="122" y="104" width="150" height="7" rx="3.5" fill="rgba(122,144,199,0.5)"/>
  <line x1="470" y1="98" x2="470" y2="118" stroke="#7a90c7" stroke-width="2" stroke-linecap="round"/>
  <rect x="60" y="160" width="190" height="10" rx="5" fill="#4d65af"/>
  <rect x="60" y="180" width="360" height="6" rx="3" fill="rgba(122,144,199,0.28)"/>
  <rect x="60" y="194" width="300" height="6" rx="3" fill="rgba(122,144,199,0.28)"/>
  <rect x="60" y="228" width="160" height="10" rx="5" fill="#4d65af"/>
  <rect x="60" y="248" width="330" height="6" rx="3" fill="rgba(122,144,199,0.28)"/>
  <rect x="60" y="262" width="270" height="6" rx="3" fill="rgba(122,144,199,0.28)"/>
  <rect x="300" y="232" width="218" height="92" rx="14" fill="rgba(77,101,175,0.18)" stroke="rgba(122,144,199,0.7)" stroke-width="1.5"/>
  <path d="M326 256l3.4 8.6 8.6 3.4-8.6 3.4L326 280l-3.4-8.6L314 268l8.6-3.4z" fill="#7a90c7"/>
  <rect x="346" y="258" width="150" height="8" rx="4" fill="rgba(244,244,242,0.85)"/>
  <rect x="346" y="274" width="120" height="6" rx="3" fill="rgba(122,144,199,0.5)"/>
  <rect x="318" y="298" width="180" height="6" rx="3" fill="rgba(122,144,199,0.32)"/>
  <rect x="318" y="312" width="150" height="6" rx="3" fill="rgba(122,144,199,0.32)"/>
</svg>'''

# ---------------------------------------------------------------- client logos
CLIENT_LOGOS = [
    ("aig.png", "AIG"),
    ("hertz.png", "Hertz"),
    ("nestle.png", "Nestle"),
    ("maggi.png", "Maggi"),
    ("ikea.png", "IKEA"),
    ("bank-negara.png", "Bank Negara Malaysia"),
    ("wspace.png", "WSPACE"),
    ("xcl.png", "XCL Education"),
    ("real-schools.png", "REAL Schools"),
    ("common-ground.png", "Common Ground"),
]

def clients_marquee():
    chips = "".join(
        '<div class="logo-chip"><img src="/assets/img/clients/%s" alt="%s" decoding="async"></div>'
        % (f, a) for f, a in CLIENT_LOGOS)
    track = chips + chips  # duplicated for a seamless loop
    return ('<section class="section-sm clients"><div class="container">'
            '<div class="clients-head"><span class="eyebrow">Clients</span>'
            '<h2>Brands we have worked with</h2></div>'
            '<div class="logos" aria-label="Logos of brands we have worked with">'
            '<div class="logos-track">%s</div></div>'
            '</div></section>') % track

CLIENTS_HTML = clients_marquee()

# ---------------------------------------------------------------- guide visuals
# a small ringgit-tag icon for the cost guide card
_TAG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M20 12l-8 8-9-9V3h8z"/>'
        '<circle cx="7.5" cy="7.5" r="1.4"/></svg>')
GUIDE_ICONS = {
    "seo-guide-malaysia": ICONS["seo"],
    "what-is-geo": ICONS["geo"],
    "seo-cost-malaysia": _TAG,
}

_C_INK = '#7a90c7'
GUIDE_ILLO = {
 # three pillars of SEO
 "seo-guide-malaysia": (
  '<svg class="guide-illustration" viewBox="0 0 560 300" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The three pillars of SEO: technical health, content and authority, supporting rankings">'
  '<title>The three pillars of SEO</title>'
  '<rect x="40" y="40" width="480" height="40" rx="6" fill="rgba(77,101,175,0.18)" stroke="#4d65af"/>'
  '<text x="280" y="65" text-anchor="middle" fill="#f4f4f2" font-family="Satoshi,Arial" font-size="17" font-weight="700">Rankings &amp; visibility</text>'
  + "".join(
     f'<rect x="{x}" y="120" width="150" height="140" rx="8" fill="rgba(77,101,175,0.08)" stroke="rgba(77,101,175,0.45)"/>'
     f'<text x="{x+75}" y="180" text-anchor="middle" fill="{_C_INK}" font-family="Satoshi,Arial" font-size="14" font-weight="700">{t}</text>'
     f'<text x="{x+75}" y="205" text-anchor="middle" fill="#9aa3b8" font-family="Satoshi,Arial" font-size="11">{s}</text>'
     for x, t, s in [(40, "Technical", "crawlable, fast"), (205, "Content", "intent matched"), (370, "Authority", "trusted links")])
  + '<path d="M115 120v-40M280 120v-40M445 120v-40" stroke="rgba(77,101,175,0.5)" stroke-width="1.5" stroke-dasharray="4 4"/>'
  '</svg>'),
 # question -> AI -> cited sources
 "what-is-geo": (
  '<svg class="guide-illustration" viewBox="0 0 560 300" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A question goes to an AI engine, which cites your business among its sources">'
  '<title>How AI answer engines cite sources</title>'
  '<rect x="30" y="120" width="150" height="60" rx="10" fill="rgba(77,101,175,0.10)" stroke="rgba(77,101,175,0.5)"/>'
  '<text x="105" y="155" text-anchor="middle" fill="#f4f4f2" font-family="Satoshi,Arial" font-size="13">"best ... in KL?"</text>'
  '<rect x="220" y="110" width="120" height="80" rx="12" fill="rgba(77,101,175,0.18)" stroke="#4d65af"/>'
  '<path d="M252 150l7 7 12-14" stroke="#7a90c7" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
  '<text x="280" y="178" text-anchor="middle" fill="#9aa3b8" font-family="Satoshi,Arial" font-size="11">AI engine</text>'
  '<rect x="400" y="95" width="150" height="34" rx="6" fill="rgba(77,101,175,0.12)" stroke="#4d65af"/>'
  '<text x="475" y="117" text-anchor="middle" fill="#7a90c7" font-family="Satoshi,Arial" font-size="12" font-weight="700">Your business</text>'
  '<rect x="400" y="140" width="150" height="22" rx="5" fill="rgba(154,163,184,0.10)" stroke="rgba(154,163,184,0.3)"/>'
  '<rect x="400" y="170" width="150" height="22" rx="5" fill="rgba(154,163,184,0.10)" stroke="rgba(154,163,184,0.3)"/>'
  '<path d="M180 150h35M340 150h55" stroke="rgba(77,101,175,0.6)" stroke-width="2" marker-end="url(#ar)"/>'
  '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0l6 3-6 3z" fill="rgba(77,101,175,0.8)"/></marker></defs>'
  '<text x="475" y="210" text-anchor="middle" fill="#9aa3b8" font-family="Satoshi,Arial" font-size="11">cited sources</text>'
  '</svg>'),
 # cost factors -> scope -> value
 "seo-cost-malaysia": (
  '<svg class="guide-illustration" viewBox="0 0 560 300" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Cost depends on market, starting point and competition, which set the scope and the value returned">'
  '<title>What drives the cost of SEO</title>'
  + "".join(
     f'<rect x="40" y="{y}" width="180" height="44" rx="8" fill="rgba(77,101,175,0.08)" stroke="rgba(77,101,175,0.4)"/>'
     f'<text x="130" y="{y+28}" text-anchor="middle" fill="#cfd6e6" font-family="Satoshi,Arial" font-size="13">{t}</text>'
     for y, t in [(60, "Your market"), (128, "Starting point"), (196, "Competition")])
  + '<rect x="300" y="110" width="110" height="80" rx="10" fill="rgba(77,101,175,0.18)" stroke="#4d65af"/>'
  '<text x="355" y="155" text-anchor="middle" fill="#f4f4f2" font-family="Satoshi,Arial" font-size="14" font-weight="700">Scope</text>'
  '<rect x="450" y="120" width="80" height="60" rx="10" fill="rgba(77,101,175,0.12)" stroke="#4d65af"/>'
  '<text x="490" y="156" text-anchor="middle" fill="#7a90c7" font-family="Satoshi,Arial" font-size="13" font-weight="700">Value</text>'
  '<path d="M220 82h80v40M220 150h80M220 218h80v-40M410 150h40" stroke="rgba(77,101,175,0.55)" stroke-width="1.6" fill="none"/>'
  '</svg>'),
}

# ---------------------------------------------------------------- home page

CAPABILITY_TAGS = ["Insurance", "Automotive &amp; Travel", "Retail", "FMCG",
                   "Education", "Government &amp; Finance"]

PROCESS_STEPS = [
    ("Understand your business and your customers first",
     "A clinic and an e-commerce brand are not fighting the same battle. We start with your situation."),
    ("Map the searches and questions that matter",
     "We find the keywords and questions genuinely connected to what you sell, not just what has volume."),
    ("Fix the foundations before chasing growth",
     "Technical issues, weak content and gaps in structure get sorted before we push for rankings."),
    ("Measure honestly and adjust as we learn",
     "Monthly reporting in plain terms, including what is not working yet and what we are changing."),
]

bento_cards = "".join(
    card_html(s[0], s[1], s[3], featured=(s[0] == "seo")) for s in SERVICES
)

process_cards = "".join(
    '<div class="process-step"><span class="dot">%02d</span><h3>%s</h3><p>%s</p></div>'
    % (i + 1, html.escape(t), html.escape(b))
    for i, (t, b) in enumerate(PROCESS_STEPS)
)

capability_pills = "".join('<span>%s</span>' % t for t in CAPABILITY_TAGS)

home_body = """
<section class="hero"><div class="container">
  <div class="hero-grid">
    <div class="hero-copy">
      <span class="eyebrow">SEO &amp; AI Optimisation</span>
      <h1>Helping businesses<br>get found <em>online.</em></h1>
      <p class="lead">We help businesses across Malaysia rank on Google, show up in AI search results, and grow organically through smart SEO, content and paid strategy.</p>
      <div class="services-tags" role="list" aria-label="Our services">
        <span class="service-tag" role="listitem">SEO</span>
        <span class="service-tag" role="listitem">GEO</span>
        <span class="service-tag" role="listitem">AI Optimisation</span>
        <span class="service-tag" role="listitem">Content Writing</span>
        <span class="service-tag" role="listitem">Google Ads</span>
      </div>
      <div class="btn-row">
        <a class="btn btn-primary" href="/contact/">Get in Touch</a>
        <a class="btn btn-ghost" href="/services/">See What We Do</a>
      </div>
    </div>
    <div class="hero-media" aria-hidden="true">
      HERO_SVG_PLACEHOLDER
    </div>
  </div>
</div></section>

<section class="section panel-alt capability-band"><div class="container">
  <div class="capability-head">
    <span class="eyebrow">Industries we've worked in</span>
  </div>
  <div class="capability-row" role="list" aria-label="Industries we have worked in">CAPABILITY_PILLS</div>
</div></section>

CLIENTS_MARQUEE

<section class="section"><div class="container">
  <span class="eyebrow">What we do</span>
  <h2>Five ways we help you grow</h2>
  <p>Each service stands on its own or works together as one organic growth plan. SEO is where most engagements start.</p>
  <div class="bento" style="margin-top:2rem">
    BENTO_CARDS
  </div>
</div></section>

<section class="section panel-alt"><div class="container">
  <span class="eyebrow">How we work</span>
  <h2>The same process, every time.</h2>
  <p>No two businesses get the same strategy, but every engagement runs through the same four steps.</p>
  <div class="process-strip">PROCESS_CARDS</div>
</div></section>

<section class="section statement-panel"><div class="container">
  <div class="statement-grid">
    <div class="statement">
      <p>Rankings are not luck. They are what happens when the <em>technical work</em>, the <em>content</em> and the <em>authority</em> all point the same direction.</p>
    </div>
    <div class="statement-note">
      <span class="eyebrow">Our approach</span>
      <p>We treat SEO, GEO and AI optimisation as one system, not three separate line items on an invoice.</p>
    </div>
  </div>
</div></section>

<section class="section-sm panel-alt"><div class="container split">
  <div>
    <span class="eyebrow">Why OnceMore</span>
    <h2>Built for how search <em>works now.</em></h2>
    <p>Search is splitting between Google's results and AI answer engines. We work across both, so your business stays visible no matter where your customers look.</p>
  </div>
  <ul class="feature-list">
    <li>Clear reporting you can read, not jargon</li>
    <li>Work grounded in real data, not guesswork</li>
    <li>One team across SEO, content and paid</li>
    <li>Focused on Malaysian businesses and audiences</li>
  </ul>
</div></section>
"""
home_body = (home_body
    .replace("HERO_SVG_PLACEHOLDER", HERO_SVG)
    .replace("CLIENTS_MARQUEE", CLIENTS_HTML)
    .replace("CAPABILITY_PILLS", capability_pills)
    .replace("BENTO_CARDS", bento_cards)
    .replace("PROCESS_CARDS", process_cards)
)

home_faq_items = [
    ("What does OnceMore Digital do?",
     "We help businesses in Malaysia grow online through SEO, GEO, AI optimisation, content writing and Google Ads."),
    ("Where are you based?",
     "We work with businesses across Malaysia and can support clients remotely."),
    ("How do I get started?",
     "Email walter@oncemoredigital.com or use the contact page, and we will set up a short call to understand your goals."),
]
home_faq_html, home_faq_schema = faq_block(home_faq_items)
home_body += home_faq_html

home_body += """
<section class="section cta-final"><div class="container">
  <div class="cta-band">
    <h2>Ready to get found?</h2>
    <p>Tell us what you are working on and we will be in touch.</p>
    <div class="btn-row"><a class="btn btn-primary" href="/contact/">Start the conversation</a></div>
  </div>
</div></section>
"""

home_schema = [
    jsonld({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "OnceMore Digital",
        "url": URL,
        "email": EMAIL,
        "logo": URL + "/oncemoredigial-seo-marketing-logo.jpg",
        "description": "SEO, GEO, AI optimisation, content writing and Google Ads for businesses in Malaysia.",
        "areaServed": {"@type": "Country", "name": "Malaysia"},
        "address": ADDRESS,
        "identifier": "LLP0046284-LGN",
    }),
    jsonld({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "OnceMore Digital",
        "url": URL,
    }),
    jsonld({
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": "OnceMore Digital",
        "description": "SEO, GEO, AI Optimisation, Content Writing and Google Ads for Malaysian businesses",
        "url": URL,
        "email": EMAIL,
        "image": OG_IMAGE,
        "areaServed": {"@type": "Country", "name": "Malaysia"},
        "knowsAbout": ["SEO", "Search Engine Optimisation", "GEO",
                       "Generative Engine Optimisation", "AI Optimisation",
                       "Content Writing", "Google Ads", "Digital Marketing"],
    }),
    home_faq_schema,
]

page("/", "OnceMore Digital | SEO, GEO &amp; AI Optimisation in Malaysia",
     "OnceMore Digital helps Malaysian businesses rank higher on Google, get found in AI search, and grow organically. SEO, GEO, AI optimisation, content writing and Google Ads.",
     home_body, active="home", schema_blocks=home_schema)

# ---------------------------------------------------------------- services hub
hub_cards = "".join(card_html(s[0], s[1], s[3]) for s in SERVICES)
hub_body = """
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Services</nav>
  <span class="eyebrow" style="margin-top:1.5rem">Services</span>
  <h1>Everything you need to <em>get found.</em></h1>
  <p class="lead">From classic search rankings to AI answer engines, here is how we help your business grow.</p>
  <div class="grid" style="margin-top:2.5rem">%s</div>
</div></section>
<section class="section-sm"><div class="container">
  <div class="cta-band">
    <h2>Not sure where to start?</h2>
    <p>Tell us about your business and we will point you to the right place.</p>
    <div class="btn-row"><a class="btn btn-primary" href="/contact/">Get in Touch</a></div>
  </div>
</div></section>
""" % hub_cards

hub_schema = [
    breadcrumb([("Home", "/"), ("Services", "/services/")]),
    jsonld({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": s[2],
             "url": URL + "/services/%s/" % s[0]}
            for i, s in enumerate(SERVICES)
        ],
    }),
]
page("/services/", "Services | SEO, GEO, AI Optimisation, Content &amp; Google Ads",
     "Our digital marketing services for Malaysian businesses: SEO, GEO, AI optimisation, content writing and Google Ads. One team across organic and paid growth.",
     hub_body, active="services", schema_blocks=hub_schema)

# ---------------------------------------------------------------- service pages
for slug, short, full_name, tagline, intro, features, faqs in SERVICES:
    others = "".join(card_html(s[0], s[1], s[3]) for s in SERVICES if s[0] != slug)
    fl = "".join("<li>%s</li>" % f for f in features)
    extra = SERVICE_CONTENT.get(slug, {})
    sections_html = "".join(
        '<h2 style="margin-top:2.25rem">%s</h2>%s' % (html.escape(h), b)
        for h, b in extra.get("sections", []))
    process = extra.get("process")
    if process:
        proc_cards = "".join(
            '<div class="card"><span class="num">%02d</span><h3>%s</h3><p>%s</p></div>'
            % (i + 1, html.escape(step_title), step_body)
            for i, (step_title, step_body) in enumerate(process["steps"]))
        process_html = (
            '<h2 style="margin-top:2.5rem">%s</h2>'
            '<p class="lead" style="font-size:1.05rem;max-width:62ch;margin-bottom:1.75rem">%s</p>'
            '<div class="grid">%s</div>'
            % (html.escape(process["heading"]), html.escape(process["intro"]), proc_cards)
        )
    else:
        process_html = ""
    all_faqs = list(faqs) + extra.get("faqs", [])
    faq_html, faq_schema = faq_block(all_faqs)
    related_guides = "".join(
        '<li><a href="/resources/%s/">%s</a></li>' % (g["slug"], html.escape(g["title"]))
        for g in RESOURCES)
    body = f"""
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/services/">Services</a> / {short}</nav>
  <div class="svc-icon">{ICONS[slug]}</div>
  <span class="eyebrow" style="margin-top:0">{html.escape(full_name)}</span>
  <h1>{html.escape(short)}</h1>
  <p class="lead">{html.escape(tagline)}</p>
  <div class="divider left" aria-hidden="true"></div>
  <div class="prose">
    <p>{html.escape(intro)}</p>
    {sections_html}
  </div>
  {process_html}
  <h2 style="margin-top:2.5rem">What is included</h2>
  <ul class="feature-list">{fl}</ul>
  <div class="btn-row" style="justify-content:flex-start;margin-top:1.5rem">
    <a class="btn btn-primary" href="/contact/">Enquire about {html.escape(short)}</a>
  </div>
</div></section>
{faq_html}
<section class="section-sm"><div class="container">
  <span class="eyebrow">Related reading</span>
  <h2>Go deeper</h2>
  <ul class="link-list">{related_guides}</ul>
</div></section>
<section class="section-sm"><div class="container">
  <span class="eyebrow">More services</span>
  <h2>Explore the rest</h2>
  <div class="grid" style="margin-top:1.5rem">{others}</div>
</div></section>
"""
    schema = [
        breadcrumb([("Home", "/"), ("Services", "/services/"), (short, "/services/%s/" % slug)]),
        jsonld({
            "@context": "https://schema.org",
            "@type": "Service",
            "name": full_name,
            "serviceType": full_name,
            "description": tagline,
            "url": URL + "/services/%s/" % slug,
            "areaServed": {"@type": "Country", "name": "Malaysia"},
            "provider": {"@type": "Organization", "name": "OnceMore Digital", "url": URL},
        }),
        faq_schema,
    ]
    page("/services/%s/" % slug,
         f"{short} Services in Malaysia | OnceMore Digital",
         f"{tagline} {full_name} for Malaysian businesses from OnceMore Digital.",
         body, active="services", schema_blocks=schema)

# ---------------------------------------------------------------- about
about_body = """
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / About</nav>
  <span class="eyebrow" style="margin-top:1.5rem">About</span>
  <h1>A search partner built for <em>what comes next.</em></h1>
  <p class="lead">OnceMore Digital helps businesses in Malaysia grow through search, whether that search happens on Google or inside an AI answer engine.</p>
  <div class="divider left" aria-hidden="true"></div>
  <p style="max-width:65ch">The way people find businesses is changing. Some still type into Google. More are starting to ask AI tools for a recommendation. We work across both, combining solid SEO fundamentals with newer GEO and AI optimisation work, so your visibility holds up as habits shift.</p>
  <p style="max-width:65ch;margin-top:1rem">We keep things straight. Recommendations are grounded in real data, reporting is written to be understood, and we tell you what is worth doing rather than selling work for its own sake.</p>
  <h2 style="margin-top:2.5rem">How we work</h2>
  <ul class="feature-list">
    <li>Understand your business and your customers first</li>
    <li>Map the searches and questions that matter</li>
    <li>Fix the foundations before chasing growth</li>
    <li>Measure honestly and adjust as we learn</li>
  </ul>
  <div class="btn-row" style="justify-content:flex-start;margin-top:1.5rem">
    <a class="btn btn-primary" href="/contact/">Work with us</a>
  </div>
</div></section>
""" + CLIENTS_HTML
about_schema = [
    breadcrumb([("Home", "/"), ("About", "/about/")]),
    jsonld({
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "name": "About OnceMore Digital",
        "url": URL + "/about/",
        "about": {"@type": "Organization", "name": "OnceMore Digital", "url": URL},
    }),
]
page("/about/", "About | OnceMore Digital",
     "OnceMore Digital is a search partner for Malaysian businesses, working across SEO, GEO and AI optimisation to keep you visible as search habits change.",
     about_body, active="about", schema_blocks=about_schema)

# ---------------------------------------------------------------- contact
contact_body = """
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Contact</nav>
  <span class="eyebrow" style="margin-top:1.5rem">Contact</span>
  <h1>Let's get you <em>found.</em></h1>
  <p class="lead">Tell us what you are working on and we will get back to you.</p>
  <div class="divider left" aria-hidden="true"></div>
  <div class="contact-grid" style="margin-top:1rem">
    <div>
      <form id="contact-form" novalidate>
        <div class="field"><label for="name">Name</label><input id="name" name="name" type="text" autocomplete="name" required></div>
        <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required></div>
        <div class="field"><label for="message">How can we help?</label><textarea id="message" name="message" required></textarea></div>
        <button class="btn btn-primary" type="submit">Send message</button>
      </form>
    </div>
    <div>
      <h3>Prefer email?</h3>
      <p style="margin-bottom:1.25rem">Reach us directly any time.</p>
      <p><a href="mailto:%s">%s</a></p>
      <h3 style="margin-top:2rem">Where we work</h3>
      <p>We work with businesses across Malaysia. Our office:</p>
      <address class="office-address">BO1-A-9, Menara 2, KL Eco City,<br>3, Jln Bangsar, 59200 Kuala Lumpur, Malaysia</address>
    </div>
  </div>
</div></section>
""" % (EMAIL, EMAIL)
contact_schema = [
    breadcrumb([("Home", "/"), ("Contact", "/contact/")]),
    jsonld({
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": "Contact OnceMore Digital",
        "url": URL + "/contact/",
    }),
    jsonld({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "OnceMore Digital",
        "url": URL,
        "email": EMAIL,
        "contactPoint": {"@type": "ContactPoint", "email": EMAIL,
                         "contactType": "customer service", "areaServed": "MY"},
        "address": ADDRESS,
        "identifier": "LLP0046284-LGN",
    }),
]
page("/contact/", "Contact | OnceMore Digital",
     "Get in touch with OnceMore Digital. Email walter@oncemoredigital.com or send a message and we will be in touch about your SEO, GEO and digital marketing goals.",
     contact_body, active="contact", schema_blocks=contact_schema)

# ---------------------------------------------------------------- resources
for g in RESOURCES:
    def _sid(h):
        return re.sub(r'[^a-z0-9]+', '-', h.lower()).strip('-')
    secs = g["body"]
    toc = "".join('<li><a href="#%s">%s</a></li>' % (_sid(h), html.escape(h)) for h, _ in secs)
    body_sections = "".join(
        '<h2 id="%s">%s</h2>%s' % (_sid(h), html.escape(h), b) for h, b in secs)
    tldr = "".join("<li>%s</li>" % html.escape(x) for x in g["tldr"])
    g_faq_html, g_faq_schema = faq_block(g["faqs"])
    related = "".join(
        '<li><a href="/resources/%s/">%s</a></li>' % (o["slug"], html.escape(o["title"]))
        for o in RESOURCES if o["slug"] != g["slug"])
    gbody = f"""
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/resources/">Resources</a> / {html.escape(g["title"])}</nav>
  <span class="eyebrow" style="margin-top:1.25rem">{html.escape(g["eyebrow"])}</span>
  <h1>{html.escape(g["h1"])}</h1>
  <p class="updated">Updated {UPDATED}</p>
  <div class="answer-box">
    <span class="answer-label">Short answer</span>
    <p>{html.escape(g["answer"])}</p>
  </div>
  <nav class="toc" aria-label="On this page">
    <p class="toc-title">On this page</p>
    <ul>{toc}</ul>
  </nav>
  <article class="prose">
    {body_sections}
  </article>
  <div class="tldr">
    <h2>TL;DR</h2>
    <ul>{tldr}</ul>
  </div>
  <div class="author-bio">
    <p><strong>Written by the OnceMore Digital team.</strong> We work on SEO, GEO, AI optimisation, content and Google Ads for brands across Malaysia.</p>
  </div>
  <div class="btn-row" style="justify-content:flex-start;margin-top:1.75rem">
    <a class="btn btn-primary" href="/contact/">Talk to us about this</a>
  </div>
</div></section>
{g_faq_html}
<section class="section-sm"><div class="container">
  <span class="eyebrow">Keep reading</span>
  <h2>More guides</h2>
  <ul class="link-list">{related}</ul>
</div></section>
"""
    gschema = [
        breadcrumb([("Home", "/"), ("Resources", "/resources/"),
                    (g["title"], "/resources/%s/" % g["slug"])]),
        jsonld({
            "@context": "https://schema.org", "@type": "Article",
            "headline": g["title"], "description": g["desc"],
            "url": URL + "/resources/%s/" % g["slug"],
            "inLanguage": "en-MY",
            "datePublished": "2026-06-10", "dateModified": "2026-06-10",
            "author": {"@type": "Organization", "name": "OnceMore Digital", "url": URL},
            "publisher": {"@type": "Organization", "name": "OnceMore Digital",
                          "logo": {"@type": "ImageObject", "url": OG_IMAGE}},
        }),
        g_faq_schema,
    ]
    page("/resources/%s/" % g["slug"], "%s | OnceMore Digital" % g["title"], g["desc"],
         gbody, active="resources", schema_blocks=gschema)

# resources hub
res_cards = "".join(
    '<a class="card" href="/resources/%s/"><span class="icon">%s</span><h3>%s</h3><p>%s</p><span class="more">Read guide &rarr;</span></a>'
    % (g["slug"], GUIDE_ICONS.get(g["slug"], ICONS["content-writing"]),
       html.escape(g["title"]), html.escape(g["desc"])) for g in RESOURCES)
res_hub_body = """
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Resources</nav>
  <span class="eyebrow" style="margin-top:1.5rem">Resources</span>
  <h1>Guides on <em>search, AI and growth.</em></h1>
  <p class="lead">Straight-talking guides on getting found in Malaysia, across both classic search and the AI answer engines that increasingly sit on top of it.</p>
  <div class="grid" style="margin-top:2.5rem">%s</div>
</div></section>
<section class="section-sm"><div class="container"><div class="cta-band">
  <h2>Want this applied to your site?</h2>
  <p>We turn the thinking in these guides into work that moves your rankings and visibility.</p>
  <div class="btn-row"><a class="btn btn-primary" href="/contact/">Get in Touch</a></div>
</div></div></section>
""" % res_cards
res_hub_schema = [
    breadcrumb([("Home", "/"), ("Resources", "/resources/")]),
    jsonld({"@context": "https://schema.org", "@type": "CollectionPage",
            "name": "Resources", "url": URL + "/resources/",
            "hasPart": [{"@type": "Article", "headline": g["title"],
                         "url": URL + "/resources/%s/" % g["slug"]} for g in RESOURCES]}),
]
page("/resources/", "Resources | SEO, GEO &amp; AI Search Guides | OnceMore Digital",
     "Straight-talking guides on SEO, GEO and AI search for Malaysian businesses, from OnceMore Digital.",
     res_hub_body, active="resources", schema_blocks=res_hub_schema)

# ---------------------------------------------------------------- 404
nf_body = """
<section class="section"><div class="container" style="text-align:center">
  <span class="eyebrow" style="justify-content:center">Error 404</span>
  <h1>This page took a <em>wrong turn.</em></h1>
  <p class="lead" style="margin:0 auto 2rem">The page you are looking for does not exist or has moved.</p>
  <div class="btn-row"><a class="btn btn-primary" href="/">Back to home</a><a class="btn btn-ghost" href="/services/">See our services</a></div>
</div></section>
"""
# 404.html must sit at site root
canonical_404 = page("/404-tmp/", "Page not found | OnceMore Digital",
                      "The page you are looking for does not exist.",
                      nf_body)
os.replace(canonical_404, os.path.join(SITE, "404.html"))
os.rmdir(os.path.join(SITE, "404-tmp"))

print("HTML pages written.")
for root, _, files in os.walk(SITE):
    for fn in sorted(files):
        if fn.endswith(".html"):
            print(" ", os.path.relpath(os.path.join(root, fn), SITE))
