"""Builds the OnceMore Digital static site.
Each page gets its own title, meta description, canonical, Open Graph,
Twitter card and JSON-LD schema. GTM and the og:image path are preserved
exactly from the original markup. Output is plain static HTML for GitHub Pages.
"""
import os, json, html, re
from content import SERVICE_CONTENT, RESOURCES, CASE_STUDIES

SITE = "/home/claude/site"
URL = "https://oncemoredigital.com"
EMAIL = "walter@oncemoredigital.com"
GTM = "GTM-MJ5WCPR6"
UPDATED = "July 2026"
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
      </ul>
    </li>
    <li><a href="/resources/"{resources}>Resources</a></li>
    <li><a href="/case-studies/"{case_studies}>Case Studies</a></li>
    <li><a href="/about/"{about}>About</a></li>
    <li><a href="/contact/"{contact}>Contact</a></li>
    <li><a class="nav-cta" href="mailto:%s">Get in Touch</a></li>
  </ul>
</nav></div></header>""" % EMAIL

SOCIAL_LINKS = [
    ("Instagram", "https://www.instagram.com/oncemoredigital/",
     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.9" fill="currentColor" stroke="none"/></svg>'),
    ("LinkedIn", "https://www.linkedin.com/company/oncemore-digital-services/",
     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="7.5" cy="7" r="0.9" fill="currentColor" stroke="none"/><line x1="7.5" y1="10.5" x2="7.5" y2="17"/><path d="M11.5 17v-4.3c0-1.4 1-2.4 2.2-2.4s2.1 1 2.1 2.4V17"/><line x1="11.5" y1="10.5" x2="11.5" y2="17"/></svg>'),
]
SOCIAL_ICONS_HTML = "".join(
    '<a href="%s" aria-label="%s" target="_blank" rel="noopener">%s</a>' % (url, name, svg)
    for name, url, svg in SOCIAL_LINKS
)

FOOTER = """<footer class="site-footer"><div class="container">
  <div class="footer-grid">
    <div class="footer-brand">
      <a class="brand" href="/"><img src="/assets/img/logo-wordmark.png" alt="OnceMore Digital" class="brand-logo footer-logo"></a>
      <p>SEO, GEO, AI optimisation and content for businesses in Malaysia.</p>
      <address class="footer-address">BO1-A-9, Menara 2, KL Eco City,<br>3, Jln Bangsar, 59200 Kuala Lumpur, Malaysia</address>
      <p class="footer-ssm">SSM: 202604001053 (LLP0046284-LGN)</p>
      <div class="social-icons">SOCIAL_ICONS_PLACEHOLDER</div>
    </div>
    <div>
      <h4><a href="/services/">Services</a></h4>
      <ul>
        <li><a href="/services/seo/">SEO</a></li>
        <li><a href="/services/geo/">GEO</a></li>
        <li><a href="/services/ai-optimisation/">AI Optimisation</a></li>
        <li><a href="/services/content-writing/">Content Writing</a></li>
      </ul>
    </div>
    <div class="footer-stack">
      <h4><a href="/resources/">Resources</a></h4>
      <h4><a href="/case-studies/">Case Studies</a></h4>
    </div>
    <div>
      <h4>Company</h4>
      <ul>
        <li><a href="/about/">About Us</a></li>
        <li><a href="/contact/">Contact Us</a></li>
        <li><a href="/sitemap/">Sitemap</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">&copy; 2026 OnceMore Digital Services. All rights reserved.</div>
