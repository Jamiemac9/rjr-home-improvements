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
| Pages | 95 indexable pages (94 + Contact, added in round 7) |
| Breakdown | Home, services index, 12 roofing service pages, 3 grouped trade pages, areas index, 10 area pages, 60 area-and-service pages, before & after, reviews, about, privacy policy, cookie policy, sitemap |
| Lead offer | Emergency roof repairs, storm damage and roof leaks |
| Main call to action | Quote form on every page (dropdowns + details) that opens WhatsApp with a structured message, pre-set for that page's service and area. Originally a direct WhatsApp link with a message already filled in for that page (e.g. "Hi RJR, I'm in Moseley (B13) and need help with roof leak repairs.") |
| Reviews | Linked to the Google Business Profile and Rated People; reviews shown word for word |
| Questions answered | 217 different questions answered across the site |
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

## Measured results (finished build)

| Measure | Figure |
|---|---|
| Home page HTML (compressed) | 8 KB |
| Stylesheet (compressed) | 5 KB |
| JavaScript | One file, under 2 KB (cookie consent only) |
| Home hero background image | 18 KB |
| Original photos supplied | 3.7 MB for 11 photos |
| Typical photo as served | 78 KB (720px WebP; phones download the smallest size that fits) |
| Pages that scroll sideways on a 360px phone | 0 of 95 |
| Broken links or images | 0 (153 URLs crawled over HTTP) |
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
