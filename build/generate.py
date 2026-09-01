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
        <li><a href="/services/geo/">AIO / GEO</a></li>
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
        <li><a href="/services/geo/">AIO / GEO</a></li>
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
<script>document.documentElement.classList.add('js')</script>
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
    ("geo", "AIO/GEO", "AI Optimisation & GEO",
     "Get your business cited, quoted and recommended by the AI tools your customers already use.",
     "AIO/GEO is the combined discipline of getting your business cited, quoted and recommended by AI tools. GEO (Generative Engine Optimisation) is the goal: being one of the sources an AI tool names. AIO (AI Optimisation) is the practical layer underneath it: the structural work of clean headings, direct answers, schema markup and consistent facts that makes that possible.",
     ["Content structured for AI extraction",
      "Entity and topical authority signals",
      "Schema markup that machines can read",
      "Clear, quotable answers on key pages",
      "Tracking where you appear in AI results"],
     []),
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
    "content-writing": _S + '<line x1="6" y1="10" x2="20" y2="10"/><line x1="6" y1="16" x2="16" y2="16"/>'
                            '<line x1="6" y1="22" x2="13" y2="22"/><path d="M20 24l6-6 3 3-6 6-4 1z"/></svg>',
}

# Curated line-icon set (data/analytics pack), recoloured to currentColor so
# icons inherit whatever CSS color is applied to their wrapper.
ROADMAP_ICONS = {
    "audience": "<svg viewBox=\"0 0 47.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M15.65,53.25a.61.61,0,0,1-.39-.13.63.63,0,0,1-.24-.49V44.78a.38.38,0,0,0-.37-.38h-7A1.63,1.63,0,0,1,6,42.78V35.67a.37.37,0,0,0-.27-.36L.45,33.73a.66.66,0,0,1-.4-.35.65.65,0,0,1,0-.53L5.33,22.11a9.08,9.08,0,0,0,.91-3.31A20.57,20.57,0,0,1,31.39.52a20.21,20.21,0,0,1,15.86,20,21.93,21.93,0,0,1-2.1,9.65,34.53,34.53,0,0,0-3.43,15v1.43a.63.63,0,0,1-.48.61l-25.45,6ZM1.51,32.74l4.58,1.37a1.63,1.63,0,0,1,1.16,1.56v7.11a.38.38,0,0,0,.37.37h7a1.63,1.63,0,0,1,1.62,1.63v7.06l24.2-5.71V45.2A35.7,35.7,0,0,1,44,29.64a20.77,20.77,0,0,0,2-9.1A19,19,0,0,0,31.12,1.74,19.33,19.33,0,0,0,7.49,18.91a10.44,10.44,0,0,1-1,3.75ZM41.09,46.63h0Z\"/><path d=\"M26.62,26.75a6.13,6.13,0,1,1,6.13-6.12A6.13,6.13,0,0,1,26.62,26.75Zm0-11a4.88,4.88,0,1,0,4.88,4.88A4.88,4.88,0,0,0,26.62,15.75Z\"/><path d=\"M26.62,36.81a.62.62,0,0,1-.44-.18L18.4,28.85a11.63,11.63,0,1,1,16.45,0l-7.78,7.78A.63.63,0,0,1,26.62,36.81Zm0-26.55A10.37,10.37,0,0,0,19.29,28l7.33,7.34L34,28a10.37,10.37,0,0,0-7.34-17.7Z\"/></svg>",
    "signpost": "<svg viewBox=\"0 0 54.64 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M30.32,53.25h-6a.63.63,0,0,1-.62-.63v-14a.62.62,0,0,1,.62-.62h6a.63.63,0,0,1,.63.62v14A.63.63,0,0,1,30.32,53.25ZM25,52H29.7V39.25H25Z\"/><path d=\"M30.32,27.25h-6a.63.63,0,0,1-.62-.63v-7a.62.62,0,0,1,.62-.62h6a.63.63,0,0,1,.63.62v7A.63.63,0,0,1,30.32,27.25ZM25,26H29.7V20.25H25Z\"/><path d=\"M30.32,8.25h-6a.63.63,0,0,1-.62-.63v-7A.62.62,0,0,1,24.32,0h6A.63.63,0,0,1,31,.62v7A.63.63,0,0,1,30.32,8.25ZM25,7H29.7V1.25H25Z\"/><path d=\"M48,20.25H13a.63.63,0,0,1-.63-.63v-12A.63.63,0,0,1,13,7H48a.67.67,0,0,1,.44.18l6,6a.64.64,0,0,1,0,.89l-6,6A.67.67,0,0,1,48,20.25ZM13.64,19H47.76l5.37-5.38L47.76,8.25H13.64Z\"/><path d=\"M41.62,39.25h-35a.67.67,0,0,1-.44-.18l-6-6a.64.64,0,0,1,0-.89l6-6A.67.67,0,0,1,6.62,26h35a.63.63,0,0,1,.63.62v12A.63.63,0,0,1,41.62,39.25ZM6.88,38H41V27.25H6.88L1.51,32.62Z\"/><path d=\"M53.32,53.25h-52a.63.63,0,0,1,0-1.25h52a.63.63,0,1,1,0,1.25Z\"/></svg>",
    "checklist": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M48.62,53.25a.6.6,0,0,1-.55-.35l-4-8a.53.53,0,0,1-.07-.28v-38A.62.62,0,0,1,44.62,6h8a.63.63,0,0,1,.63.62v38a.53.53,0,0,1-.07.28l-4,8A.61.61,0,0,1,48.62,53.25Zm-3.37-8.77,3.37,6.75L52,44.48V7.25H45.25Z\"/><path d=\"M52.62,45.25h-8a.63.63,0,0,1,0-1.25h8a.63.63,0,1,1,0,1.25Z\"/><path d=\"M48.62,45.25a.63.63,0,0,1-.62-.63v-38a.63.63,0,0,1,1.25,0v38A.63.63,0,0,1,48.62,45.25Z\"/><path d=\"M52.62,7.25h-8A.63.63,0,0,1,44,6.62v-4A2.63,2.63,0,0,1,46.62,0h4a2.63,2.63,0,0,1,2.63,2.62v4A.63.63,0,0,1,52.62,7.25ZM45.25,6H52V2.62a1.38,1.38,0,0,0-1.38-1.37h-4a1.38,1.38,0,0,0-1.37,1.37Z\"/><path d=\"M25.62,9.25h-5a.63.63,0,0,1,0-1.25h5a.63.63,0,1,1,0,1.25Z\"/><path d=\"M17.62,9.25h-3a.63.63,0,0,1,0-1.25h3a.63.63,0,1,1,0,1.25Z\"/><path d=\"M25.62,12.25h-11a.63.63,0,0,1,0-1.25h11a.63.63,0,1,1,0,1.25Z\"/><path d=\"M33.62,23.25h-11a.63.63,0,0,1,0-1.25h11a.63.63,0,1,1,0,1.25Z\"/><path d=\"M19.62,23.25h-5a.63.63,0,0,1,0-1.25h5a.63.63,0,1,1,0,1.25Z\"/><path d=\"M33.62,20.25h-4a.63.63,0,0,1,0-1.25h4a.63.63,0,1,1,0,1.25Z\"/><path d=\"M26.62,20.25h-12a.63.63,0,0,1,0-1.25h12a.63.63,0,1,1,0,1.25Z\"/><path d=\"M28.62,34.25h-14a.63.63,0,0,1,0-1.25h14a.63.63,0,1,1,0,1.25Z\"/><path d=\"M33.62,31.25h-8a.63.63,0,0,1,0-1.25h8a.63.63,0,1,1,0,1.25Z\"/><path d=\"M22.62,31.25h-8a.63.63,0,0,1,0-1.25h8a.63.63,0,1,1,0,1.25Z\"/><path d=\"M33.62,42.25h-10a.63.63,0,0,1,0-1.25h10a.63.63,0,1,1,0,1.25Z\"/><path d=\"M20.62,42.25h-6a.63.63,0,0,1,0-1.25h6a.63.63,0,1,1,0,1.25Z\"/><path d=\"M24.62,45.25h-10a.63.63,0,0,1,0-1.25h10a.63.63,0,1,1,0,1.25Z\"/><path d=\"M39.62,53.25H.62A.63.63,0,0,1,0,52.62V.62A.62.62,0,0,1,.62,0h29a.67.67,0,0,1,.45.18l10,10a.67.67,0,0,1,.18.44v42A.63.63,0,0,1,39.62,53.25ZM1.25,52H39V10.88L29.37,1.25H1.25Z\"/><path d=\"M39.62,11.25h-10a.63.63,0,0,1-.62-.63V.62a.61.61,0,0,1,.39-.57.62.62,0,0,1,.68.13l10,10a.62.62,0,0,1,.13.68A.61.61,0,0,1,39.62,11.25ZM30.25,10h7.87L30.25,2.13Z\"/><path d=\"M7.39,12.75a.66.66,0,0,1-.45-.18L5,10.66a.63.63,0,1,1,.89-.89l1.47,1.47,3.55-3.56a.63.63,0,0,1,.89.89l-4,4A.62.62,0,0,1,7.39,12.75Z\"/><path d=\"M7.39,23.75a.66.66,0,0,1-.45-.18L5,21.66a.63.63,0,1,1,.89-.89l1.47,1.47,3.55-3.56a.63.63,0,0,1,.89.89l-4,4A.62.62,0,0,1,7.39,23.75Z\"/><path d=\"M7.39,34.75a.66.66,0,0,1-.45-.18L5,32.66a.63.63,0,1,1,.89-.89l1.47,1.47,3.55-3.56a.63.63,0,0,1,.89.89l-4,4A.62.62,0,0,1,7.39,34.75Z\"/><path d=\"M7.39,45.75a.66.66,0,0,1-.45-.18L5,43.66a.63.63,0,0,1,.89-.89l1.47,1.47,3.55-3.56a.63.63,0,0,1,.89.89l-4,4A.62.62,0,0,1,7.39,45.75Z\"/></svg>",
    "gears": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M17.56,31.25H13.69a1.35,1.35,0,0,1-1.31-1l-1-4.1-.47-.6.32.54L7.59,28.25A1.35,1.35,0,0,1,6,28L3.21,25.3A1.35,1.35,0,0,1,3,23.66L5.18,20l-.06-.15-4.1-1a1.35,1.35,0,0,1-1-1.31V13.69a1.35,1.35,0,0,1,1-1.31l4.1-1,.06-.14L3,7.59A1.35,1.35,0,0,1,3.21,6L6,3.21A1.35,1.35,0,0,1,7.59,3l3.62,2.18.15-.06,1-4.1a1.35,1.35,0,0,1,1.31-1h3.87a1.35,1.35,0,0,1,1.31,1l1,4.1.47.6L20,5.18,23.66,3a1.35,1.35,0,0,1,1.64.21L28,6a1.35,1.35,0,0,1,.21,1.64l-2.18,3.63.06.14,4.1,1h0a1.35,1.35,0,0,1,1,1.31v3.87a1.35,1.35,0,0,1-1,1.31l-4.1,1-.59.47.53-.32,2.18,3.62A1.35,1.35,0,0,1,28,25.3L25.3,28a1.35,1.35,0,0,1-1.64.21L20,26.07l-.15.06-1,4.1A1.35,1.35,0,0,1,17.56,31.25Zm-6.3-6.44a1.33,1.33,0,0,1,1.31,1l1,4.1a.11.11,0,0,0,.1.07h3.87a.11.11,0,0,0,.1-.07l1-4.1a1.35,1.35,0,0,1,2-.83l3.62,2.17a.09.09,0,0,0,.12,0l2.74-2.74a.09.09,0,0,0,0-.12L25,20.68a1.36,1.36,0,0,1-.09-1.21,1.33,1.33,0,0,1,.92-.79l4.1-1a.11.11,0,0,0,.07-.1V13.69a.11.11,0,0,0-.07-.1l-4.1-1a1.35,1.35,0,0,1-.83-2L27.17,7a.09.09,0,0,0,0-.12L24.42,4.09a.09.09,0,0,0-.12,0L20.68,6.25a1.35,1.35,0,0,1-2-.83l-1-4.1a.11.11,0,0,0-.1-.07H13.69a.11.11,0,0,0-.1.07l-1,4.1a1.35,1.35,0,0,1-2,.83L7,4.08a.09.09,0,0,0-.12,0L4.09,6.83a.09.09,0,0,0,0,.12l2.17,3.62a1.35,1.35,0,0,1-.83,2l-4.1,1a.11.11,0,0,0-.07.1v3.87a.11.11,0,0,0,.07.1l4.1,1a1.31,1.31,0,0,1,.92.79,1.36,1.36,0,0,1-.09,1.21L4.08,24.3a.09.09,0,0,0,0,.12l2.74,2.74a.09.09,0,0,0,.12,0L10.57,25A1.33,1.33,0,0,1,11.26,24.81Z\"/><path d=\"M15.62,21.75a6.13,6.13,0,1,1,6.13-6.13A6.13,6.13,0,0,1,15.62,21.75Zm0-11a4.88,4.88,0,1,0,4.88,4.87A4.88,4.88,0,0,0,15.62,10.75Z\"/><path d=\"M42.21,40.65a1.15,1.15,0,0,1-1-.67l-1.24-2.66-2.19,2a1.14,1.14,0,0,1-1.41.09L34,37.79a1.13,1.13,0,0,1-.43-1.35l1-2.75-2.93-.17a1.12,1.12,0,0,1-1.06-.93L30,29.83a1.15,1.15,0,0,1,.65-1.26l2.66-1.24-2-2.19a1.14,1.14,0,0,1-.09-1.41l1.58-2.33A1.14,1.14,0,0,1,34.22,21L37,22,37.14,19A1.16,1.16,0,0,1,38.07,18l2.77-.53a1.15,1.15,0,0,1,1.26.65l1.24,2.66,2.19-2a1.16,1.16,0,0,1,1.41-.1l2.33,1.58a1.15,1.15,0,0,1,.44,1.35l-1,2.76,2.93.16a1.15,1.15,0,0,1,1.07.93l.53,2.77a1.15,1.15,0,0,1-.65,1.26l-2.66,1.24,2,2.18a1.17,1.17,0,0,1,.1,1.42L50.4,36.67a1.15,1.15,0,0,1-1.35.43l-2.76-1L46.13,39a1.14,1.14,0,0,1-.93,1.06l-2.77.54ZM40,36l.24,0a1.16,1.16,0,0,1,.81.65l1.26,2.71,2.61-.5.17-3a1.14,1.14,0,0,1,1.54-1l2.81,1,1.5-2.2-2-2.23a1.15,1.15,0,0,1,.37-1.81L52,28.4l-.51-2.61-3-.17a1.12,1.12,0,0,1-.89-.52,1.09,1.09,0,0,1-.12-1l1-2.82L46.3,19.77l-2.23,2a1.15,1.15,0,0,1-1.81-.37L41,18.68l-2.61.5-.17,3a1.14,1.14,0,0,1-1.54,1l-2.81-1-1.49,2.21,2,2.23a1.13,1.13,0,0,1,.26,1,1.12,1.12,0,0,1-.64.81l-2.71,1.26.5,2.61,3,.17a1.13,1.13,0,0,1,1,1.54l-1,2.81L37,38.29l2.23-2A1.15,1.15,0,0,1,40,36Zm11.6-10.21Z\"/><path d=\"M41.63,32.66a3.63,3.63,0,0,1-3-5.66,3.63,3.63,0,1,1,6,4.07,3.61,3.61,0,0,1-2.32,1.52A3.23,3.23,0,0,1,41.63,32.66Zm0-6a2.28,2.28,0,0,0-.45,0,2.38,2.38,0,0,0-1.52,1,2.35,2.35,0,0,0-.37,1.78,2.4,2.4,0,0,0,1,1.52A2.38,2.38,0,0,0,44,28.59h0a2.38,2.38,0,0,0-2.33-1.92Z\"/><path d=\"M22,53.25a.55.55,0,0,1-.18,0l-2.45-.41a1.07,1.07,0,0,1-.91-1l-.19-2.49-2.32.92a1.1,1.1,0,0,1-1.28-.38l-1.45-2a1.08,1.08,0,0,1,.06-1.33l1.62-1.9-2.29-1a1.09,1.09,0,0,1-.63-1.18L12.35,40a1.09,1.09,0,0,1,1-.91l2.49-.19-.92-2.32a1.08,1.08,0,0,1,.39-1.28l2-1.45a1.08,1.08,0,0,1,1.33.06l1.9,1.62,1-2.29a1.1,1.1,0,0,1,1.18-.63l2.45.41a1.08,1.08,0,0,1,.91,1l.19,2.49,2.32-.92a1.1,1.1,0,0,1,1.28.38l1.45,2a1.08,1.08,0,0,1-.06,1.33l-1.62,1.9,2.29,1a1.11,1.11,0,0,1,.64,1.18l-.42,2.45a1.08,1.08,0,0,1-1,.91l-2.49.19.92,2.32a1.09,1.09,0,0,1-.38,1.28l-2,1.45a1.08,1.08,0,0,1-1.33-.06L24,50.31,23,52.6A1.09,1.09,0,0,1,22,53.25Zm-2.3-1.64,2.2.37,1-2.37a1.09,1.09,0,0,1,.76-.62,1.07,1.07,0,0,1,.94.23l2,1.68,1.82-1.3-.95-2.4a1.09,1.09,0,0,1,.93-1.49l2.57-.2.37-2.2-2.37-1a1.09,1.09,0,0,1-.39-1.7l1.68-2-1.3-1.82-2.4,1A1.09,1.09,0,0,1,25,36.81l-.2-2.57-2.2-.37-1,2.37a1.06,1.06,0,0,1-.76.62,1,1,0,0,1-.94-.23l-2-1.68-1.82,1.3.95,2.4a1.09,1.09,0,0,1-.93,1.49l-2.57.2-.37,2.2,2.37,1a1.09,1.09,0,0,1,.62.75,1.11,1.11,0,0,1-.23,1l-1.68,2,1.3,1.82,2.4-1a1.09,1.09,0,0,1,1,.09,1.11,1.11,0,0,1,.51.84Zm-4.6-6.89Z\"/><path d=\"M22.25,46.05a3,3,0,0,1-.52,0,3.13,3.13,0,1,1,3.6-2.57h0A3.14,3.14,0,0,1,22.25,46.05Zm0-5a1.88,1.88,0,0,0-1.84,1.57,1.87,1.87,0,1,0,3.69.61,1.81,1.81,0,0,0-.32-1.39,1.83,1.83,0,0,0-1.22-.76A1.63,1.63,0,0,0,22.24,41.05Zm2.47,2.29h0Z\"/></svg>",
    "report": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M44.84,35.13H41.62a.63.63,0,0,1,0-1.25h3.22A7.15,7.15,0,0,0,46.2,19.71a.64.64,0,0,1-.45-.35.67.67,0,0,1,0-.57,6,6,0,0,0-9.2-7.35.63.63,0,0,1-.63.12.64.64,0,0,1-.41-.51,11.26,11.26,0,0,0-22.42,1.46,11.42,11.42,0,0,0,.2,2.07.62.62,0,0,1-.74.73,9.19,9.19,0,0,0-1.93-.21,9.39,9.39,0,0,0,0,18.78h1a.63.63,0,1,1,0,1.25h-1A10.64,10.64,0,1,1,12,13.94a11.68,11.68,0,0,1-.09-1.43A12.51,12.51,0,0,1,36.59,9.84a7.15,7.15,0,0,1,4-1.21,7.21,7.21,0,0,1,6.64,10,8.4,8.4,0,0,1-2.38,16.46Z\"/><path d=\"M41.62,29.25a.63.63,0,0,1-.62-.63v-5a1.38,1.38,0,0,0-1.38-1.37h-26a1.38,1.38,0,0,0-1.37,1.37v5a.63.63,0,1,1-1.25,0v-5A2.63,2.63,0,0,1,13.62,21h26a2.63,2.63,0,0,1,2.63,2.62v5A.63.63,0,0,1,41.62,29.25Z\"/><path d=\"M37.62,28.25a.63.63,0,0,1-.62-.63v-3a.63.63,0,0,1,1.25,0v3A.63.63,0,0,1,37.62,28.25Z\"/><path d=\"M33.62,28.25a.63.63,0,0,1-.62-.63v-3a.63.63,0,0,1,1.25,0v3A.63.63,0,0,1,33.62,28.25Z\"/><path d=\"M29.62,28.25a.63.63,0,0,1-.62-.63v-3a.63.63,0,0,1,1.25,0v3A.63.63,0,0,1,29.62,28.25Z\"/><path d=\"M41.62,38.25a.63.63,0,0,1-.62-.63v-5a1.38,1.38,0,0,0-1.38-1.37h-26a1.38,1.38,0,0,0-1.37,1.37v5a.63.63,0,1,1-1.25,0v-5A2.63,2.63,0,0,1,13.62,30h26a2.63,2.63,0,0,1,2.63,2.62v5A.63.63,0,0,1,41.62,38.25Z\"/><path d=\"M37.62,37.25a.63.63,0,0,1-.62-.63v-3a.63.63,0,0,1,1.25,0v3A.63.63,0,0,1,37.62,37.25Z\"/><path d=\"M33.62,37.25a.63.63,0,0,1-.62-.63v-3a.63.63,0,0,1,1.25,0v3A.63.63,0,0,1,33.62,37.25Z\"/><path d=\"M29.62,37.25a.63.63,0,0,1-.62-.63v-3a.63.63,0,0,1,1.25,0v3A.63.63,0,0,1,29.62,37.25Z\"/><path d=\"M39.62,49.25h-26A2.63,2.63,0,0,1,11,46.62v-5A2.63,2.63,0,0,1,13.62,39h26a2.63,2.63,0,0,1,2.63,2.62v5A2.63,2.63,0,0,1,39.62,49.25Zm-26-9a1.38,1.38,0,0,0-1.37,1.37v5A1.38,1.38,0,0,0,13.62,48h26A1.38,1.38,0,0,0,41,46.62v-5a1.38,1.38,0,0,0-1.38-1.37Z\"/><path d=\"M37.62,46.25a.63.63,0,0,1-.62-.63v-3a.63.63,0,0,1,1.25,0v3A.63.63,0,0,1,37.62,46.25Z\"/><path d=\"M33.62,46.25a.63.63,0,0,1-.62-.63v-3a.63.63,0,0,1,1.25,0v3A.63.63,0,0,1,33.62,46.25Z\"/><path d=\"M29.62,46.25a.63.63,0,0,1-.62-.63v-3a.63.63,0,0,1,1.25,0v3A.63.63,0,0,1,29.62,46.25Z\"/><path d=\"M26.62,53.25a.63.63,0,0,1-.62-.63v-4a.63.63,0,0,1,1.25,0v4A.63.63,0,0,1,26.62,53.25Z\"/><path d=\"M26.62,53.25h-11a.63.63,0,0,1,0-1.25h11a.63.63,0,1,1,0,1.25Z\"/><path d=\"M37.62,53.25h-11a.63.63,0,0,1,0-1.25h11a.63.63,0,1,1,0,1.25Z\"/></svg>",
    "growth": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M52.62,53.25H.62A.63.63,0,0,1,0,52.62V.62a.63.63,0,0,1,1.25,0V52H52.62a.63.63,0,1,1,0,1.25Z\"/><path d=\"M31.62,53.25h-7a.63.63,0,0,1-.62-.63v-19a.62.62,0,0,1,.62-.62h7a.63.63,0,0,1,.63.62v19A.63.63,0,0,1,31.62,53.25ZM25.25,52H31V34.25H25.25Z\"/><path d=\"M24.62,53.25h-7a.63.63,0,0,1-.62-.63v-24a.62.62,0,0,1,.62-.62h7a.63.63,0,0,1,.63.62v24A.63.63,0,0,1,24.62,53.25ZM18.25,52H24V29.25H18.25Z\"/><path d=\"M17.62,53.25h-7a.63.63,0,0,1-.62-.63v-13a.62.62,0,0,1,.62-.62h7a.63.63,0,0,1,.63.62v13A.63.63,0,0,1,17.62,53.25ZM11.25,52H17V40.25H11.25Z\"/><path d=\"M38.62,53.25h-7a.63.63,0,0,1-.62-.63v-29a.62.62,0,0,1,.62-.62h7a.63.63,0,0,1,.63.62v29A.63.63,0,0,1,38.62,53.25ZM32.25,52H38V24.25H32.25Z\"/><path d=\"M45.62,53.25h-7a.63.63,0,0,1-.62-.63v-23a.62.62,0,0,1,.62-.62h7a.63.63,0,0,1,.63.62v23A.63.63,0,0,1,45.62,53.25ZM39.25,52H45V30.25H39.25Z\"/><path d=\"M52.62,53.25h-7a.63.63,0,0,1-.62-.63v-38a.62.62,0,0,1,.62-.62h7a.63.63,0,0,1,.63.62v38A.63.63,0,0,1,52.62,53.25ZM46.25,52H52V15.25H46.25Z\"/><path d=\"M2.62,35.25h-2A.63.63,0,0,1,.62,34h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,29.25h-2A.63.63,0,0,1,.62,28h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,47.25h-2A.63.63,0,0,1,.62,46h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,41.25h-2A.63.63,0,0,1,.62,40h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,11.25h-2A.63.63,0,0,1,.62,10h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,5.25h-2A.63.63,0,0,1,.62,4h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,23.25h-2A.63.63,0,0,1,.62,22h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,17.25h-2A.63.63,0,0,1,.62,16h2a.63.63,0,1,1,0,1.25Z\"/></svg>",
    "compass": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M26.62,53.25A26.63,26.63,0,1,1,53.25,26.62,26.65,26.65,0,0,1,26.62,53.25Zm0-52A25.38,25.38,0,1,0,52,26.62,25.4,25.4,0,0,0,26.62,1.25Z\"/><path d=\"M26.62,47.25A20.63,20.63,0,1,1,47.25,26.62,20.65,20.65,0,0,1,26.62,47.25Zm0-40A19.38,19.38,0,1,0,46,26.62,19.39,19.39,0,0,0,26.62,7.25Z\"/><path d=\"M10.62,27.25h-4a.63.63,0,0,1,0-1.25h4a.63.63,0,1,1,0,1.25Z\"/><path d=\"M46.62,27.25h-4a.63.63,0,0,1,0-1.25h4a.63.63,0,1,1,0,1.25Z\"/><path d=\"M26.62,47.25a.63.63,0,0,1-.62-.63v-4a.63.63,0,0,1,1.25,0v4A.63.63,0,0,1,26.62,47.25Z\"/><path d=\"M26.62,11.25a.63.63,0,0,1-.62-.63v-4a.63.63,0,0,1,1.25,0v4A.63.63,0,0,1,26.62,11.25Z\"/><path d=\"M15.62,38.25a.62.62,0,0,1-.44-.18.64.64,0,0,1-.12-.71l7-15a.62.62,0,0,1,.3-.3l15-7a.62.62,0,0,1,.83.83l-7,15a.62.62,0,0,1-.3.3l-15,7A.66.66,0,0,1,15.62,38.25ZM23.1,23.1,16.92,36.33l13.23-6.18,6.18-13.23Zm7.52,7.52h0Z\"/><path d=\"M30.62,31.25a.64.64,0,0,1-.44-.18l-8-8a.63.63,0,0,1,.89-.89l8,8a.63.63,0,0,1-.45,1.07Z\"/></svg>",
    "megaphone": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M22.62,45.25A22.63,22.63,0,1,1,45.25,22.62a.63.63,0,1,1-1.25,0A21.36,21.36,0,1,0,27.28,43.49.64.64,0,0,1,28,44a.63.63,0,0,1-.48.74A22.57,22.57,0,0,1,22.62,45.25Z\"/><path d=\"M22.62,45.25C15.66,45.25,10,35.1,10,22.62S15.66,0,22.62,0,35.25,10.15,35.25,22.62a.63.63,0,1,1-1.25,0C34,10.84,28.9,1.25,22.62,1.25S11.25,10.84,11.25,22.62,16.35,44,22.62,44a.63.63,0,1,1,0,1.25Z\"/><path d=\"M22.62,45.25a.63.63,0,0,1-.62-.63V.62a.63.63,0,0,1,1.25,0v44A.63.63,0,0,1,22.62,45.25Z\"/><path d=\"M27.62,23.25H.62A.63.63,0,0,1,.62,22h27a.63.63,0,1,1,0,1.25Z\"/><path d=\"M41.68,12.25H3.57a.63.63,0,0,1,0-1.25H41.68a.63.63,0,0,1,0,1.25Z\"/><path d=\"M27.62,34.25h-24a.63.63,0,0,1,0-1.25H27.62a.63.63,0,1,1,0,1.25Z\"/><path d=\"M46.62,53.25h-16a.63.63,0,0,1-.62-.63v-30a.62.62,0,0,1,.62-.62h22a.63.63,0,0,1,.63.62v24a.67.67,0,0,1-.18.45l-6,6A.67.67,0,0,1,46.62,53.25ZM31.25,52H46.37L52,46.37V23.25H31.25Z\"/><path d=\"M46.62,53.25a.59.59,0,0,1-.23,0,.61.61,0,0,1-.39-.58v-6a.62.62,0,0,1,.62-.62h6a.61.61,0,0,1,.58.39.62.62,0,0,1-.13.68l-6,6A.63.63,0,0,1,46.62,53.25Zm.63-6v3.87l3.87-3.87Z\"/></svg>",
    "chart_up": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M52.62,53.25H.62A.63.63,0,0,1,0,52.62V.62a.63.63,0,0,1,1.25,0V52H52.62a.63.63,0,1,1,0,1.25Z\"/><path d=\"M46.62,53.25a.63.63,0,0,1-.62-.63v-42a.62.62,0,0,1,.62-.62h4.6l-7.6-8.44L36,10h4.59a.63.63,0,0,1,.63.62v42a.63.63,0,1,1-1.25,0V11.25H34.62a.64.64,0,0,1-.57-.37.63.63,0,0,1,.11-.67l9-10a.64.64,0,0,1,.93,0l9,10a.63.63,0,0,1,.11.67.64.64,0,0,1-.58.37H47.25V52.62A.63.63,0,0,1,46.62,53.25Z\"/><path d=\"M34.62,53.25a.63.63,0,0,1-.62-.63v-36a.63.63,0,0,1,1.25,0v36A.63.63,0,0,1,34.62,53.25Z\"/><path d=\"M28.62,53.25a.63.63,0,0,1-.62-.63v-30a.63.63,0,0,1,1.25,0v30A.63.63,0,0,1,28.62,53.25Z\"/><path d=\"M22.62,53.25a.63.63,0,0,1-.62-.63v-24a.63.63,0,0,1,1.25,0v24A.63.63,0,0,1,22.62,53.25Z\"/><path d=\"M16.62,53.25a.63.63,0,0,1-.62-.63v-18a.63.63,0,0,1,1.25,0v18A.63.63,0,0,1,16.62,53.25Z\"/><path d=\"M10.62,53.25a.63.63,0,0,1-.62-.63v-12a.63.63,0,0,1,1.25,0v12A.63.63,0,0,1,10.62,53.25Z\"/><path d=\"M2.62,35.25h-2A.63.63,0,0,1,.62,34h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,29.25h-2A.63.63,0,0,1,.62,28h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,47.25h-2A.63.63,0,0,1,.62,46h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,41.25h-2A.63.63,0,0,1,.62,40h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,11.25h-2A.63.63,0,0,1,.62,10h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,5.25h-2A.63.63,0,0,1,.62,4h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,23.25h-2A.63.63,0,0,1,.62,22h2a.63.63,0,1,1,0,1.25Z\"/><path d=\"M2.62,17.25h-2A.63.63,0,0,1,.62,16h2a.63.63,0,1,1,0,1.25Z\"/></svg>",
    "target": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M26.62,38.25A11.63,11.63,0,1,1,38.25,26.62,11.63,11.63,0,0,1,26.62,38.25Zm0-22A10.38,10.38,0,1,0,37,26.62,10.38,10.38,0,0,0,26.62,16.25Z\"/><path d=\"M26.62,45.25A18.63,18.63,0,1,1,45.25,26.62,18.65,18.65,0,0,1,26.62,45.25Zm0-36A17.38,17.38,0,1,0,44,26.62,17.39,17.39,0,0,0,26.62,9.25Z\"/><path d=\"M26.62,51.25A24.63,24.63,0,1,1,51.25,26.62,24.66,24.66,0,0,1,26.62,51.25Zm0-48A23.38,23.38,0,1,0,50,26.62,23.4,23.4,0,0,0,26.62,3.25Z\"/><path d=\"M52.62,27.25h-15a.63.63,0,0,1,0-1.25h15a.63.63,0,1,1,0,1.25Z\"/><path d=\"M15.62,27.25H.62A.63.63,0,0,1,.62,26h15a.63.63,0,1,1,0,1.25Z\"/><path d=\"M26.62,16.25a.63.63,0,0,1-.62-.63V.62a.63.63,0,0,1,1.25,0v15A.63.63,0,0,1,26.62,16.25Z\"/><path d=\"M26.62,53.25a.63.63,0,0,1-.62-.63v-15a.63.63,0,0,1,1.25,0v15A.63.63,0,0,1,26.62,53.25Z\"/></svg>",
    "analytics": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M7.62,35.25h-5A2.63,2.63,0,0,1,0,32.62v-30A2.63,2.63,0,0,1,2.62,0h16a.63.63,0,0,1,.53.28L23,6H40.62a2.63,2.63,0,0,1,2.63,2.62v13a.63.63,0,1,1-1.25,0v-13a1.38,1.38,0,0,0-1.38-1.37h-18A.63.63,0,0,1,22.1,7L18.29,1.25H2.62A1.38,1.38,0,0,0,1.25,2.62v30A1.38,1.38,0,0,0,2.62,34h5a.63.63,0,1,1,0,1.25Z\"/><path d=\"M15.62,7.25h-9A.63.63,0,0,1,6.62,6h9a.63.63,0,1,1,0,1.25Z\"/><path d=\"M50.62,53.25h-38A2.63,2.63,0,0,1,10,50.62v-30A2.63,2.63,0,0,1,12.62,18h16a.63.63,0,0,1,.53.28L33,24H50.62a2.63,2.63,0,0,1,2.63,2.62v24A2.63,2.63,0,0,1,50.62,53.25Zm-38-34a1.38,1.38,0,0,0-1.37,1.37v30A1.38,1.38,0,0,0,12.62,52h38A1.38,1.38,0,0,0,52,50.62v-24a1.38,1.38,0,0,0-1.38-1.37h-18A.63.63,0,0,1,32.1,25l-3.81-5.72Z\"/><path d=\"M25.62,25.25h-9a.63.63,0,0,1,0-1.25h9a.63.63,0,1,1,0,1.25Z\"/></svg>",
    "content": "<svg viewBox=\"0 0 49.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M47.62,53.25h-37a.63.63,0,0,1-.62-.63V.62A.62.62,0,0,1,10.62,0h37a1.63,1.63,0,0,1,1.63,1.62v50A1.63,1.63,0,0,1,47.62,53.25ZM11.25,52H47.62a.38.38,0,0,0,.38-.38v-50a.38.38,0,0,0-.38-.37H11.25Z\"/><path d=\"M10.62,53.25h-5A1.63,1.63,0,0,1,4,51.62v-50A1.63,1.63,0,0,1,5.62,0h5a.63.63,0,0,1,.63.62v52A.63.63,0,0,1,10.62,53.25Zm-5-52a.38.38,0,0,0-.37.37v50a.38.38,0,0,0,.37.38H10V1.25Z\"/><path d=\"M4.62,29.44H2.81a2.82,2.82,0,0,1,0-5.63H6.44a.63.63,0,0,1,0,1.25H2.81a1.57,1.57,0,0,0,0,3.13H4.62a.63.63,0,1,1,0,1.25Z\"/><path d=\"M4.62,38.94H2.81a2.82,2.82,0,0,1,0-5.63H6.44a.63.63,0,0,1,0,1.25H2.81a1.57,1.57,0,0,0,0,3.13H4.62a.63.63,0,1,1,0,1.25Z\"/><path d=\"M4.62,48.44H2.81a2.82,2.82,0,0,1,0-5.63H6.44a.63.63,0,0,1,0,1.25H2.81a1.57,1.57,0,0,0,0,3.13H4.62a.63.63,0,1,1,0,1.25Z\"/><path d=\"M4.62,10.44H2.81a2.82,2.82,0,0,1,0-5.63H6.44a.63.63,0,0,1,0,1.25H2.81a1.57,1.57,0,0,0,0,3.13H4.62a.63.63,0,1,1,0,1.25Z\"/><path d=\"M4.62,19.94H2.81a2.82,2.82,0,0,1,0-5.63H6.44a.63.63,0,0,1,0,1.25H2.81a1.57,1.57,0,0,0,0,3.13H4.62a.63.63,0,1,1,0,1.25Z\"/><path d=\"M29.62,16.25a3.63,3.63,0,1,1,3.63-3.63A3.63,3.63,0,0,1,29.62,16.25Zm0-6A2.38,2.38,0,1,0,32,12.62,2.38,2.38,0,0,0,29.62,10.25Z\"/><path d=\"M29.62,20.25a7.63,7.63,0,1,1,7.63-7.63v1a2.63,2.63,0,1,1-5.25,0v-1a.63.63,0,0,1,1.25,0v1a1.38,1.38,0,1,0,2.75,0v-1A6.38,6.38,0,1,0,29.62,19a6.3,6.3,0,0,0,3.94-1.36.63.63,0,0,1,.77,1A7.56,7.56,0,0,1,29.62,20.25Z\"/><path d=\"M42.62,25.25h-17a.63.63,0,0,1,0-1.25h17a.63.63,0,1,1,0,1.25Z\"/><path d=\"M21.62,25.25h-5a.63.63,0,0,1,0-1.25h5a.63.63,0,1,1,0,1.25Z\"/><path d=\"M41.62,29.25h-17a.63.63,0,0,1,0-1.25h17a.63.63,0,1,1,0,1.25Z\"/><path d=\"M20.62,29.25h-4a.63.63,0,0,1,0-1.25h4a.63.63,0,1,1,0,1.25Z\"/><path d=\"M42.62,33.25h-17a.63.63,0,0,1,0-1.25h17a.63.63,0,1,1,0,1.25Z\"/><path d=\"M21.62,33.25h-5a.63.63,0,0,1,0-1.25h5a.63.63,0,1,1,0,1.25Z\"/><path d=\"M40.62,37.25h-17a.63.63,0,0,1,0-1.25h17a.63.63,0,1,1,0,1.25Z\"/><path d=\"M19.62,37.25h-3a.63.63,0,0,1,0-1.25h3a.63.63,0,1,1,0,1.25Z\"/><path d=\"M42.62,41.25h-19a.63.63,0,0,1,0-1.25h19a.63.63,0,1,1,0,1.25Z\"/><path d=\"M19.62,41.25h-3a.63.63,0,0,1,0-1.25h3a.63.63,0,1,1,0,1.25Z\"/><path d=\"M41.62,45.25h-16a.63.63,0,0,1,0-1.25h16a.63.63,0,1,1,0,1.25Z\"/><path d=\"M21.62,45.25h-5a.63.63,0,0,1,0-1.25h5a.63.63,0,1,1,0,1.25Z\"/></svg>",
    "star_doc": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M40,53.25a.62.62,0,0,1-.59-.41l-7.4-20a.62.62,0,0,1,.8-.8l20,7.4a.63.63,0,0,1,.41.59.62.62,0,0,1-.41.58l-9,3.23-3.23,9a.62.62,0,0,1-.58.41ZM33.68,33.68,40,50.8l2.74-7.66a.65.65,0,0,1,.38-.38L50.8,40Z\"/><path d=\"M50.62,37.25a.63.63,0,0,1,0-1.25A1.38,1.38,0,0,0,52,34.62v-32a1.38,1.38,0,0,0-1.38-1.37h-48A1.38,1.38,0,0,0,1.25,2.62v32A1.38,1.38,0,0,0,2.62,36h28a.63.63,0,1,1,0,1.25h-28A2.63,2.63,0,0,1,0,34.62v-32A2.63,2.63,0,0,1,2.62,0h48a2.63,2.63,0,0,1,2.63,2.62v32A2.63,2.63,0,0,1,50.62,37.25Z\"/><path d=\"M32.76,29.32a1.86,1.86,0,0,1-.89-.22l-5-2.62a.65.65,0,0,0-.62,0l-5,2.61a1.92,1.92,0,0,1-2.78-2l.95-5.54a.66.66,0,0,0-.19-.59l-4-3.92a1.91,1.91,0,0,1,1.06-3.26L21.88,13a.68.68,0,0,0,.5-.37l2.48-5a1.93,1.93,0,0,1,3.44,0h0l2.49,5a.64.64,0,0,0,.5.37l5.56.81a1.87,1.87,0,0,1,1.54,1.3,1.9,1.9,0,0,1-.48,2l-4,3.92a.72.72,0,0,0-.19.59l1,5.54a1.92,1.92,0,0,1-1.88,2.24Zm-6.18-4.16a1.86,1.86,0,0,1,.89.22l5,2.61a.66.66,0,0,0,.7,0,.63.63,0,0,0,.26-.65l-.95-5.54A1.93,1.93,0,0,1,33,20.06l4-3.92a.68.68,0,0,0,.17-.69.69.69,0,0,0-.54-.45l-5.56-.81a1.89,1.89,0,0,1-1.44-1l-2.49-5a.68.68,0,0,0-1.19,0l-2.49,5a1.92,1.92,0,0,1-1.44,1L16.49,15a.66.66,0,0,0-.53.45.66.66,0,0,0,.17.69l4,3.92a1.9,1.9,0,0,1,.55,1.69l-.95,5.54a.67.67,0,0,0,1,.7l5-2.61A1.89,1.89,0,0,1,26.58,25.16Z\"/></svg>",
    "shield_bug": "<svg viewBox=\"0 0 53.25 53.25\" fill=\"currentColor\" aria-hidden=\"true\"><path d=\"M26.62,43.25A10.64,10.64,0,0,1,16,32.62v-12A4.63,4.63,0,0,1,20.62,16h12a4.63,4.63,0,0,1,4.63,4.62v12A10.64,10.64,0,0,1,26.62,43.25Zm-6-26a3.37,3.37,0,0,0-3.37,3.37v12a9.38,9.38,0,1,0,18.75,0v-12a3.37,3.37,0,0,0-3.38-3.37Z\"/><path d=\"M32.62,17.25h-12a.63.63,0,0,1-.62-.63,6.63,6.63,0,0,1,13.25,0A.63.63,0,0,1,32.62,17.25ZM21.29,16H32a5.37,5.37,0,0,0-10.67,0Z\"/><path d=\"M26.62,40.25a.63.63,0,0,1-.62-.63v-20a.63.63,0,0,1,1.25,0v20A.63.63,0,0,1,26.62,40.25Z\"/><path d=\"M30.12,12.25a.63.63,0,0,1-.62-.63A3.63,3.63,0,0,1,33.12,8a.63.63,0,1,1,0,1.25,2.38,2.38,0,0,0-2.37,2.37A.63.63,0,0,1,30.12,12.25Z\"/><path d=\"M37,23l-.47,0A.63.63,0,0,1,36,22.3a.61.61,0,0,1,.68-.57,2.89,2.89,0,0,0,3.3-3.3.63.63,0,0,1,.57-.68.62.62,0,0,1,.68.57,4.26,4.26,0,0,1-1.18,3.48A4.17,4.17,0,0,1,37,23Z\"/><path d=\"M42.62,28.75a.65.65,0,0,1-.48-.23,3.19,3.19,0,0,0-5,0,.63.63,0,1,1-1-.79,4.38,4.38,0,0,1,7,0,.62.62,0,0,1-.49,1Z\"/><path d=\"M40.61,37h-.06a.63.63,0,0,1-.57-.68,3,3,0,0,0-.81-2.49A3,3,0,0,0,36.68,33a.63.63,0,1,1-.11-1.25A4.21,4.21,0,0,1,40.05,33a4.26,4.26,0,0,1,1.18,3.48A.63.63,0,0,1,40.61,37Z\"/><path d=\"M16.21,23a4.17,4.17,0,0,1-3-1.2A4.26,4.26,0,0,1,12,18.32a.62.62,0,0,1,.68-.57.63.63,0,0,1,.57.68,2.89,2.89,0,0,0,3.3,3.3.62.62,0,0,1,.68.57.63.63,0,0,1-.57.68Z\"/><path d=\"M16.62,28.75a.65.65,0,0,1-.48-.23,3.19,3.19,0,0,0-5,0,.63.63,0,1,1-1-.79,4.38,4.38,0,0,1,7,0,.62.62,0,0,1-.49,1Z\"/><path d=\"M12.64,37a.63.63,0,0,1-.62-.57,4.15,4.15,0,0,1,4.66-4.66A.63.63,0,0,1,16.57,33a2.89,2.89,0,0,0-3.3,3.3.63.63,0,0,1-.57.68Z\"/><path d=\"M23.12,12.25a.63.63,0,0,1-.62-.63,2.38,2.38,0,0,0-2.38-2.37.63.63,0,0,1,0-1.25,3.63,3.63,0,0,1,3.63,3.62A.63.63,0,0,1,23.12,12.25Z\"/><path d=\"M26.62,53.25A26.63,26.63,0,1,1,53.25,26.62,26.65,26.65,0,0,1,26.62,53.25Zm0-52A25.38,25.38,0,1,0,52,26.62,25.4,25.4,0,0,0,26.62,1.25Z\"/><path d=\"M8.24,45.63a.62.62,0,0,1-.44-.18.61.61,0,0,1,0-.88L44.57,7.8a.62.62,0,1,1,.88.88L8.68,45.45A.62.62,0,0,1,8.24,45.63Z\"/></svg>",
}
ROADMAP_ICON_ORDER = ['audience', 'signpost', 'checklist', 'gears', 'report', 'growth', 'compass', 'megaphone', 'chart_up', 'target', 'analytics', 'content', 'star_doc', 'shield_bug']