</div></footer>"""
FOOTER = FOOTER.replace("SOCIAL_ICONS_PLACEHOLDER", SOCIAL_ICONS_HTML)


def nav_for(active):
    cur = ' aria-current="page"'
    return NAV.format(
        home=cur if active == "home" else "",
        services=cur if active == "services" else "",
        resources=cur if active == "resources" else "",
        case_studies=cur if active == "case-studies" else "",
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


# ---------------------------------------------------------------- floating shapes
# A single fixed-position layer of square-motif shapes (derived from the logo
# mark) that drifts continuously from the bottom of the viewport to the top,
# independent of scroll or which section is in view. Added once per page via
# the shared page() template below, so every page gets the same treatment.
# Balanced left/right, varied shapes, durations and negative delays so they
# do not all move in lockstep.
_RISE_SHAPES = [
    # (classes, side, offset, duration_s, delay_s)
    ("motif motif-sq motif-rise",              "left",  "5%",  42, -7),
    ("motif motif-grid motif-rise",             "left",  "13%", 50, -33),
    ("motif motif-diamond motif-rise is-diamond","left", "22%", 58, -12),
    ("motif motif-mini motif-rise",             "left",  "33%", 38, -18),
    ("motif motif-sq alt motif-rise",           "left",  "42%", 48, -25),
    ("motif motif-diamond outline motif-rise is-diamond","right","8%", 55, -21),
    ("motif motif-mini motif-rise",             "right", "18%", 34, -4),
    ("motif motif-sq outline motif-rise",       "right", "28%", 52, -39),
    ("motif motif-grid motif-rise",             "right", "38%", 44, -3),
    ("motif motif-diamond motif-rise is-diamond","right", "46%", 56, -29),
]

def _rise_shape_html(classes, side, offset, duration, delay):
    grid_inner = "<span></span><span></span><span></span><span></span>" if "motif-grid" in classes else ""
    return ('<div class="%s" style="%s:%s;animation-duration:%ss;animation-delay:%ss">%s</div>'
            % (classes, side, offset, duration, delay, grid_inner))

SHAPE_LAYER_HTML = ('<div class="shape-layer" aria-hidden="true">'
                     + "".join(_rise_shape_html(*s) for s in _RISE_SHAPES)
                     + '</div>')


def page(path, title, desc, body, active="", schema_blocks=None):
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
{SHAPE_LAYER_HTML}
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
     "Our SEO services map the keywords that bring qualified traffic, fix the technical SEO issues holding your site back, and build content and links that earn organic rankings over time. Search Engine Optimisation is a compounding investment, and the focus is steady organic growth, not quick wins that fade.",
     ["Keyword research and content mapping",
      "Technical SEO audits and site health fixes",
      "On-page SEO optimisation for target pages",
      "Local SEO and Google Business Profile",
      "Monthly SEO reporting you can actually read"],
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
]

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
}

def card_html(slug, name, tagline):
    return ('<a class="card" href="/services/%s/"><span class="icon">%s</span>'
            '<h3>%s</h3><p>%s</p><span class="more">Learn more &rarr;</span></a>'
            % (slug, ICONS[slug], name, tagline))

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
        '<div class="logo-chip"><img src="/assets/img/clients/%s" alt="%s logo" decoding="async"></div>'
        % (f, a) for f, a in CLIENT_LOGOS)
    track = chips + chips  # duplicated for a seamless loop
    return ('<section class="section-sm clients"><div class="container">'
            '<div class="clients-head"><span class="eyebrow">Clients</span>'
            '<h2>Brands we have worked with</h2></div>'
            '<div class="logos" aria-label="Logos of brands we have worked with">'
            '<div class="logos-track">%s</div></div>'
            '</div></section>') % track

CLIENTS_HTML = clients_marquee()

# Sparse decorative shape fields (2 motifs each) for page hero/intro sections
# site-wide. Kept deliberately light, alternated for variety across templates.

# Chart images now live per case study in CASE_STUDIES[i]["charts"]
# as (image_path, alt_text, caption) tuples, since different case studies
# have different numbers of supporting screenshots.

# ---------------------------------------------------------------- guide visuals
# a small ringgit-tag icon for the cost guide card
_TAG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M20 12l-8 8-9-9V3h8z"/>'
        '<circle cx="7.5" cy="7.5" r="1.4"/></svg>')
_PIN = ('<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M16 4c-4.4 0-8 3.4-8 8 0 6 8 16 8 16s8-10 8-16c0-4.6-3.6-8-8-8z"/>'
        '<circle cx="16" cy="12" r="3"/></svg>')
GUIDE_ICONS = {
    "seo-guide-malaysia": ICONS["seo"],
    "what-is-geo": ICONS["geo"],
    "seo-cost-malaysia": _TAG,
    "local-seo-malaysia": _PIN,
}

# ---------------------------------------------------------------- service page illustrations
# The approved concept icons (browser mockup + bespoke content per service),
# kept pixel-for-pixel as designed. class="hero-illustration" + the
# service-hero-grid/.hero-media CSS gives them the same placement and size
# as the homepage hero illustration (big, beside the copy, no dead space).
SERVICE_ILLO = {
    "seo": '''<svg class="hero-illustration" viewBox="0 0 300 300" role="img" aria-label="Browser mockup with a magnifying glass and ascending bars">
<defs><clipPath id="c1"><rect x="0" y="0" width="300" height="300" rx="28"/></clipPath></defs>
<g clip-path="url(#c1)">
<rect x="0" y="0" width="300" height="300" fill="#262b40"/>
<rect x="0" y="0" width="300" height="64" fill="#1c2033"/>
<circle cx="28" cy="32" r="6" fill="#e0b23c"/><circle cx="48" cy="32" r="6" fill="#7a90c7"/><circle cx="68" cy="32" r="6" fill="#4d65af"/>
<rect x="90" y="20" width="180" height="24" rx="12" fill="rgba(255,255,255,0.08)"/>
<circle cx="88" cy="152" r="34" stroke="#7a90c7" stroke-width="11" fill="none"/>
<line x1="113" y1="177" x2="148" y2="212" stroke="#7a90c7" stroke-width="11" stroke-linecap="round"/>
<rect x="176" y="230" width="24" height="40" rx="4" fill="#3a4e8f"/>
<rect x="206" y="200" width="24" height="70" rx="4" fill="#4d65af"/>
<rect x="236" y="165" width="24" height="105" rx="4" fill="#7a90c7"/>
<rect x="266" y="130" width="24" height="140" rx="4" fill="#e0b23c"/>
</g>
<rect x="1" y="1" width="298" height="298" rx="27" fill="none" stroke="rgba(122,144,199,0.35)"/>
</svg>''',
    "geo": '''<svg class="hero-illustration" viewBox="0 0 300 300" role="img" aria-label="Browser mockup with a chat bubble, a spark badge, and a citation checkmark">
<defs><clipPath id="c2"><rect x="0" y="0" width="300" height="300" rx="28"/></clipPath></defs>
<g clip-path="url(#c2)">
<rect x="0" y="0" width="300" height="300" fill="#262b40"/>
<rect x="0" y="0" width="300" height="64" fill="#1c2033"/>
<circle cx="28" cy="32" r="6" fill="#e0b23c"/><circle cx="48" cy="32" r="6" fill="#7a90c7"/><circle cx="68" cy="32" r="6" fill="#4d65af"/>
<rect x="90" y="20" width="180" height="24" rx="12" fill="rgba(255,255,255,0.08)"/>
<rect x="26" y="96" width="140" height="88" rx="20" fill="#3a4e8f"/>
<path d="M42 184 L42 206 L66 184 Z" fill="#3a4e8f"/>
<path d="M196 82 L204 102 L224 110 L204 118 L196 138 L188 118 L168 110 L188 102 Z" fill="#e0b23c"/>
<rect x="168" y="158" width="106" height="76" rx="14" fill="#1c2033" stroke="#4d65af" stroke-width="3"/>
<path d="M190 196 L202 208 L228 178" stroke="#f4f4f2" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</g>
<rect x="1" y="1" width="298" height="298" rx="27" fill="none" stroke="rgba(122,144,199,0.35)"/>
</svg>''',
    "ai-optimisation": '''<svg class="hero-illustration" viewBox="0 0 300 300" role="img" aria-label="Browser mockup with a bracket and three checked rows">
<defs><clipPath id="c3"><rect x="0" y="0" width="300" height="300" rx="28"/></clipPath></defs>
<g clip-path="url(#c3)">
<rect x="0" y="0" width="300" height="300" fill="#262b40"/>
<rect x="0" y="0" width="300" height="64" fill="#1c2033"/>
<circle cx="28" cy="32" r="6" fill="#e0b23c"/><circle cx="48" cy="32" r="6" fill="#7a90c7"/><circle cx="68" cy="32" r="6" fill="#4d65af"/>
<rect x="90" y="20" width="180" height="24" rx="12" fill="rgba(255,255,255,0.08)"/>
<path d="M72 92 C52 92 47 102 47 117 V140 C47 150 42 155 32 158 C42 161 47 166 47 176 V199 C47 214 52 224 72 224" stroke="#7a90c7" stroke-width="9" fill="none" stroke-linecap="round"/>
<rect x="104" y="98" width="172" height="36" rx="9" fill="#1c2033" stroke="rgba(122,144,199,0.5)" stroke-width="2"/>
<circle cx="122" cy="116" r="12" fill="#e0b23c"/><path d="M116 116l4 5 9-10" stroke="#1c2033" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="104" y="148" width="172" height="36" rx="9" fill="#1c2033" stroke="rgba(122,144,199,0.5)" stroke-width="2"/>
<circle cx="122" cy="166" r="12" fill="#4d65af"/><path d="M116 166l4 5 9-10" stroke="#f4f4f2" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="104" y="198" width="172" height="36" rx="9" fill="#1c2033" stroke="rgba(122,144,199,0.5)" stroke-width="2"/>
<circle cx="122" cy="216" r="12" fill="#4d65af"/><path d="M116 216l4 5 9-10" stroke="#f4f4f2" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</g>
<rect x="1" y="1" width="298" height="298" rx="27" fill="none" stroke="rgba(122,144,199,0.35)"/>
</svg>''',
    "content-writing": '''<svg class="hero-illustration" viewBox="0 0 300 300" role="img" aria-label="Browser mockup with a document, text lines, and a large pencil">
<defs><clipPath id="c4"><rect x="0" y="0" width="300" height="300" rx="28"/></clipPath></defs>
<g clip-path="url(#c4)">
<rect x="0" y="0" width="300" height="300" fill="#262b40"/>
<rect x="0" y="0" width="300" height="64" fill="#1c2033"/>
<circle cx="28" cy="32" r="6" fill="#e0b23c"/><circle cx="48" cy="32" r="6" fill="#7a90c7"/><circle cx="68" cy="32" r="6" fill="#4d65af"/>
<rect x="90" y="20" width="180" height="24" rx="12" fill="rgba(255,255,255,0.08)"/>
<rect x="46" y="92" width="132" height="172" rx="12" fill="#1c2033" stroke="#7a90c7" stroke-width="3"/>
<path d="M154 92 L178 92 L178 116 Z" fill="#7a90c7"/>
<rect x="62" y="120" width="100" height="11" rx="5" fill="#4d65af"/>
<rect x="62" y="146" width="88" height="11" rx="5" fill="#3a4e8f"/>
<rect x="62" y="172" width="100" height="11" rx="5" fill="#4d65af"/>
<rect x="62" y="198" width="70" height="11" rx="5" fill="#3a4e8f"/>
<g transform="translate(214,222) rotate(-45)">
<rect x="-42" y="-11" width="70" height="22" rx="5" fill="#e0b23c"/>
<path d="M28 -11 L46 0 L28 11 Z" fill="#e0b23c"/>
</g>
</g>
<rect x="1" y="1" width="298" height="298" rx="27" fill="none" stroke="rgba(122,144,199,0.35)"/>
</svg>''',
}

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
    card_html(s[0], s[1], s[3]) for s in SERVICES
)

process_cards = "".join(
    '<div class="process-step"><span class="dot">%02d</span><h3>%s</h3><p>%s</p></div>'
    % (i + 1, html.escape(t), html.escape(b))
    for i, (t, b) in enumerate(PROCESS_STEPS)
)

home_body = """
<section class="hero"><div class="container">
  <div class="hero-grid">
    <div class="hero-copy">
      <span class="eyebrow">Digital Marketing Agency in Malaysia</span>
      <h1>Helping businesses<br>get found <em>online.</em></h1>
      <p class="lead">OnceMore Digital is a Kuala Lumpur based digital marketing agency and SEO agency helping businesses across Malaysia rank on Google, show up in AI search results, and grow organically through smart SEO, content and strategy.</p>
      <div class="services-tags" role="list" aria-label="Our services">
        <span class="service-tag" role="listitem">SEO</span>
        <span class="service-tag" role="listitem">GEO</span>
        <span class="service-tag" role="listitem">AI Optimisation</span>
        <span class="service-tag" role="listitem">Content Writing</span>
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

