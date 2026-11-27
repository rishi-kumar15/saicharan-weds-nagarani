#!/usr/bin/env python3
"""
Local server for the Wedding Website (Sai Charan Gudivada & Nagarani Kunta invitation).

Serves the `www.dreamsinvite.com` folder as the web root so that all
absolute asset paths (/_next/..., /templates/..., /music/...) resolve
correctly, then opens the invitation in your default browser.

Usage:
    python run.py                 # http://localhost:8000
    python run.py 8080            # custom port
    python run.py 8080 --no-browser
"""

import http.server
import mimetypes
import os
import re
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE / "www.dreamsinvite.com"
START_PAGE = "/dev-weds-ananya098f.html?test="

# Clean URLs used by the Next.js app -> mirrored HTML file
CLEAN_URLS = {
    "/": "index.html",
    "/dev-weds-ananya": "dev-weds-ananya.html",
    "/ethan-weds-lily": "ethan-weds-lily.html",
    "/templates": "templates7f3d.html",
    "/services": "services.html",
    "/contact": "contact.html",
    "/privacy": "privacy.html",
    "/refund": "refund.html",
}

mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("audio/mpeg", ".mp3")
mimetypes.add_type("text/x-component", ".rsc")


class SiteHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path):
        parts = urlsplit(path)
        path = unquote(parts.path)
        if path in CLEAN_URLS:
            path = "/" + CLEAN_URLS[path]
        elif not os.path.splitext(path)[1]:
            slug = path.strip("/")
            rsc = slug + ".rsc"
            if "_rsc" in parts.query and (ROOT / rsc).is_file():
                path = "/" + rsc
            else:
                candidate = slug + ".html"
                if (ROOT / candidate).is_file():
                    path = "/" + candidate
        return super().translate_path(path)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_head(self):
        """Add HTTP Range support so videos/audio can stream and seek."""
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()
        header = self.headers.get("Range")
        if not header:
            return super().send_head()
        match = re.match(r"bytes=(\d*)-(\d*)", header)
        if not match:
            return super().send_head()

        file_size = os.path.getsize(path)
        start, end = match.group(1), match.group(2)
        if start:
            start = int(start)
            end = int(end) if end else file_size - 1
        else:
            end = int(end)
            start = max(file_size - end, 0)
            end = file_size - 1
        end = min(end, file_size - 1)
        if start > end or start >= file_size:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{file_size}")
            self.end_headers()
            return None

        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        self.send_response(206)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        f = open(path, "rb")
        f.seek(start)
        return _BoundedFile(f, end - start + 1)

    def log_message(self, fmt, *args):
        # Keep console output tidy; comment out to see every request.
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(fmt, *args)


class _BoundedFile:
    """File wrapper that yields at most `remaining` bytes (for Range responses)."""

    def __init__(self, fileobj, remaining):
        self.fileobj = fileobj
        self.remaining = remaining

    def read(self, size=-1):
        if self.remaining <= 0:
            return b""
        if size < 0 or size > self.remaining:
            size = self.remaining
        data = self.fileobj.read(size)
        self.remaining -= len(data)
        return data

    def close(self):
        self.fileobj.close()


class ReusableTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8000
    open_browser = "--no-browser" not in sys.argv

    if not (ROOT / "dev-weds-ananya098f.html").is_file():
        print(f"ERROR: site files not found in {ROOT}")
        sys.exit(1)

    url = f"http://localhost:{port}{START_PAGE}"
    with ReusableTCPServer(("127.0.0.1", port), SiteHandler) as httpd:
        print("=" * 60)
        print("  Wedding Website is ready!")
        print(f"  Open: {url}")
        print("  Press Ctrl+C to stop the server.")
        print("=" * 60)
        if open_browser:
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
