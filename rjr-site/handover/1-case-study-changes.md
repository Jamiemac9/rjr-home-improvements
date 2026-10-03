# Case study notes: RJR Home Improvements website

Built by APX Digital. Source notes for writing the case study. Everything below is factual and was measured on the finished build unless marked "not yet measured".

## The client

- RJR Home Improvements (R.J.R Home Improvements Ltd), a family-run roofing, bricklaying and building business in Birmingham and the West Midlands.
- 45 years' combined experience. Rated "Excellent" from 127 ratings on Rated People.

## The brief

- A website that brings in local roofing work across Birmingham, with pages for specific areas (Edgbaston, Kings Heath, Moseley, Solihull, Shirley, Hall Green and nearby).
- Content that ranks in Google and gets picked up by AI answer tools (ChatGPT, Google AI answers and similar).
- A design that doesn't look like a template: strong type, strict layout, no rounded cards or stock layouts.
- Use only what the client supplied: their About text, service list, five reviews and 11 job photos. Nothing invented.

## What was delivered

| Item | Detail |
|---|---|
| Pages | 111 indexable pages (after the round 10 refocus on Bromsgrove, Rubery & Rednal) |
| Breakdown | Home, contact, services index, 8 roofing service pages, 2 grouped trade pages, areas index, 13 area pages, 78 area-and-service pages, before & after, reviews, about, privacy, cookie, sitemap |
| Lead offer | Emergency roof repairs, storm damage and roof leaks |
| Main call to action | Quote form on every page (dropdowns + details) that opens WhatsApp with a structured message, pre-set for that page's service and area. Originally a direct WhatsApp link with a message already filled in for that page (e.g. "Hi RJR, I'm in Moseley (B13) and need help with roof leak repairs.") |
| Reviews | Linked to the Google Business Profile and Rated People; reviews shown word for word |
| Questions answered | 229 different questions answered across the site |
| Typical page length | About 800 words of real content (median) |
| Legal | Cookie consent banner, privacy policy, cookie policy |
| Handover | Full source code, set up for editing in Cursor, with a README and design rules file |

## How it changed, round by round

### Round 1: first build
- Three font pairing options supplied; the build used Archivo (headings) with IBM Plex Sans and Plex Mono.
- Type sizes scale smoothly between phone and desktop on a fixed ratio, rather than jumping at breakpoints.
- Left-aligned layout, heavy rules between sections, no rounded corners, shadows or gradients.
- Landing page, service pages, area pages, sitemaps.
- No phone number, email or Google link had been supplied, so none were made up. The quote button went to Rated People as a stop-gap.

### Round 2: client feedback
Feedback: more colour and pictures; a blurred photo behind the hero; before and after photos paired properly; link the Google profile; WhatsApp as the main contact; focus on emergency work.

Changes:
- Blurred job photo behind the hero, with a dark overlay so the text stays readable.
- Photo thumbnails on every service row. Colour-blocked sections.
- **Photo pairing corrected.** Two pairs had been labelled wrongly in round 1:
  - One pair was labelled as a porch roof job. It was actually new white fascias, bargeboards and gutters, which is clear from the black trims in the "before" and white in the "after" on the same house.
  - One photo was labelled as flat roof work. It actually showed the verge of the same grey-tile re-roof as another photo.
  - All pairs were then checked against fixed details (same windows, same nameplate, same chimney shape).
- WhatsApp button on every page, in the header, and in a bar fixed to the bottom of the screen on phones.
- Google Business Profile linked across the site.
- Three emergency services added (emergency repairs, storm damage, leaks), each with a page for all 10 areas.
- A "What to do right now" guide for a leaking roof (contain the water, keep clear, take photos, message us).

### Round 3: client feedback
Feedback: needs cookie consent and a privacy policy; pages feel thin and repetitive; too much repetition of reviews, calls to action and FAQs; colours inconsistent between pages; highlight boxes overlapping text; some images broken; needs to load fast; add an APX Digital credit; must be ready to hand into Cursor.

Changes:
- **Cookie consent**: "Accept analytics" and "Reject" buttons given equal weight, a "Cookie settings" link on every page, and no tracking unless accepted.
- **Privacy and cookie policies** written for a UK limited company: what's collected, why, who it's shared with (including WhatsApp and Google Fonts), how long it's kept, and the right to complain to the ICO.
- **Content rebuilt for depth:**
  - Each main service page now covers causes, materials and options, the process step by step, what affects the price, repair or replace, prevention, and 4–5 specific FAQs.
  - Each area is described by its real housing: slate or concrete tiles, shared chimneys, back-addition valleys, flat-roofed garages, conservation areas. Area pages are built from advice that matches that housing, so a Moseley leak page and a Shirley leak page give genuinely different advice.