def roadmap_step(num, title, body_html, icon_key):
    icon_svg = ROADMAP_ICONS.get(icon_key, "")
    return (
        '<div class="roadmap-step"><span class="roadmap-dot">%s</span>'
        '<div class="roadmap-box"><span class="roadmap-icon">%s</span>'
        '<h3>%s</h3><p>%s</p></div></div>'
        % (num, icon_svg, html.escape(title), body_html)
    )


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
    "seo": '<img class="hero-illustration" src="/assets/img/illustrations/financial-planning.svg" alt="Illustration of an analytics dashboard with rising bar charts, a report screen and a magnifying glass" loading="lazy" decoding="async">',
    "geo": '<img class="hero-illustration" src="/assets/img/illustrations/team-analytics.svg" alt="Illustration of a team reviewing search and AI analytics together at their desks" loading="lazy" decoding="async">',
    "content-writing": '<img class="hero-illustration" src="/assets/img/illustrations/spot/icon-7.svg" alt="Illustration of a person presenting a webpage with an image and text block" loading="lazy" decoding="async">',
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
  <h2>A Malaysian-led digital marketing agency, <em>built on direct access.</em></h2>
  <p>OnceMore Digital is a Malaysian-led digital marketing agency, with a team bringing a combined 10+ years of hands-on experience across SEO, GEO, AI optimisation and content. That experience covers everything from independent local businesses to established international brands, and the same standard applies to each.</p>
  <p style="margin-top:1rem">Being Malaysian-led means Malaysian search behaviour, language and local intent are the starting point, not an afterthought layered on top of a global template. Our focus has always been on helping local businesses compete and win visibility in their own market, though the same expertise applies just as well to international brands entering it.</p>
  <p style="margin-top:1rem">Our biggest strength is simple: the person you talk to about your strategy is the person actually doing the work. No hand-offs, no account managers relaying messages from someone else.</p>
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
  <h2>How we help you <em>get found</em></h2>
  <p>Three services built to work together: SEO to rank on the results page, AIO/GEO to get you cited by AI tools, and content that ties both together, so your customers find you wherever they are searching.</p>
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
  <h2>The same process, <em>every time.</em></h2>
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
      <p>We treat SEO and AIO/GEO as one connected system, not separate line items pulling in different directions.</p>
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
    ("Do you work with small businesses or only large companies?",
     "Both. Our client base has included large brands and independent local businesses, and the same fundamentals apply to each. What changes is the scope of work, not the standard we hold it to."),
    ("Can one team handle SEO, GEO and AI optimisation for my business?",
     "Yes, and there is an advantage to it being one team rather than several. SEO, GEO and AI optimisation share the same foundation, so keeping them under one roof means the strategy stays consistent instead of three vendors pulling a site in different directions."),
    ("Is SEO still worth it now that people search using AI tools?",
     "More than ever. Most AI tools still discover and trust pages through a search engine's index before they cite them, so SEO is the foundation AI visibility gets built on, not something it replaces."),
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
  <p>Digital marketing covers a lot of ground: ads, social media, email, SEO, and not all of it moves the needle for every business. We focus on the channels that reliably improve website traffic and turn it into enquiries, not vanity numbers that look good in a report and do nothing for revenue.</p>
  <p style="margin-top:1rem">Each service below can run on its own, but most businesses see the best results when they work together as one strategy, rather than as four separate vendors pulling in different directions.</p>
  <div class="grid" style="margin-top:2.5rem">%s</div>
