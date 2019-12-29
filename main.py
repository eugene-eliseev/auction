import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from models import Player


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        player = Player.from_session(None)
        if player is None:
            self.send_html("login.html")
            return
        self.path = self.path.split('?')[0]
        if self.path == "/":
            self.path = "/static/index.html"
        if self.path.startswith("/static/"):
            if os.path.exists(self.path[1:]):
                self.send_html(self.path[1:])
                return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'404 not found')

    def send_html(self, file):
        data = open(file, "rb").read()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())


httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()
