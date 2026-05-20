"""Notifica a IndexNow (Bing, Yandex, etc.) las URLs del sitio que cambiaron.

IndexNow es un protocolo abierto: con un POST avisamos a los buscadores que
una o varias URLs se actualizaron, y las recrawlean sin esperar al ciclo
normal. La verificación de propiedad es por un archivo-key en la raíz del
sitio (<key>.txt cuyo contenido es la key).

Uso:
    python3 scripts/indexnow_ping.py                # usa las URLs del sitemap
    python3 scripts/indexnow_ping.py <url> [<url>]  # URLs puntuales

Se corre solo tras un deploy (ver `task site:deploy`).
"""

import json
import os
import re
import sys
import urllib.request

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SITE_DIR = os.path.join(PROJECT_ROOT, 'site', 'spiralout')

HOST = 'spiralout.space'
KEY = '5502d857e903da2aa87a071701f01007'
KEY_LOCATION = f'https://{HOST}/{KEY}.txt'
ENDPOINT = 'https://api.indexnow.org/indexnow'


def urls_from_sitemap():
    """Extrae los <loc> del sitemap.xml local."""
    sitemap = os.path.join(SITE_DIR, 'sitemap.xml')
    if not os.path.exists(sitemap):
        return []
    with open(sitemap, encoding='utf-8') as fh:
        xml = fh.read()
    return re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', xml)


def ping(urls):
    """Manda el batch de URLs a IndexNow. Devuelve el status HTTP."""
    payload = {
        'host': HOST,
        'key': KEY,
        'keyLocation': KEY_LOCATION,
        'urlList': urls,
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode('utf-8', 'replace')


def main():
    urls = sys.argv[1:] or urls_from_sitemap()
    if not urls:
        print('IndexNow: no hay URLs para notificar (sitemap vacío?).')
        return
    print(f'IndexNow: notificando {len(urls)} URL(s) a {ENDPOINT}')
    for u in urls:
        print(f'  - {u}')
    try:
        status, body = ping(urls)
    except Exception as exc:  # noqa: BLE001 — el ping no debe romper el deploy
        print(f'IndexNow: fallo al notificar ({exc}). No bloqueante.')
        return
    # 200 y 202 son OK; 422 = URL no coincide con host/key.
    if status in (200, 202):
        print(f'IndexNow: OK (HTTP {status}).')
    else:
        print(f'IndexNow: respuesta HTTP {status}: {body[:200]}')


if __name__ == '__main__':
    main()
