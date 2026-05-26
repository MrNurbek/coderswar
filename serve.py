"""Local dev server — serves frontend/ with Nginx-style path rewrite."""
import http.server
import socketserver
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
FRONTEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND, **kwargs)

    def translate_path(self, path):
        # /static/frontend/x  →  /static/x  (mirrors Nginx alias)
        if path.startswith('/static/frontend/'):
            path = '/static/' + path[len('/static/frontend/'):]
        return super().translate_path(path)

    def log_message(self, fmt, *args):
        pass

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('', PORT), Handler) as httpd:
    httpd.serve_forever()