<section class="section"><div class="container">
  <span class="eyebrow">Who we are</span>
  <h2>A Malaysian-led digital marketing agency, built on direct access.</h2>
  <p style="max-width:65ch">OnceMore Digital is a Malaysian-led digital marketing agency, with a team bringing a combined 10+ years of hands-on experience across SEO, GEO, AI optimisation and content. That experience covers everything from independent local businesses to established international brands, and the same standard applies to each.</p>
  <p style="max-width:65ch;margin-top:1rem">Being Malaysian-led means Malaysian search behaviour, language and local intent are the starting point, not an afterthought layered on top of a global template. Our focus has always been on helping local businesses compete and win visibility in their own market, though the same expertise applies just as well to international brands entering it.</p>
  <p style="max-width:65ch;margin-top:1rem">Our biggest strength is simple: the person you talk to about your strategy is the person actually doing the work. No hand-offs, no account managers relaying messages from someone else.</p>
  <div class="btn-row" style="justify-content:flex-start;margin-top:1.5rem">
    <a class="btn btn-ghost" href="/about/">Read more about us</a>
  </div>
</div></section>

<section class="section"><div class="container">
  <span class="eyebrow">Digital Marketing Agency in Malaysia</span>
  <h2>What a digital marketing agency should <em>actually do.</em></h2>
  <p>A good digital marketing agency brings SEO, GEO, AI optimisation and content together under one strategy, so every channel works toward the same goal instead of being managed in isolation.</p>
  <p style="margin-top:1rem">OnceMore Digital started as an SEO agency, and SEO is still the foundation of most engagements we run. As search itself has changed, we have grown into a full digital marketing agency covering SEO, GEO, AI optimisation and content, all handled by the same team.</p>
