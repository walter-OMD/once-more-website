# OnceMore Digital

Static marketing site for OnceMore Digital. Plain HTML, CSS and a little JavaScript, ready to host on GitHub Pages with a custom domain. No build step is needed to serve it.

## Pages

| URL | File |
|-----|------|
| `/` | `index.html` |
| `/services/` | `services/index.html` |
| `/services/seo/` | `services/seo/index.html` |
| `/services/geo/` | `services/geo/index.html` |
| `/services/ai-optimisation/` | `services/ai-optimisation/index.html` |
| `/services/content-writing/` | `services/content-writing/index.html` |
| `/services/google-ads/` | `services/google-ads/index.html` |
| `/about/` | `about/index.html` |
| `/contact/` | `contact/index.html` |
| 404 | `404.html` |

Each page uses a folder + `index.html` so GitHub Pages serves clean URLs (for example `/services/seo/`).

## SEO built in

- Unique title, meta description and canonical on every page
- Open Graph and Twitter card tags
- JSON-LD schema per page: Organization, WebSite and ProfessionalService on the home page, Service and BreadcrumbList on service pages, FAQPage where there are questions, AboutPage and ContactPage on the relevant pages
- `sitemap.xml` and `robots.txt`
- `site.webmanifest`
- Semantic HTML, heading order, alt text, keyboard focus styles and reduced-motion support

## Preserved from the original

- Google Tag Manager (`GTM-MJ5WCPR6`) in the head and the `noscript` body tag on every page
- The `og:image` now points at your existing `oncemoredigial-seo-marketing-logo.jpg` at the site root (the original markup pointed at a `.png` that did not exist, so this also fixes the broken share image)
- The design system: blue `#4d65af`, dark `#0a0a0a`, Barlow, the radial-gradient background and the rise animation

## Replace before launch

The logo, favicon and apple touch icon are placeholder brand marks (a blue "OM" monogram), since the originals were embedded inline and could not be carried over. Swap these files with your real artwork, keeping the same names and paths:

- `assets/img/logo.png` (header logo)
- `assets/img/favicon.png` (32x32)
- `assets/img/apple-touch-icon.png` (180x180)

The social share image uses your existing `oncemoredigial-seo-marketing-logo.jpg` at the site root. For best results that file should be roughly 1200x630.

The contact form has no backend yet. On submit it opens the visitor's email client addressed to `walter@oncemoredigital.com`, so nothing is lost. Connect a form service (Formspree, Netlify Forms, Google Forms) when ready.

## Deploy on GitHub Pages

1. Push this folder to a GitHub repository.
2. In the repo, go to Settings, Pages, and set the source to the `main` branch, root.
3. The `CNAME` file points the site at `oncemoredigital.com`. Add the matching DNS records at your domain provider, then enable HTTPS in the Pages settings.

## Editing

The HTML pages were produced by `build/generate.py`, which keeps the header, footer and meta tags consistent across pages. Edit the generator and re-run it to regenerate all pages, or edit the HTML files directly for one-off changes. The `build/` folder is for development only and does not need to be served.