</div></section>

<section class="section panel-alt"><div class="container">
  <div class="split">
    <div>
      <span class="eyebrow">How it fits together</span>
      <h2>How each service helps improve your <em>website traffic.</em></h2>
      <p>Digital marketing works best when every channel is pulling toward the same goal. Here is what each one is actually doing for your traffic.</p>
      <ul class="feature-list" style="margin-top:1.75rem">
        <li><strong>SEO</strong> brings in visitors who are already searching for what you offer, the highest-intent traffic there is.</li>
        <li><strong>GEO</strong> captures the growing share of people who ask AI tools a question instead of searching, before they ever reach a results page.</li>
        <li><strong>AI Optimisation</strong> makes sure the traffic you already get lands on pages structured to convert, not just pages that happen to rank.</li>
        <li><strong>Content Writing</strong> fuels both SEO and GEO with the pages and answers that traffic actually needs to find in the first place.</li>
      </ul>
    </div>
    <div class="illustration-frame spot"><img src="/assets/img/illustrations/spot/icon-9.svg" alt="Illustration of a person celebrating in front of a screen with gears, representing channels working together" loading="lazy" decoding="async"></div>
  </div>
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
    if short.isupper() and short not in full_name:
        h1_html = f"{html.escape(full_name)} <em>({short})</em>"
    else:
        words = short.rsplit(" ", 1)
        h1_html = f"<em>{html.escape(short)}</em>" if len(words) == 1 else f"{html.escape(words[0])} <em>{html.escape(words[1])}</em>"
    sections_html = "".join(
        '<h2 style="margin-top:2.25rem">%s</h2>%s' % (html.escape(h), b)
        for h, b in extra.get("sections", []))
    process = extra.get("process")
    if process:
        proc_cards = "".join(
            roadmap_step("%02d" % (i + 1), step_title, step_body, ROADMAP_ICON_ORDER[i % len(ROADMAP_ICON_ORDER)])
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
            '<div class="roadmap">%s</div>%s'
            % (html.escape(process["heading"]), html.escape(process["intro"]), proc_cards, example_html)
        )
    else:
        process_html = ""
    process_section_html = (
        '<section class="section"><div class="container">%s</div></section>' % process_html
    ) if process_html else ""
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
    feature_split = extra.get("feature_split")
    if feature_split:
        heading = feature_split.get("heading", "")
        paragraphs = feature_split.get("paragraphs", [])
        img_tag = (
            '<img src="%s" alt="%s" loading="lazy" decoding="async">'
            % (feature_split["image"], html.escape(feature_split.get("image_alt", "")))
        )
        if heading or paragraphs:
            link_html = ""
            if feature_split.get("link_href"):
                link_html = (
                    '<div class="btn-row" style="justify-content:flex-start;margin-top:1.25rem">'
                    '<a class="btn btn-ghost" href="%s">%s</a></div>'
                    % (feature_split["link_href"], html.escape(feature_split.get("link_text", "Learn more")))
                )
            text_html = "".join(
                '<p style="margin-top:1rem">%s</p>' % p if i > 0 else '<p>%s</p>' % p
                for i, p in enumerate(paragraphs)
            )
            heading_html = ('<h2 style="margin-top:0">%s</h2>' % html.escape(heading)) if heading else ""
            text_block = '<div>%s%s%s</div>' % (heading_html, text_html, link_html)
            frame_class = "illustration-frame spot" if feature_split.get("compact") else "illustration-frame"
            img_block = '<div class="%s">%s</div>' % (frame_class, img_tag)
            pair = (img_block, text_block) if feature_split.get("image_side") == "left" else (text_block, img_block)
            feature_split_html = (
                '<section class="section-sm"><div class="container">'
                '<div class="split">%s%s</div></div></section>'
                % pair
            )
        else:
            # No accompanying text: show the image alone, modestly sized, not stretched full width.
            feature_split_html = (
                '<section class="section-sm"><div class="container">'
                '<div class="illustration-frame" style="max-width:480px;margin:0 auto">%s</div>'
                '</div></section>'
                % img_tag
            )
    else:
        feature_split_html = ""
    all_faqs = list(faqs) + extra.get("faqs", [])
    faq_html, faq_schema = faq_block(all_faqs)
    related_guides = "".join(
        '<li><a href="/resources/%s/">%s</a></li>' % (g["slug"], html.escape(g["title"]))
        for g in RESOURCES)

    def _alt(section_html, alt):
        """Insert panel-alt into a block's outer <section> tag when alt=True."""
        if not alt or not section_html:
            return section_html
        return section_html.replace('<section class="section-sm">', '<section class="section-sm panel-alt">', 1) \
                            .replace('<section class="section">', '<section class="section panel-alt">', 1)

    layout = extra.get("layout")
    if layout:
        sections_by_heading = {h: (h, b) for h, b in extra.get("sections", [])}
        blocks = []
        for i, item in enumerate(layout):
            t = item["type"]
            # Force strict alternation between plain and panel-alt bands,
            # regardless of what content.py specifies. Two same-background
            # sections back to back just look like a dead, unexplained gap
            # (padding stacks with nothing to visually justify it); a forced
            # alternation always turns that space into a legible panel break.
            alt = bool(i % 2)
            divider = '<div class="divider left" aria-hidden="true"></div>' if i == 0 else ""
            if t == "prose":
                group_html = "".join(
                    '<h2 style="margin-top:2.25rem">%s</h2>%s' % (html.escape(h), b)
                    for h, b in (sections_by_heading[hd] for hd in item["headings"] if hd in sections_by_heading)
                )
                blocks.append(_alt(
                    '<section class="section"><div class="container">%s<div class="prose">%s</div></div></section>'
                    % (divider, group_html), alt))
            elif t == "process":
                blocks.append(_alt(process_section_html, alt))
            elif t == "feature_split":
                blocks.append(_alt(feature_split_html, alt))
            elif t == "tools":
                blocks.append(_alt(tools_html, alt))
            elif t == "faq":
                blocks.append(_alt(faq_html, alt))
        middle_html = "\n".join(blocks)
        last_alt = bool((len(layout) - 1) % 2)
    else:
        included_html = f"""<section class="section-sm"><div class="container">
  <span class="eyebrow">What's included</span>
  <h2>Everything in this service</h2>
  <ul class="feature-list">{fl}</ul>
</div></section>"""
        fallback_blocks = [
            '<section class="section"><div class="container">'
            '<div class="divider left" aria-hidden="true"></div>'
            f'<div class="prose"><p>{html.escape(intro)}</p>{sections_html}</div>'
            '</div></section>',
            feature_split_html,
            process_section_html,
            included_html,
            tools_html,
            faq_html,
        ]
        blocks = []
        i = 0
        for raw in fallback_blocks:
            if not raw:
                continue
            blocks.append(_alt(raw, bool(i % 2)))
            i += 1
        middle_html = "\n".join(blocks)
        last_alt = bool((i - 1) % 2) if i else False

    body = f"""
<section class="section service-hero"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/services/">Services</a> / {short}</nav>
  <div class="service-hero-grid">
    <div>
      <div class="svc-icon">{ICONS[slug]}</div>
      <span class="eyebrow" style="margin-top:0">{html.escape(full_name)}</span>
      <h1>{h1_html}</h1>
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

{middle_html}

<section class="section-sm{" panel-alt" if not last_alt else ""}"><div class="container">
  <span class="eyebrow">Related reading</span>
  <h2>Go deeper</h2>
  <ul class="link-list">{related_guides}</ul>
</div></section>
<section class="section-sm{" panel-alt" if last_alt else ""}"><div class="container">
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

# ---------------------------------------------------------------- legacy redirect
# AI Optimisation and GEO were merged into one service (AIO/GEO) at
# /services/geo/. GitHub Pages has no server-side 301s, so this is the
# standard static-site workaround: meta-refresh + canonical + noindex.
# Kept here (rather than deleted) so old links, bookmarks and any existing
# search results still land somewhere useful instead of a 404.
_redirect_target = "/services/geo/"
_redirect_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={_redirect_target}">
<link rel="canonical" href="{URL}{_redirect_target}">
<meta name="robots" content="noindex, follow">
<title>AI Optimisation is now part of AIO/GEO | OnceMore Digital</title>
{GTM_HEAD}
</head>
<body>
{GTM_BODY}
<p>AI Optimisation and GEO are now one service, AIO/GEO. Redirecting to <a href="{_redirect_target}">{URL}{_redirect_target}</a>&hellip;</p>
</body>
</html>
"""
_redirect_path = os.path.join(SITE, "services", "ai-optimisation", "index.html")
os.makedirs(os.path.dirname(_redirect_path), exist_ok=True)
with open(_redirect_path, "w", encoding="utf-8") as f:
    f.write(_redirect_body)