- **Less repetition.**
  - Page count went from 131 to 94. Thin one-line pages (thatch, pizza ovens, etc.) were merged into three trade pages, and each area has 6 service pages instead of 9.
  - Wording shared between area pages fell from 50–60% to about 45% on average, measured by comparing five-word phrases across pages.
  - Full review lists now appear only on the home and reviews pages; other pages show one short quote, which varies by area.
  - Every page ends with its own headline, e.g. "Roof leak repairs in Moseley? Send a photo."
- **Colour locked to four:** black, light, orange and neon, used the same way on every page. Orange marks urgency, neon marks the main action.
- **Highlight boxes removed.** Emphasis is now coloured text, so nothing overlaps.
- **Broken images fixed.** Links had started at the site root, which breaks when a page is opened as a file or hosted in a sub-folder. All links are now relative.
- **Speed**: see the figures below.
- "Website by APX Digital" in every footer.
- Cursor-ready project: README, a rules file that keeps the design and content rules in place when AI edits the code, and one command to rebuild.

### Round 4: client feedback
Feedback: the photos set into the hero headline didn't suit; the hero background wasn't the latest image.

Changes:
- Photos removed from the headline.
- Home hero background changed to the photo the client supplied last (the gable-fronted house), with a lighter blur and lighter overlay so the house is recognisable behind the text.

### Round 5: domain and preview
- Domain set to rjrhomeimprovements.com. Every page's canonical link, the sitemaps, robots.txt, social previews, structured data and llms.txt now use it. www redirects to the main domain.
- "Error response 404" in the nav was traced to an old preview server still pointing at a deleted build folder. Fix: a one-command preview (`python3 serve.py`), Cursor Live Server settings, and a full link check. All 94 pages are reachable through the site's own links, 151 URLs checked, zero 404s, both at the site root and from a sub-folder.

### Round 6: demo mode and local preview
- Demo mode added. While the site is on a free Netlify or Cloudflare address, every page is hidden from search engines and robots.txt blocks crawlers. Switching it off at launch is one line.
- Local preview error ("ERR_EMPTY_RESPONSE" on localhost:8080) traced to port 8080 already being used by two other programs on the Mac: the Hermes agent and an old test server. The preview script now finds a free port itself, prints the exact address, and opens it. Cursor's Live Server was moved to port 5500.

### Round 7: quote form
Feedback: needs a contact form with dropdowns that customers fill in before it goes to WhatsApp pre-filled.

Changes:
- Quote form on every page, plus a new Contact page (95 pages in total). Dropdowns: service, urgency, area, property type, reply method, best time. Text fields: name, postcode (checked and tidied, e.g. "b139ab" becomes "B13 9AB") and what's happening.
- Pressing **Continue to WhatsApp** opens WhatsApp with a structured message: service, urgency, name, postcode, area, property, details, reply preference, and the page it came from. The customer adds photos and sends.
- Each page pre-selects its own service and area, and "Emergency" on emergency pages. The "Report an emergency" and "Leak or storm damage?" links set urgency to Emergency before jumping to the form.
- No data goes to a server: the form has no backend and its fields have no submit names, so even with JavaScript off nothing is sent. The privacy policy was updated to say so.
- All "WhatsApp a photo" buttons, the header button and the mobile bar now go to the form ("Get a quote"). Call links still dial directly, and a plain "Open WhatsApp directly" link remains.
- Checked: empty submits are blocked with the missing fields highlighted; all 95 pages have exactly one form; no overflow at 360px; 153 URLs crawled with zero 404s.

### Round 8: company details and backup
- Companies House number 13349077 added to the footer, the privacy policy, the structured data (as the company identifier) and llms.txt.
- Source code backed up to a private GitHub repository (Jamiemac9/rjr-home-improvements), with each change committed separately.

### Round 9: sticky header (made in Cursor, PR #1)
- The header stays on screen, shortens after a short scroll, and collapses into a Menu button on small screens. Without JavaScript the full nav still shows.
- The key facts panel was removed from the home page hero to keep the first screen focused on the headline and the quote button.
- Checked afterwards with the new site check (`tools/check_site.py`): 95 pages, 153 URLs, no broken links, one form and one heading per page.

