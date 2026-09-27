#!/usr/bin/env python3
"""Build the site and preview it locally.

    python3 serve.py              # builds, then serves on the first free port from 8000
    python3 serve.py --port 8123  # try a specific port first
    python3 serve.py --no-build   # serve the existing site/ folder without rebuilding
    python3 serve.py --no-open    # don't open a browser tab
    python3 serve.py --live       # build in live mode (only at launch)

Builds in DEMO mode by default: site/ is hidden from search engines, so it's safe to
drag onto Netlify Drop for a preview. Use --live (or plain `python3 build.py`) at launch.

It prints the exact address and opens it in your browser. Use THAT address:
other programs on this Mac (e.g. Hermes on 8080) may be using common ports,
and visiting their port gives "ERR_EMPTY_RESPONSE".
"""
import argparse
import functools
import os
import http.server
import socket
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT / "site"


def free_port(start):
    for port in range(start, start + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    sys.exit("No free port found between %d and %d." % (start, start + 49))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--no-open", action="store_true", help="don't open a browser tab")
    ap.add_argument("--live", action="store_true", help="build in live mode (indexable). Default is demo mode.")
    args = ap.parse_args()

    if not args.no_build:
        env = dict(os.environ)
        if not args.live:
            env["DEMO"] = "1"   # keeps site/ safe to drag onto Netlify Drop before launch
        result = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env)
        if result.returncode != 0:
            if (SITE / "index.html").exists():
                print("\nBuild failed (see above). Serving the last built version instead.")
                print("Most common fix: python3 -m pip install -r requirements.txt\n")
            else:
                sys.exit("Build failed and there is no site/ folder to serve. Run: python3 -m pip install -r requirements.txt")

    port = free_port(args.port)
    url = "http://127.0.0.1:%d/" % port
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    print("\n  RJR site running at:  %s\n  (Ctrl+C to stop)\n" % url, flush=True)
    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