print("Redirect written: /services/ai-optimisation/ -> /services/geo/")

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
  <p>The way people find businesses is changing. Some still type into Google. More are starting to ask AI tools for a recommendation. We work across both, combining solid SEO fundamentals with newer GEO and AI optimisation work, so your visibility holds up as habits shift.</p>
  <p style="margin-top:1rem">We keep things straight. Recommendations are grounded in real data, reporting is written so you can actually understand it, and we tell you what is worth doing rather than selling work for its own sake.</p>
</div></section>

<section class="section panel-alt"><div class="container">
  <div class="split story-split">
    <div class="photo-frame">
      <img src="/assets/img/about/team-meeting.jpg" alt="OnceMore Digital team presenting website traffic data to a client during a strategy session in a Kuala Lumpur meeting room" loading="lazy" decoding="async">
    </div>
    <div>
      <span class="eyebrow">How we work</span>
      <h2>Less deck, <em>more actual conversation.</em></h2>
      <p>A lot of agencies show you a slide deck once a quarter and go quiet until renewal. We would rather be in the room walking through the numbers with you, which is what most of our client meetings actually look like.</p>
      <p style="margin-top:1rem">Every account gets a monthly call with the people doing the actual work on it, not a summary read back by someone who was not in the room. If something is not working, you hear that directly, along with what we are changing about it.</p>
    </div>
  </div>