</div></section>

<section class="section panel-alt"><div class="container">
  <div class="split">
    <div>
      <span class="eyebrow">Why OnceMore</span>
      <h2>Built for how search <em>works now.</em></h2>
      <p>Search is splitting between Google's results and AI answer engines. We work across both, so your business stays visible no matter where your customers look.</p>
      <p>Most SEO agencies still treat search as the only channel that matters. We built OnceMore, a digital marketing agency that blends SEO, GEO and AI optimisation from the start, not bolted on later as an afterthought.</p>
    </div>
    <div class="illustration-frame"><img src="/assets/img/illustrations/social-search-behaviour.svg" alt="Illustration of a person browsing search results and social profiles" loading="lazy" decoding="async"></div>
  </div>
  <ul class="feature-list" style="margin-top:2rem">
    <li>Clear reporting you can read, not jargon</li>
    <li>Work grounded in real data, not guesswork</li>
    <li>One team across SEO, content and paid</li>
    <li>Focused on Malaysian businesses and audiences</li>
    <li>Straight answers about what is and is not working</li>
    <li>Strategy adjusted monthly, not locked in for a year</li>
  </ul>
</div></section>

<section class="section"><div class="container">
  <span class="eyebrow">What we do</span>
  <h2>Five ways we help you grow</h2>
  <p>Each service stands on its own or works together as one organic growth plan. SEO is where most engagements start.</p>
  <div class="grid" style="margin-top:2rem">
    BENTO_CARDS
  </div>
</div></section>

<section class="section"><div class="container">
  <span class="eyebrow">Who we help</span>
  <h2>Malaysian businesses across <em>every industry we touch.</em></h2>
  <p>As a digital marketing agency, we adapt strategy to how each industry's customers actually search, not a one size fits all template.</p>
  <div class="grid" style="margin-top:2rem">
    <div class="card"><h3>Retail &amp; FMCG</h3><p>Product and category pages built to rank for what shoppers search before they buy, not just brand terms.</p></div>
    <div class="card"><h3>Education</h3><p>Programme and enrolment pages that answer the questions parents and students actually type into Google.</p></div>
    <div class="card"><h3>Financial &amp; public sector</h3><p>Content and technical SEO built to the standard that regulated, high-trust organisations need.</p></div>
    <div class="card"><h3>Hospitality &amp; travel</h3><p>Local and national visibility for businesses competing for customers actively comparing options.</p></div>
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

CLIENTS_MARQUEE
"""
home_body = (home_body
    .replace("HERO_SVG_PLACEHOLDER", HERO_SVG)
    .replace("CLIENTS_MARQUEE", CLIENTS_HTML)
    .replace("BENTO_CARDS", bento_cards)
    .replace("PROCESS_CARDS", process_cards)
)

home_faq_items = [
    ("Where are you based?",
     "We work with businesses across Malaysia and can support clients remotely."),
    ("How do I get started?",
     "Email walter@oncemoredigital.com or use the contact page, and we will set up a short call to understand your goals."),
    ("How do I choose an SEO agency in Malaysia?",
     "Look for one that explains its work in plain terms, shows you real reporting, and treats SEO as an ongoing strategy rather than a one-off fix. A good SEO agency should be able to tell you what is not working, not just what is."),
    ("What is the difference between an SEO agency and a digital marketing agency?",
     "An SEO agency focuses specifically on organic search rankings. A digital marketing agency covers a wider range of channels, from SEO to content to AI optimisation. OnceMore started as an SEO agency and has grown into a full digital marketing agency, though SEO remains the foundation of most of our work."),
    ("Do you work with small businesses or only large companies?",
     "Both. Our client base has included large brands and independent local businesses, and the same fundamentals apply to each. What changes is the scope of work, not the standard we hold it to."),
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
        "description": "Digital marketing agency and SEO agency helping businesses in Malaysia with SEO, GEO, AI optimisation and content writing.",
        "areaServed": {"@type": "Country", "name": "Malaysia"},
        "address": ADDRESS,
        "identifier": "LLP0046284-LGN",
        "sameAs": [url for _, url, _ in SOCIAL_LINKS],
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
        "description": "Digital marketing agency and SEO agency in Malaysia covering SEO, GEO, AI Optimisation and Content Writing",
        "url": URL,
        "email": EMAIL,
        "image": OG_IMAGE,
        "areaServed": {"@type": "Country", "name": "Malaysia"},
        "knowsAbout": ["SEO", "Search Engine Optimisation", "GEO",
                       "Generative Engine Optimisation", "AI Optimisation",
                       "Content Writing", "Digital Marketing"],
    }),
    home_faq_schema,
]

page("/", "OnceMore Digital | Digital Marketing Agency &amp; SEO Agency in Malaysia",
     "OnceMore Digital is a digital marketing agency and SEO agency in Malaysia, helping businesses rank higher on Google, get found in AI search, and grow organically through SEO, GEO, AI optimisation and content writing.",
     home_body, active="home", schema_blocks=home_schema)

# ---------------------------------------------------------------- services hub
hub_cards = "".join(card_html(s[0], s[1], s[3]) for s in SERVICES)
hub_body = """
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Services</nav>
  <span class="eyebrow" style="margin-top:1.5rem">Digital Marketing Services in Malaysia</span>
  <h1>Everything you need to <em>get found.</em></h1>
  <p class="lead">From classic search rankings to AI answer engines, here is how our digital marketing services help improve your website traffic and grow your business online.</p>
  <div class="divider left" aria-hidden="true"></div>
  <p style="max-width:65ch">Digital marketing covers a lot of ground: ads, social media, email, SEO, and not all of it moves the needle for every business. We focus on the channels that reliably improve website traffic and turn it into enquiries, not vanity numbers that look good in a report and do nothing for revenue.</p>
  <p style="max-width:65ch;margin-top:1rem">Each service below can run on its own, but most businesses see the best results when they work together as one strategy, rather than as four separate vendors pulling in different directions.</p>
  <div class="grid" style="margin-top:2.5rem">%s</div>
