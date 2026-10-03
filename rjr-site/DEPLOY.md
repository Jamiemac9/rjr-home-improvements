# Deploying the RJR site

## 1. Open it in Cursor

1. Unzip `rjr-site.zip`.
2. In Cursor: **File → Open Folder** → choose the `rjr-site` folder.
3. Open the terminal (**View → Terminal**) and run:
   ```bash
   python3 -m pip install -r requirements.txt
   python3 serve.py
   ```
4. It prints `RJR site running at: http://127.0.0.1:XXXX/` and opens that page. Use that exact address. Press Ctrl+C in the terminal to stop.
   - Don't use `localhost:8080`: Hermes runs there, and you'll get `ERR_EMPTY_RESPONSE`.

## 2. Fastest demo (no GitHub, about 2 minutes)

`python3 serve.py` builds the `site/` folder in demo mode (hidden from Google), so it's safe to upload.

1. Go to https://app.netlify.com/drop and log in (free account).
2. Drag the **`site`** folder (not `rjr-site`) onto the page.
3. You get a link like `https://random-name-123.netlify.app`. Send that to the client.
4. To get a tidier link: **Site configuration → Change site name** → e.g. `rjr-demo` → `https://rjr-demo.netlify.app`.

To update it, run `python3 serve.py` (demo mode by default), then drag the `site` folder onto **Deploys** in that site.

## 3. Proper setup (auto-deploys every time you push from Cursor)

### Put the project on GitHub
1. In Cursor, open **Source Control** (the branch icon on the left).
2. **Initialize Repository** → type a message like "RJR site" → **Commit**.
3. **Publish Branch** → choose **private** repository → sign in to GitHub if asked.

### Option A: Netlify
1. https://app.netlify.com → **Add new site → Import an existing project → GitHub** → pick the repo.
2. Netlify reads `netlify.toml`, so the build command (`python3 build.py`), publish folder (`site`), Python version and `DEMO=1` are already set. Leave the fields as they are.
3. **Deploy**. The link will be `https://<name>.netlify.app`. Rename it under **Site configuration → Change site name**.

### Option B: Cloudflare Pages
1. https://dash.cloudflare.com → **Workers & Pages → Create → Pages → Connect to Git** → pick the repo.
2. Build settings:
   - Framework preset: **None**
   - Build command: `pip install -r requirements.txt && python3 build.py`
   - Build output directory: `site`
3. **Environment variables**: add `PYTHON_VERSION` = `3.11` and `DEMO` = `1`.
4. **Save and Deploy**. The link will be `https://<name>.pages.dev`.

After this, every commit you push from Cursor redeploys the demo automatically.

## 4. Going live once rjrhomeimprovements.com is bought

If you deploy by drag-and-drop instead of GitHub: build with `python3 serve.py --live` (or `python3 build.py`), then upload `site`.


1. **Switch off demo mode**
   - Netlify: delete the `DEMO = "1"` line in `netlify.toml`, commit and push.
   - Cloudflare: delete the `DEMO` variable under **Settings → Environment variables**, then **Retry deployment**.
2. **Connect the domain**
   - Netlify: **Domain management → Add a domain** → `rjrhomeimprovements.com` → follow the DNS steps. HTTPS is automatic.
   - Cloudflare: **Custom domains → Set up a domain** → `rjrhomeimprovements.com`. Simplest if the domain is bought through Cloudflare or its DNS is moved there.
   - Add `www.rjrhomeimprovements.com` too. Netlify redirects www to the main domain via `netlify.toml`; on Cloudflare add a redirect rule for www.
3. **Check it's live and indexable**: open `https://rjrhomeimprovements.com/robots.txt`. It should say `Allow: /`, not `Disallow: /`.
4. **Tell Google**
   - Add the domain in Google Search Console and submit `https://rjrhomeimprovements.com/sitemap.xml`.
   - Add the website link to the Google Business Profile and the Rated People profile.
5. **Before launch:** get the client to confirm the registered office (246 Court Oak Road, Birmingham B32 2EG, already in `content.py`) and approve the privacy policy.

## If something looks wrong

- **"Error response 404" locally**: the preview server is pointing at an old or wrong folder. Stop it and run `python3 serve.py`.
- **"ERR_EMPTY_RESPONSE" locally**: you're on a port another app owns (8080 is Hermes on this Mac). Use the address `serve.py` prints.
- **Build fails on the host with "No module named PIL"**: the build command must include `pip install -r requirements.txt`.
- **Changes not showing**: builds take a minute or two. Check the deploy log on Netlify or Cloudflare, then hard-refresh the browser.
