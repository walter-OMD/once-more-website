"""Builds the OnceMore Digital static site.
Each page gets its own title, meta description, canonical, Open Graph,
Twitter card and JSON-LD schema. GTM and the og:image path are preserved
exactly from the original markup. Output is plain static HTML for GitHub Pages.
"""
import os, json, html

SITE = "/home/claude/site"
URL = "https://www.oncemoredigital.com"
EMAIL = "walter@oncemoredigital.com"
GTM = "GTM-MJ5WCPR6"
OG_IMAGE = URL + "/oncemoredigial-seo-marketing-logo.png"  # path preserved from original

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
  <a class="brand" href="/"><img src="/assets/img/logo.png" alt="OnceMore Digital logo" width="38" height="38"><span>OnceMore Digital</span></a>
  <button class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="nav-links">&#9776;</button>
  <ul class="nav-links" id="nav-links">
    <li><a href="/"{home}>Home</a></li>
    <li><a href="/services/"{services}>Services</a></li>
    <li><a href="/about/"{about}>About</a></li>
    <li><a href="/contact/"{contact}>Contact</a></li>
    <li><a class="nav-cta" href="mailto:%s">Get in Touch</a></li>
  </ul>
</nav></div></header>""" % EMAIL

FOOTER = """<footer class="site-footer"><div class="container">
  <div class="footer-grid">
    <div class="footer-brand">
      <a class="brand" href="/"><img src="/assets/img/logo.png" alt="OnceMore Digital logo" width="38" height="38"><span>OnceMore Digital</span></a>
      <p>SEO, GEO, AI optimisation, content and Google Ads for businesses in Malaysia.</p>
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

<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">

<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="OnceMore Digital">
<meta property="og:locale" content="en_MY">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="OnceMore Digital">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{OG_IMAGE}">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,300;0,400;0,600;1,300&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,300;0,400;0,600;1,300&display=swap"></noscript>
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
      "Monthly reporting in plain language"],
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

# ---------------------------------------------------------------- home page
home_body = """
<section class="hero"><div class="container">
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
  <div class="divider" aria-hidden="true"></div>
  <div class="btn-row">
    <a class="btn btn-primary" href="/contact/">Get in Touch</a>
    <a class="btn btn-ghost" href="/services/">See What We Do</a>
  </div>
</div></section>

<section class="section"><div class="container">
  <span class="eyebrow">What we do</span>
  <h2>Five ways we help you grow</h2>
  <p>Each service stands on its own or works together as one organic growth plan.</p>
  <div class="grid" style="margin-top:2rem">
    %s
  </div>
</div></section>

<section class="section-sm"><div class="container split">
  <div>
    <span class="eyebrow">Why OnceMore</span>
    <h2>Built for how search <em>works now.</em></h2>
    <p>Search is splitting between Google's results and AI answer engines. We work across both, so your business stays visible no matter where your customers look.</p>
  </div>
  <ul class="feature-list">
    <li>Clear reporting written in plain language, not jargon</li>
    <li>Work grounded in real data, not guesswork</li>
    <li>One team across SEO, content and paid</li>
    <li>Focused on Malaysian businesses and audiences</li>
  </ul>
</div></section>

<section class="section"><div class="container">
  <div class="cta-band">
    <h2>Ready to get found?</h2>
    <p>We are launching soon. Tell us what you are working on and we will be in touch.</p>
    <div class="btn-row"><a class="btn btn-primary" href="/contact/">Start the conversation</a></div>
  </div>
</div></section>
""" % "".join(
    '<a class="card" href="/services/%s/"><span class="num">0%d</span><h3>%s</h3><p>%s</p><span class="more">Learn more &rarr;</span></a>'
    % (s[0], i + 1, s[1], s[3]) for i, s in enumerate(SERVICES)
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

home_schema = [
    jsonld({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "OnceMore Digital",
        "url": URL,
        "email": EMAIL,
        "logo": URL + "/assets/img/logo.png",
        "description": "SEO, GEO, AI optimisation, content writing and Google Ads for businesses in Malaysia.",
        "areaServed": {"@type": "Country", "name": "Malaysia"},
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
hub_cards = "".join(
    '<a class="card" href="/services/%s/"><span class="num">0%d</span><h3>%s</h3><p>%s</p><span class="more">Learn more &rarr;</span></a>'
    % (s[0], i + 1, s[1], s[3]) for i, s in enumerate(SERVICES)
)
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
    others = "".join(
        '<a class="card" href="/services/%s/"><h3>%s</h3><p>%s</p><span class="more">Learn more &rarr;</span></a>'
        % (s[0], s[1], s[3]) for s in SERVICES if s[0] != slug
    )
    fl = "".join("<li>%s</li>" % f for f in features)
    faq_html, faq_schema = faq_block(faqs)
    body = f"""
<section class="section"><div class="container">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/services/">Services</a> / {short}</nav>
  <span class="eyebrow" style="margin-top:1.5rem">{html.escape(full_name)}</span>
  <h1>{html.escape(short)}</h1>
  <p class="lead">{html.escape(tagline)}</p>
  <div class="divider left" aria-hidden="true"></div>
  <p style="max-width:65ch">{html.escape(intro)}</p>
  <h2 style="margin-top:2.5rem">What is included</h2>
  <ul class="feature-list">{fl}</ul>
  <div class="btn-row" style="justify-content:flex-start;margin-top:1.5rem">
    <a class="btn btn-primary" href="/contact/">Enquire about {html.escape(short)}</a>
  </div>
</div></section>
{faq_html}
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
  <p style="max-width:65ch;margin-top:1rem">We keep things straight. Recommendations are grounded in real data, reporting is written in plain language, and we tell you what is worth doing rather than selling work for its own sake.</p>
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
"""
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
  <p class="lead">We are launching soon. Tell us what you are working on and we will get back to you.</p>
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
      <p>Businesses across Malaysia.</p>
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
    }),
]
page("/contact/", "Contact | OnceMore Digital",
     "Get in touch with OnceMore Digital. Email walter@oncemoredigital.com or send a message and we will be in touch about your SEO, GEO and digital marketing goals.",
     contact_body, active="contact", schema_blocks=contact_schema)

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