</div></section>

<section class="section panel-alt"><div class="container">
  <span class="eyebrow">How it fits together</span>
  <h2>How each service helps improve your <em>website traffic.</em></h2>
  <p style="max-width:65ch">Digital marketing works best when every channel is pulling toward the same goal. Here is what each one is actually doing for your traffic.</p>
  <ul class="feature-list" style="margin-top:1.75rem;max-width:70ch">
    <li><strong>SEO</strong> brings in visitors who are already searching for what you offer, the highest-intent traffic there is.</li>
    <li><strong>GEO</strong> captures the growing share of people who ask AI tools a question instead of searching, before they ever reach a results page.</li>
    <li><strong>AI Optimisation</strong> makes sure the traffic you already get lands on pages structured to convert, not just pages that happen to rank.</li>
    <li><strong>Content Writing</strong> fuels both SEO and GEO with the pages and answers that traffic actually needs to find in the first place.</li>
  </ul>
</div></section>
<section class="section-sm"><div class="container">
  <div class="cta-band">
    <h2>Not sure where to start?</h2>
    <p>Tell us about your business and we will point you to the right place.</p>
    <div class="btn-row"><a class="btn btn-primary" href="/contact/">Get in Touch</a></div>
  </div>
</div></section>
""" % hub_cards

hub_faq_items = [
    ("What is digital marketing?",
     "Digital marketing is the umbrella term for any way a business gets found and grows online, from search engines to social media to paid ads. We focus specifically on the channels proven to improve website traffic and turn it into real enquiries: SEO, GEO, AI optimisation and content."),
    ("How do I find the best digital marketing agency for my business?",
     "Look for one that explains its work in plain terms, is upfront about pricing, and can show you real reporting. The best digital marketing agency for your business is the one that treats your traffic and revenue goals as the point, not the channel mix."),
    ("Which service should I start with to improve website traffic fastest?",
     "For most businesses, SEO is the foundation, since it compounds over time and does not stop the moment you stop paying for it. If you need visibility sooner, pairing it with GEO and AI optimisation from day one prevents having to retrofit that work later."),
    ("How much does digital marketing cost in Malaysia?",
     "It depends on which services you need and how competitive your market is. A proper answer needs a look at your actual goals rather than a generic number, so get in touch and we can give you a clear picture. Our guide on SEO costs in Malaysia breaks down what actually drives the number."),
    ("How long does digital marketing take to show results?",
     "Paid channels can bring traffic within days. Organic channels like SEO, GEO and content marketing take longer to build, usually three to six months for early movement, but the results compound and keep working long after you stop paying for the work itself."),
    ("Do I need SEO, or do I need all four services?",
     "SEO is the right place to start for almost every business, since it is the foundation the other services build on. GEO, AI optimisation and content become worth adding once you want to compete for AI-generated answers and not just the classic results list, or once you need more content than your current SEO work is producing."),
    ("Do you offer digital marketing packages for small businesses?",
     "Yes. We work with businesses of every size, and pricing is matched to your budget and goals rather than a one-size-fits-all number."),
    ("What makes OnceMore Digital different from other digital marketing agencies in Malaysia?",
     "You work directly with the people doing the SEO, content and AI optimisation work, not an account manager relaying messages from someone else. Reporting says what is and is not working, and Malaysian search behaviour, bilingual queries and local intent, shapes the strategy from day one rather than being an afterthought."),
]
hub_faq_html, hub_faq_schema = faq_block(hub_faq_items)
hub_body += hub_faq_html

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
    hub_faq_schema,
]
page("/services/", "Digital Marketing Services in Malaysia | OnceMore Digital",
     "Digital marketing services built to improve website traffic for Malaysian businesses: SEO, GEO, AI optimisation and content writing, all from one team.",
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
        example = process.get("example")
        example_html = (
            '<div class="answer-box" style="margin-top:1.75rem">'
            '<span class="answer-label">%s</span><p>%s</p></div>'
            % (html.escape(example["label"]), html.escape(example["text"]))
        ) if example else ""
        process_html = (
            '<h2 style="margin-top:2.5rem">%s</h2>'
            '<p class="lead" style="font-size:1.05rem;max-width:62ch;margin-bottom:1.75rem">%s</p>'
            '<div class="grid">%s</div>%s'
            % (html.escape(process["heading"]), html.escape(process["intro"]), proc_cards, example_html)
        )
    else:
        process_html = ""
    tools = extra.get("tools")
    if tools:
        tool_cards = "".join(
            '<div class="tool-card">'
            '<div class="tool-logo"><img src="%s" alt="%s logo" loading="lazy"></div>'
            '<h3>%s</h3>'
            '<span class="tool-task">%s</span>'
            '<p>%s</p>'
            '</div>'
            % (logo, html.escape(name), html.escape(name), html.escape(task), html.escape(desc))
            for name, logo, task, desc in tools["items"])
        tools_html = (
            '<section class="section-sm"><div class="container">'
            '<span class="eyebrow">Tools</span>'
            '<h2>%s</h2>'
            '<p class="lead" style="font-size:1.05rem;max-width:62ch;margin-bottom:1.75rem">%s</p>'
            '<div class="tool-grid">%s</div>'
            '<p class="tool-note">%s</p>'
            '</div></section>'
            % (html.escape(tools["heading"]), html.escape(tools["intro"]), tool_cards, html.escape(tools["note"]))
        )
    else:
        tools_html = ""
    all_faqs = list(faqs) + extra.get("faqs", [])
    faq_html, faq_schema = faq_block(all_faqs)
    related_guides = "".join(
        '<li><a href="/resources/%s/">%s</a></li>' % (g["slug"], html.escape(g["title"]))
        for g in RESOURCES)
    body = f"""
