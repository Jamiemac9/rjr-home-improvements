#!/usr/bin/env python3
"""Check the built site before committing or deploying.

    python3 build.py && python3 tools/check_site.py

Serves site/ on a free local port, follows every internal link from the home page,
and reports:
  - any URL that doesn't return 200 (pages, CSS, JS, images, srcset sizes)
  - pages without exactly one quote form (id="quote")
  - pages whose canonical isn't on the live domain or doesn't match the page path
  - pages with more or fewer than one <h1>
  - duplicate <title>s
  - whether the build is in DEMO (noindex) or LIVE mode
Exits 1 if anything fails, so it can gate a commit or CI step.
"""
import functools
import http.server
import re
import socket
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT))
from content import SITE as CONFIG  # noqa: E402

DOMAIN = CONFIG["url"].rstrip("/")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    if not (SITE / "index.html").exists():
        sys.exit("No site/ folder. Run: python3 build.py")
    port = free_port()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Quiet, directory=str(SITE)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    start = "http://127.0.0.1:%d/" % port

    seen, queue, problems, titles = set(), [start], [], Counter()
    pages = 0
    while queue:
        url = queue.pop()
        if url in seen:
            continue
        seen.add(url)
        try:
            resp = urllib.request.urlopen(url)
            body, ctype = resp.read(), resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as err:
            problems.append("%d  %s" % (err.code, url.replace(start, "/")))
            continue
        if "text/html" not in ctype:
            continue
        pages += 1
        html = body.decode("utf-8")
        path = urllib.parse.urlparse(url).path
        if html.count('id="quote"') != 1:
            problems.append("forms=%d  %s" % (html.count('id="quote"'), path))
        if html.count("<h1") != 1:
            problems.append("h1=%d  %s" % (html.count("<h1"), path))
        can = re.search(r'rel="canonical" href="([^"]+)"', html)
        if not can or not can.group(1).startswith(DOMAIN + "/") or urllib.parse.urlparse(can.group(1)).path != path:
            problems.append("canonical  %s -> %s" % (path, can.group(1) if can else "missing"))
        title = re.search(r"<title>(.*?)</title>", html)
        titles[title.group(1) if title else ""] += 1
        refs = re.findall(r'(?:href|src)="([^"#]+)', html)
        refs += [part.split()[0] for s in re.findall(r'srcset="([^"]+)"', html) for part in s.split(", ")]
        for ref in refs:
            if ref.startswith(("http:", "https:", "mailto:", "tel:", "data:")):
                continue
            nxt = urllib.parse.urljoin(url, ref).split("?")[0]
            if nxt.startswith(start) and nxt not in seen:
                queue.append(nxt)
    server.shutdown()

    for t, n in titles.items():
        if n > 1:
            problems.append("duplicate title x%d  %s" % (n, t))
    robots = (SITE / "robots.txt").read_text()
    mode = "DEMO (noindex, robots blocks crawlers)" if "Disallow: /" in robots else "LIVE (indexable)"
    print("Mode: %s" % mode)
    print("Pages reached: %d   URLs checked: %d" % (pages, len(seen)))
    if problems:
        print("\nPROBLEMS (%d):" % len(problems))
        for p in problems[:50]:
            print("  " + p)
        sys.exit(1)
    print("OK: no broken links or images, one form and one h1 per page, canonicals correct, titles unique.")


if __name__ == "__main__":
    main()
