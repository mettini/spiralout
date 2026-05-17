"""Sirve el player + WAVs desde el root del proyecto.

Uso:
    python3 player/serve.py [--port 8000] [--no-open]

Levanta un HTTP server en el ROOT del proyecto (no en player/) para que la UI
pueda fetch /out/index.json, /out/outbound/stems/.../*.wav, etc. Despues abre
el navegador en http://localhost:PORT/player/.
"""

import argparse
import http.server
import os
import socket
import socketserver
import sys
import webbrowser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        '.wav': 'audio/wav',
        '.json': 'application/json',
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.html': 'text/html',
    }

    def end_headers(self):
        # evitar cache durante desarrollo
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write(f'{self.address_string()} {fmt % args}\n')


def find_free_port(start=8000, end=8050):
    for p in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', p))
                return p
            except OSError:
                continue
    raise RuntimeError(f'sin puerto libre en {start}-{end}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=None,
                    help='puerto (auto-detecta si no se especifica)')
    ap.add_argument('--no-open', action='store_true',
                    help='no abrir el navegador automaticamente')
    ap.add_argument('--pid-file', type=str, default=None,
                    help='escribir PID a este archivo (para que el Taskfile lo mate)')
    ap.add_argument('--port-file', type=str, default=None,
                    help='escribir puerto efectivo a este archivo')
    args = ap.parse_args()

    port = args.port or find_free_port()
    os.chdir(ROOT)
    url = f'http://localhost:{port}/player/'

    print(f'serving {ROOT}')
    print(f'open    {url}')
    print('ctrl+c to stop')

    if args.pid_file:
        with open(args.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    if args.port_file:
        with open(args.port_file, 'w') as f:
            f.write(str(port))

    with socketserver.ThreadingTCPServer(('127.0.0.1', port), Handler) as httpd:
        if not args.no_open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nbye')
        finally:
            for path in (args.pid_file, args.port_file):
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass


if __name__ == '__main__':
    main()