### Round 10: new area focus, brand and services
Feedback: move the focus from Birmingham to Bromsgrove, Rubery, Rednal and up to 20 miles around; use the RJR logo and its red-and-white colours; link the active Google Business Profile; remove "Powered by Netlify"; drop zinc/metal and thatched roofs, Velux windows, roof cleaning and roof insulation; merge guttering with fascias and soffits; use the new photos accurately; keep pages useful and specific; update the form.

Changes:
- **Areas rebuilt.** 13 areas within 20 miles of Bromsgrove: Bromsgrove, Rubery, Rednal, Barnt Green & Lickey, Catshill, Alvechurch, Longbridge & Northfield, Kings Norton, Hagley, Halesowen, Redditch, Droitwich Spa, and Wythall & Hollywood. Each names its own planning council (Bromsgrove, Birmingham, Redditch, Wychavon or Dudley), and the split ones (Rubery, Wythall) say so.
- **Two new local housing types.** Exposed ground near the Lickey and Clent Hills, and 1960s–80s new-town estates (Redditch, Droitwich). Each comes with specific questions and answers per service, so every area-and-service page has at least three local answers. Wording shared between area pages now averages about 42% across all 13 areas and 6 services (highest pair 70%, between areas with near-identical housing), down from about 45%.
- **Search signals moved to Bromsgrove.** Titles, descriptions, structured data (service area set as a 20-mile circle round Bromsgrove), geo tags, sitemaps and llms.txt. The old Birmingham URLs redirect (301) to the nearest new page.
- **Brand.** The client's logo in the header and footer; a matching favicon drawn from the logo's gable; colours changed from black/orange/neon to the logo's red and white with charcoal, and gentle colour transitions on links and buttons.
- **Services.** Five removed from the site, menus, form and schema (still in the business's own trade list but not promoted). Guttering and downpipes merged with fascias, soffits and bargeboards into one roofline page. Velux, cleaning and insulation URLs redirect to roof repairs.
- **New photos placed by what they show.** Extension re-roof (during and after, same house) on roof repairs; the large felt flat roof (two views) on flat roofs; the chimney lead flashing on leadwork, chimneys and roof leaks; the RJR van on the about and areas pages.
- **"Powered by Netlify" removed.** It came from a script Netlify injects into hosted pages, not from the site. A Content Security Policy header now only allows scripts from the site's own files, which blocks it.
- **Form.** Service list matches the new services; area list matches the new areas plus "Elsewhere within 20 miles of Bromsgrove". The mobile menu was checked: opens, closes, and its links work.
- Checked: 111 pages, 195 URLs, 0 broken links, one form and one heading per page, 0 pages wider than a 360px phone.

## Measured results (finished build)

| Measure | Figure |
|---|---|
| Home page HTML (compressed) | 10 KB |
| Stylesheet (compressed) | 7 KB |
| JavaScript | Two small files, under 7 KB together (cookie consent + sticky header, and the quote form) |
| Home hero background image | 18 KB |
| Original photos supplied | 17 photos plus the logo (11 in September, 6 in October) |
| Typical photo as served | 78 KB (720px WebP; phones download the smallest size that fits) |
| Pages that scroll sideways on a 360px phone | 0 of 111 |
| Broken links or images | 0 (195 URLs crawled over HTTP) |
| Pages with invalid structured data | 0 |
| Duplicate page titles or descriptions | 0 |

Not yet measured: Lighthouse / PageSpeed scores on the live host, Google rankings, enquiries. Add these after launch; the site isn't live yet.

## Search and AI-answer groundwork

- Every page opens with a direct answer to the main question, so it can be quoted.
- Structured data on every page tells Google it's a roofing contractor, which services it offers, which areas it covers, the page's place in the site, and its FAQs.
- An `llms.txt` file gives AI tools a plain summary: services, areas, verbatim reviews and contact details.
- Sitemaps are split into core, services and areas.
- Page titles are all under 70 characters and all unique.

## Honesty rules the site follows

- No invented prices, response times, "24/7", guarantees, accreditations, insurance claims or job counts.
- The only speed claim is a customer's own words: "Ryan got in touch really quickly and came round a few hours later."
- Planning and legal guidance is general and hedged ("may need consent", "check with the council").

## Still needed before launch

- Buy rjrhomeimprovements.com and point it at the host.
- Client to confirm the registered office (246 Court Oak Road, Birmingham B32 2EG, from Companies House) now shown in the privacy policy.
- The business to read and approve the privacy policy.
