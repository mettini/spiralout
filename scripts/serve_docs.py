#!/usr/bin/env python3
"""Server local para ver dashboard + docs con UTF-8 correcto.

El `python -m http.server` no manda `charset=utf-8` en los .md, así que el
browser rompe Æ, ·, — etc. Este handler fuerza UTF-8 en texto/markdown/json.

Uso:  python3 scripts/serve_docs.py [puerto]   (default 8770, sirve la raíz del repo)
"""
import http.server
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class UTF8Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".md": "text/plain; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".html": "text/html; charset=utf-8",
        ".svg": "image/svg+xml; charset=utf-8",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)


if __name__ == "__main__":
    with http.server.ThreadingHTTPServer(("", PORT), UTF8Handler) as httpd:
        print(f"Sirviendo {ROOT} en http://localhost:{PORT}/ (UTF-8)")
        httpd.serve_forever()