<section class="section service-hero"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/services/">Services</a> / {short}</nav>
  <div class="service-hero-grid">
    <div>
      <div class="svc-icon">{ICONS[slug]}</div>
      <span class="eyebrow" style="margin-top:0">{html.escape(full_name)}</span>
      <h1>{html.escape(short)}</h1>
      <p class="lead">{html.escape(tagline)}</p>
      <div class="btn-row" style="justify-content:flex-start;margin-top:.5rem">
        <a class="btn btn-primary" href="/contact/">Enquire about {html.escape(short)}</a>
      </div>
    </div>
    <div class="hero-media" aria-hidden="true">
      {SERVICE_ILLO[slug]}
    </div>
  </div>
</div></section>

<section class="section"><div class="container">
  <div class="divider left" aria-hidden="true"></div>
  <div class="prose">
    <p>{html.escape(intro)}</p>
    {sections_html}
  </div>
  {process_html}
</div></section>

<section class="section-sm panel-alt"><div class="container">
  <span class="eyebrow">What's included</span>
  <h2>Everything in this service</h2>
  <ul class="feature-list">{fl}</ul>
</div></section>
{tools_html}
{faq_html}
<section class="section-sm"><div class="container">
  <span class="eyebrow">Related reading</span>
  <h2>Go deeper</h2>
  <ul class="link-list">{related_guides}</ul>
</div></section>
<section class="section-sm panel-alt"><div class="container">
  <span class="eyebrow">More services</span>
  <h2>Explore the rest</h2>
  <div class="grid" style="margin-top:1.5rem">{others}</div>
</div></section>
<section class="section cta-final"><div class="container">
  <div class="cta-band">
    <h2>Ready to talk about {html.escape(short)}?</h2>
    <p>Tell us about your business and we will map out where this fits.</p>
    <div class="btn-row"><a class="btn btn-primary" href="/contact/">Get in Touch</a></div>
  </div>
</div></section>
"""
    service_schema_dict = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": full_name,
        "serviceType": full_name,
        "description": tagline,
        "url": URL + "/services/%s/" % slug,
        "areaServed": {"@type": "Country", "name": "Malaysia"},
        "provider": {"@type": "Organization", "name": "OnceMore Digital", "url": URL},
    }
    sources = extra.get("sources")
    if sources:
        service_schema_dict["citation"] = [
            {"@type": "CreativeWork", "name": name, "url": src_url}
            for name, src_url in sources
        ]
    schema = [
        breadcrumb([("Home", "/"), ("Services", "/services/"), (short, "/services/%s/" % slug)]),
        jsonld(service_schema_dict),
        faq_schema,
    ]
    page("/services/%s/" % slug,
         extra.get("title") or f"{short} Services in Malaysia | OnceMore Digital",
         extra.get("meta_description") or f"{tagline} {full_name} for Malaysian businesses from OnceMore Digital.",
         body, active="services", schema_blocks=schema)

# ---------------------------------------------------------------- about
ABOUT_VALUES = [
    ("Direct access",
     "You talk to the people actually doing the SEO, content or ads work, not an account manager relaying messages from someone you have never met."),
    ("Malaysia-first thinking",
     "Bilingual search behaviour, local intent and Malaysian buying habits shape the strategy from day one, not a global template with your logo dropped in."),
    ("Honest reporting",
     "Monthly updates say what is and is not working. A quiet dip gets flagged early, not buried until it turns into a bigger problem."),
    ("One team, every channel",
     "SEO, GEO, content and ads sit under the same roof, so nothing gets lost in a handoff between departments or agencies."),
]
about_values_cards = "".join(
    '<div class="card"><h3>%s</h3><p>%s</p></div>' % (html.escape(t), html.escape(b))
    for t, b in ABOUT_VALUES
)

about_body = """
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / About</nav>
  <span class="eyebrow" style="margin-top:1.5rem">About</span>
  <h1>Who Are We Here at <em>OnceMore Digital</em></h1>
  <p class="lead">OnceMore Digital is a small SEO and digital marketing team based in Kuala Lumpur. No rotating account managers, no quietly outsourced work. The people planning your strategy are the same people running it.</p>
  <div class="divider left" aria-hidden="true"></div>
  <p style="max-width:65ch">The way people find businesses is changing. Some still type into Google. More are starting to ask AI tools for a recommendation. We work across both, combining solid SEO fundamentals with newer GEO and AI optimisation work, so your visibility holds up as habits shift.</p>
  <p style="max-width:65ch;margin-top:1rem">We keep things straight. Recommendations are grounded in real data, reporting is written so you can actually understand it, and we tell you what is worth doing rather than selling work for its own sake.</p>
</div></section>

<section class="section panel-alt"><div class="container">
  <div class="split story-split">
    <div class="photo-frame">
      <img src="/assets/img/about/team-meeting.jpg" alt="OnceMore Digital team presenting website traffic data to a client during a strategy session in a Kuala Lumpur meeting room" loading="lazy" decoding="async">
    </div>
    <div>
      <span class="eyebrow">How we work</span>
      <h2>Less deck, more actual conversation.</h2>
      <p>A lot of agencies show you a slide deck once a quarter and go quiet until renewal. We would rather be in the room walking through the numbers with you, which is what most of our client meetings actually look like.</p>
      <p style="margin-top:1rem">Every account gets a monthly call with the people doing the actual work on it, not a summary read back by someone who was not in the room. If something is not working, you hear that directly, along with what we are changing about it.</p>
    </div>
  </div>
</div></section>

<section class="section"><div class="container">
  <span class="eyebrow">Behind the scenes</span>
  <h2>A small team, not a factory.</h2>
  <p style="max-width:65ch">OnceMore Digital is run by a small team, and that is deliberate. We would rather stay small enough that everyone on an account actually knows the business, than grow past the point where your project becomes a ticket in a queue.</p>
  <div class="team-gallery">
    <figure>
      <div class="photo-frame">
        <img src="/assets/img/about/team-office.jpg" alt="OnceMore Digital team members together at the office between client meetings" loading="lazy" decoding="async">
      </div>
    </figure>
    <figure>
      <div class="photo-frame">
        <img src="/assets/img/about/team-outing.jpg" alt="OnceMore Digital team celebrating a completed project together outside the office" loading="lazy" decoding="async">
      </div>
    </figure>
  </div>