</div></section>

<section class="section"><div class="container">
  <span class="eyebrow">Behind the scenes</span>
  <h2>A small team, <em>not a factory.</em></h2>
  <p>OnceMore Digital is run by a small team, and that is deliberate. We would rather stay small enough that everyone on an account actually knows the business, than grow past the point where your project becomes a ticket in a queue.</p>
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
  <h2>The stuff we <em>will not compromise on.</em></h2>
  <p>None of this is a mission statement for the wall. It is just what we have found actually matters once you are the one paying for the work.</p>
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
        roadmap_step(str(i + 1), t, b, ROADMAP_ICON_ORDER[i % len(ROADMAP_ICON_ORDER)])
        for i, (t, b) in enumerate(c["approach_items"]))
    # Ring angles are decorative variety, not a literal 0-100% mapping (the
    # stats themselves are percentages that can exceed 360 degrees of meaning).
    _ring_degs = [258, 292, 232, 306, 270]
    _stat_icons = ["growth", "chart_up", "analytics", "target", "report"]
    stat_cards = "".join(
        '<div class="stat-card"><span class="stat-icon">%s</span>'
        '<span class="stat-ring" style="--ring-deg:%ddeg"></span>'
        '<span class="stat-num">%s</span><span class="stat-label">%s</span></div>'
        % (ROADMAP_ICONS[_stat_icons[i % len(_stat_icons)]], _ring_degs[i % len(_ring_degs)], html.escape(n), html.escape(l))
        for i, (n, l) in enumerate(c["stats"]))
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

    # Optional hero banner: a real photo of the client, linked out to a
    # page on their own site. This doubles as a backlink for the client.
    banner_html = ""
    banner = c.get("banner")
    if banner:
        b_src, b_alt, b_href = banner["src"], banner["alt"], banner["href"]
        banner_html = f"""
  <a class="case-banner" href="{b_href}" target="_blank" rel="noopener">
    <img src="{b_src}" alt="{html.escape(b_alt)}" loading="lazy" decoding="async">
  </a>"""

    cbody = f"""
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/case-studies/">Case Studies</a> / {html.escape(c["title"])}</nav>
  <span class="case-tag" style="margin-top:1.25rem">{html.escape(c["industry"])}</span>
  <h1>{html.escape(c["h1"])}</h1>
  <p class="case-byline"><span>Written by Walter Yow, co-founder of OnceMore Digital</span><span class="case-byline-date">Published {html.escape(c.get("published", ""))}</span></p>
  <p class="lead">{html.escape(c["intro"])}</p>
  <div class="divider left" aria-hidden="true"></div>{banner_html}
  <nav class="toc" aria-label="On this page">
    <p class="toc-title">On this page</p>
    <ul>{toc_html}</ul>
  </nav>
  <article>
    {sections_html}
    <h2 id="{_case_sid(c["approach_heading"])}" style="margin-top:2.5rem">{html.escape(c["approach_heading"])}</h2>
    <p class="lead" style="font-size:1.05rem;max-width:62ch;margin-bottom:1.75rem">{html.escape(c["approach_intro"])}</p>
    <div class="roadmap">{approach_cards}</div>
    <h2 id="{_case_sid(c["results_heading"])}" style="margin-top:2.5rem">{html.escape(c["results_heading"])}</h2>
    <div class="stat-grid">{stat_cards}</div>
    {charts_html}
    <div class="prose" style="margin-top:1.5rem">{results_html}</div>
  </article>
</div></section>"""

    # Optional review/testimonial panel: deliberately its own full-width
    # section (not nested inside the article container above) so it reads
    # as a distinct, wide panel rather than another card in the grid.
    review = c.get("review")
    if review:
        cbody += f"""
<section class="section-sm review-panel"><div class="container">
  <div class="review-card">
    <span class="review-mark" aria-hidden="true">&ldquo;</span>
    <blockquote class="review-quote">{html.escape(review["quote"])}</blockquote>
    <div class="review-attribution">
      <span class="review-name">{html.escape(review["name"])}</span>
      <span class="review-role">{html.escape(review["role"])}</span>
    </div>
  </div>
</div></section>"""

    if takeaway_html:
        cbody += f"""
<section class="section"><div class="container">
  <article>
    {takeaway_html}
  </article>
</div></section>"""

    cbody += """
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
    article_ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": c["title"], "description": c["desc"],
        "url": URL + "/case-studies/%s/" % c["slug"],
        "inLanguage": "en-MY",
        "about": c["industry"],
        "datePublished": c.get("date_published", "2026-07-22"),
        "dateModified": c.get("date_modified", c.get("date_published", "2026-07-23")),
        "author": {"@type": "Person", "name": "Walter Yow", "url": URL + "/about/"},
        "publisher": {"@type": "Organization", "name": "OnceMore Digital",
                      "logo": {"@type": "ImageObject", "url": OG_IMAGE}},
    }
    if banner:
        article_ld["image"] = URL + banner["src"]
    if c.get("client_org"):
        article_ld["mentions"] = {
            "@type": "Organization",
            "name": c["client_org"]["name"],
            "url": c["client_org"]["url"],
        }
    cschema = [
        breadcrumb([("Home", "/"), ("Case Studies", "/case-studies/"),
                    (c["title"], "/case-studies/%s/" % c["slug"])]),
        jsonld(article_ld),
    ]
    # Note: deliberately NOT emitting Review/AggregateRating structured data
    # here. A testimonial about our own service, published on our own site,
    # is a self-serving review under Google's structured data guidelines and
    # is not eligible for review rich results regardless of itemReviewed
    # type (Service is not even a supported type for that field, which is
    # what previously surfaced as an "invalid item" error in Search Console).
    # The testimonial itself still renders normally on the page via the
    # review-panel HTML above; this only removes the (invalid, disallowed)
    # schema wrapper around it.
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

# ---------------------------------------------------------------- auto structure snapshot
# Derived directly from SERVICES / RESOURCES / CASE_STUDIES every time this
# script runs (which is a mandatory step for every content or code change),
# so this file cannot silently drift out of date the way a hand-written
# summary can. Treat this as the authoritative page/content inventory;
# HANDOFF.md's prose sections (design system, workflow, voice rules) still
# need a manual pass when those actually change, but the *structure* facts
# below never do.
def _write_structure_snapshot():
    lines = []
    lines.append("# Site Structure Snapshot (auto-generated by generate.py — do not hand-edit)")
    lines.append("")
    lines.append("Regenerated every time `python generate.py` runs. If this file and HANDOFF.md")
    lines.append("ever disagree on page counts, services, resources, or case studies, this file")
    lines.append("is correct and HANDOFF.md needs a refresh.")
    lines.append("")
    fixed_pages = [("Home", "/"), ("Services hub", "/services/"),
                   ("Resources hub", "/resources/"), ("Case studies hub", "/case-studies/"),
                   ("About", "/about/"), ("Contact", "/contact/"),
                   ("HTML sitemap", "/sitemap/"), ("404", "/404.html")]
    total_pages = len(fixed_pages) + len(SERVICES) + len(RESOURCES) + len(CASE_STUDIES)
    lines.append(f"**Total pages: {total_pages}** "
                 f"({len(SERVICES)} services, {len(RESOURCES)} resources, "
                 f"{len(CASE_STUDIES)} case studies, plus {len(fixed_pages)} fixed pages: "
                 + ", ".join(name for name, _ in fixed_pages) + ")")
    lines.append("")
    lines.append("## Services")
    for s in SERVICES:
        slug, short = s[0], s[1]
        extra = SERVICE_CONTENT.get(slug, {})
        flags = [k for k in ("process", "tools", "feature_split", "layout", "sources") if extra.get(k)]
        lines.append(f"- `/services/{slug}/` — {short}" + (f" (has: {', '.join(flags)})" if flags else ""))
    lines.append("")
    lines.append("## Resources")
    for g in RESOURCES:
        flags = " (has: sources)" if g.get("sources") else ""
        lines.append(f"- `/resources/{g['slug']}/` — {g['title']}{flags}")
    lines.append("")
    lines.append("## Case studies")
    for c in CASE_STUDIES:
        flags = [k for k in ("banner", "review", "client_org", "charts") if c.get(k)]
        lines.append(f"- `/case-studies/{c['slug']}/` — {c['industry']}"
                      + (f" (has: {', '.join(flags)})" if flags else ""))
    lines.append("")
    lines.append("## Fixed pages")
    for name, path in fixed_pages:
        lines.append(f"- `{path}` — {name}")
    build_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(build_dir, "STRUCTURE.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

_write_structure_snapshot()
print("STRUCTURE.md snapshot written.")