</div></section>

<section class="section panel-alt"><div class="container">
  <span class="eyebrow">What matters to us</span>
  <h2>The stuff we will not compromise on.</h2>
  <p style="max-width:65ch">None of this is a mission statement for the wall. It is just what we have found actually matters once you are the one paying for the work.</p>
  <div class="grid" style="margin-top:2rem">%s</div>
</div></section>

CLIENTS_MARQUEE

<section class="section-sm"><div class="container">
  <div class="cta-band">
    <h2>Want to meet the team properly?</h2>
    <p>Tell us about your business and we will set up a call.</p>
    <div class="btn-row"><a class="btn btn-primary" href="/contact/">Get in Touch</a></div>
  </div>
</div></section>
""".replace("CLIENTS_MARQUEE", CLIENTS_HTML) % about_values_cards

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
     "OnceMore Digital is a small SEO and digital marketing team in Kuala Lumpur, working directly with clients across SEO, GEO and AI optimisation.",
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
      <h3 style="margin-top:2rem">Follow us</h3>
      <div class="social-icons">SOCIAL_ICONS_PLACEHOLDER</div>
    </div>
  </div>
</div></section>
""" % (EMAIL, EMAIL)
contact_body = contact_body.replace("SOCIAL_ICONS_PLACEHOLDER", SOCIAL_ICONS_HTML)
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
        "sameAs": [url for _, url, _ in SOCIAL_LINKS],
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
    <p><strong>Written by the OnceMore Digital team.</strong> We work on SEO, GEO, AI optimisation and content for brands across Malaysia.</p>
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
    article_schema_dict = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": g["title"], "description": g["desc"],
        "url": URL + "/resources/%s/" % g["slug"],
        "inLanguage": "en-MY",
        "datePublished": "2026-06-10", "dateModified": "2026-07-23",
        "author": {"@type": "Organization", "name": "OnceMore Digital", "url": URL},
        "publisher": {"@type": "Organization", "name": "OnceMore Digital",
                      "logo": {"@type": "ImageObject", "url": OG_IMAGE}},
    }
    g_sources = g.get("sources")
    if g_sources:
        article_schema_dict["citation"] = [
            {"@type": "CreativeWork", "name": name, "url": src_url}
            for name, src_url in g_sources
        ]
    gschema = [
        breadcrumb([("Home", "/"), ("Resources", "/resources/"),
                    (g["title"], "/resources/%s/" % g["slug"])]),
        jsonld(article_schema_dict),
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

# ---------------------------------------------------------------- case studies
def _case_sid(h):
    return re.sub(r'[^a-z0-9]+', '-', h.lower()).strip('-')

for c in CASE_STUDIES:
    deep_sections = c.get("sections", [])
    toc_items = [(h, _case_sid(h)) for h, _ in deep_sections]
    toc_items.append((c["approach_heading"], _case_sid(c["approach_heading"])))
    toc_items.append((c["results_heading"], _case_sid(c["results_heading"])))
    if c.get("takeaway_heading"):
        toc_items.append((c["takeaway_heading"], _case_sid(c["takeaway_heading"])))
    toc_html = "".join('<li><a href="#%s">%s</a></li>' % (sid, html.escape(h)) for h, sid in toc_items)

    sections_html = "".join(
        '<h2 id="%s">%s</h2><div class="prose">%s</div>' % (_case_sid(h), html.escape(h), body)
        for h, body in deep_sections)

    approach_cards = "".join(
        '<div class="card"><h3>%s</h3><p>%s</p></div>' % (html.escape(t), b)
        for t, b in c["approach_items"])
    stat_cards = "".join(
        '<div class="stat-card"><span class="stat-num">%s</span><span class="stat-label">%s</span></div>'
        % (html.escape(n), html.escape(l)) for n, l in c["stats"])
    results_html = "".join("<p>%s</p>" % p for p in c["results_body"])
    charts_html = "".join(
        '<div class="case-chart"><img src="%s" alt="%s" loading="lazy" decoding="async"></div>'
        '<p class="case-chart-caption">%s</p>'
        % (src, html.escape(alt), html.escape(cap))
        for src, alt, cap in c.get("charts", []))
    takeaway_html = ""
    if c.get("takeaway_heading"):
        takeaway_html = '<h2 id="%s" style="margin-top:2.5rem">%s</h2><div class="prose">%s</div>' % (
            _case_sid(c["takeaway_heading"]), html.escape(c["takeaway_heading"]), c["takeaway_body"])
    related_links_html = "".join(
        '<li><a href="%s">%s</a></li>' % (url, html.escape(label))
        for label, url in c.get("related_links", []))
    other_cases = "".join(
        '<li><a href="/case-studies/%s/">%s</a></li>' % (o["slug"], html.escape(o["title"]))
        for o in CASE_STUDIES if o["slug"] != c["slug"])
    cbody = f"""
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/case-studies/">Case Studies</a> / {html.escape(c["title"])}</nav>
  <span class="case-tag" style="margin-top:1.25rem">{html.escape(c["industry"])}</span>
  <h1>{html.escape(c["h1"])}</h1>
  <p class="case-byline"><span>Written by Walter Yow, co-founder of OnceMore Digital</span><span class="case-byline-date">Published {html.escape(c.get("published", ""))}</span></p>
  <p class="lead">{html.escape(c["intro"])}</p>
  <div class="divider left" aria-hidden="true"></div>
  <nav class="toc" aria-label="On this page">
    <p class="toc-title">On this page</p>
    <ul>{toc_html}</ul>
  </nav>
  <article>
    {sections_html}
    <h2 id="{_case_sid(c["approach_heading"])}" style="margin-top:2.5rem">{html.escape(c["approach_heading"])}</h2>
    <p class="lead" style="font-size:1.05rem;max-width:62ch;margin-bottom:1.75rem">{html.escape(c["approach_intro"])}</p>
    <div class="grid">{approach_cards}</div>
    <h2 id="{_case_sid(c["results_heading"])}" style="margin-top:2.5rem">{html.escape(c["results_heading"])}</h2>
    <div class="stat-grid">{stat_cards}</div>
    {charts_html}
    <div class="prose" style="margin-top:1.5rem">{results_html}</div>
    {takeaway_html}
  </article>
</div></section>
<section class="section-sm panel-alt"><div class="container">
  <div class="cta-band">
    <h2>Want results like this for your business?</h2>
    <p>Tell us where your SEO is stuck and we will tell you honestly whether we can fix it.</p>
    <div class="btn-row"><a class="btn btn-primary" href="/contact/">Get in Touch</a></div>
  </div>
</div></section>
"""
    if related_links_html:
        cbody += f"""
<section class="section-sm"><div class="container">
  <span class="eyebrow">Go deeper</span>
  <h2>Related services and guides</h2>
  <ul class="link-list">{related_links_html}</ul>
</div></section>
"""
    if other_cases:
        cbody += f"""
<section class="section-sm"><div class="container">
  <span class="eyebrow">Keep reading</span>
  <h2>More case studies</h2>
  <ul class="link-list">{other_cases}</ul>
</div></section>
"""
    cschema = [
        breadcrumb([("Home", "/"), ("Case Studies", "/case-studies/"),
                    (c["title"], "/case-studies/%s/" % c["slug"])]),
        jsonld({
            "@context": "https://schema.org", "@type": "Article",
            "headline": c["title"], "description": c["desc"],
            "url": URL + "/case-studies/%s/" % c["slug"],
            "inLanguage": "en-MY",
            "about": c["industry"],
            "datePublished": "2026-07-22", "dateModified": "2026-07-23",
            "author": {"@type": "Person", "name": "Walter Yow", "url": URL + "/about/"},
            "publisher": {"@type": "Organization", "name": "OnceMore Digital",

                          "logo": {"@type": "ImageObject", "url": OG_IMAGE}},
        }),
    ]
    page("/case-studies/%s/" % c["slug"], "%s | OnceMore Digital" % c["title"], c["desc"],
         cbody, active="case-studies", schema_blocks=cschema)

# case studies hub
case_cards = "".join(
    f'''<a class="case-card" href="/case-studies/{c["slug"]}/">
    <span class="case-tag">{html.escape(c["industry"])}</span>
    <h3>{html.escape(c["title"])}</h3>
    <p>{html.escape(c["desc"])}</p>
    <div class="stat-row">{"".join('<div><strong>%s</strong><span>%s</span></div>' % (html.escape(n), html.escape(l)) for n, l in c["stats"][:3])}</div>
    <span class="more">Read case study &rarr;</span>
    </a>''' for c in CASE_STUDIES)
case_hub_body = """
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Case Studies</nav>
  <span class="eyebrow" style="margin-top:1.5rem">Case Studies</span>
  <h1>Real results for <em>real businesses.</em></h1>
  <p class="lead">No vanity metrics. Here is what actually changed for businesses we have worked with, and how we did it.</p>
  <div class="case-grid" style="margin-top:2.5rem">%s</div>
</div></section>
<section class="section-sm"><div class="container"><div class="cta-band">
  <h2>Want to be the next one?</h2>
  <p>Tell us what is not working and we will tell you honestly what it will take to fix it.</p>
  <div class="btn-row"><a class="btn btn-primary" href="/contact/">Get in Touch</a></div>
</div></div></section>
""" % case_cards
case_hub_schema = [
    breadcrumb([("Home", "/"), ("Case Studies", "/case-studies/")]),
    jsonld({"@context": "https://schema.org", "@type": "CollectionPage",
            "name": "Case Studies", "url": URL + "/case-studies/",
            "hasPart": [{"@type": "Article", "headline": c["title"],
                         "url": URL + "/case-studies/%s/" % c["slug"]} for c in CASE_STUDIES]}),
]
page("/case-studies/", "Case Studies | Real SEO Results | OnceMore Digital",
     "Real case studies from OnceMore Digital: what we did, why it mattered, and the results Malaysian and regional businesses achieved.",
     case_hub_body, active="case-studies", schema_blocks=case_hub_schema)

# ---------------------------------------------------------------- html sitemap
sitemap_groups = [
    ("Main", [("Home", "/")]),
    ("Services", [("Services overview", "/services/")] +
     [(s[1] + " (" + s[2] + ")", "/services/%s/" % s[0]) for s in SERVICES]),
    ("Resources", [("Resources overview", "/resources/")] +
     [(g["title"], "/resources/%s/" % g["slug"]) for g in RESOURCES]),
    ("Case Studies", [("Case studies overview", "/case-studies/")] +
     [(c["title"], "/case-studies/%s/" % c["slug"]) for c in CASE_STUDIES]),
    ("Company", [("About", "/about/"), ("Contact", "/contact/")]),
]

sitemap_sections_html = "".join(
    '<div><h3>%s</h3><ul class="link-list">%s</ul></div>' % (
        html.escape(group_name),
        "".join('<li><a href="%s">%s</a></li>' % (href, html.escape(name)) for name, href in links)
    )
    for group_name, links in sitemap_groups
)

sitemap_body = """
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Sitemap</nav>
  <span class="eyebrow" style="margin-top:1.5rem">Sitemap</span>
  <h1>Every page on <em>this site.</em></h1>
  <p class="lead">A quick, human-readable map of the whole site. Looking for the XML version for search engines? It lives at <a href="/sitemap.xml">/sitemap.xml</a>.</p>
  <div class="divider left" aria-hidden="true"></div>
  <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:2.5rem;margin-top:1rem">
    %s
  </div>
</div></section>
""" % sitemap_sections_html

sitemap_schema = [
    breadcrumb([("Home", "/"), ("Sitemap", "/sitemap/")]),
    jsonld({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Sitemap",
        "url": URL + "/sitemap/",
        "hasPart": [
            {"@type": "WebPage", "name": name, "url": URL + href}
            for _, links in sitemap_groups for name, href in links
        ],
    }),
]
page("/sitemap/", "Sitemap | OnceMore Digital",
     "A full, human-readable sitemap of every page on the OnceMore Digital website.",
     sitemap_body, schema_blocks=sitemap_schema)

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
