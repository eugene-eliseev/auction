import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

from api_worker import Api
from functions import generate_session, template, generate_nav, get_items, get_name_from_id
from models import Player
from http.cookies import SimpleCookie
from urllib.parse import parse_qs


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def redirect(self, path, cookie=None):
        self.send_response(302)
        if cookie is not None:
            self.send_header("Set-Cookie", cookie.output(header=''))
        self.send_header("Location", path)
        self.end_headers()

    def do_GET(self):
        cookies = SimpleCookie(self.headers.get("Cookie"))
        session_id = None
        if "session_id" in cookies:
            session_id = cookies["session_id"].value
        player = Player.from_session(session_id)
        self.path = self.path.split('?')[0][1:]
        if self.path == "":
            self.path = "index"
        print("Request", self.path)
        if player is None and self.path != "login":
            self.redirect("/login")
            return
        if player is not None and self.path == "login":
            self.redirect("/")
            return

        if self.path == "exit":
            print("Logout")
            player.session_id = ""
            player.save()
            self.redirect("/login")
            return

        if self.path == "login":
            self.path = "login.html"
        file = os.path.join("static", self.path)
        if os.path.exists(file):
            self.send_file(file)
            return

        vars = {}

        if self.path == "add_lot":
            item_str = open(os.path.join("static", "add_lot_item.html"), "r", encoding="utf8").read()
            vars["items"] = ""
            items = get_items(player.player)
            for item in items:
                vars["items"] += template(item_str, {
                    "server_name": item.server,
                    "user_name": item.player,
                    "item_count": item.amount,
                    "item_id": item.item,
                    "id": item.id,
                    "item_name": get_name_from_id(item.server, item.item)
                })
        file_html = os.path.join("static", "{}.html".format(self.path))
        if os.path.exists(file_html):
            self.send_html(file_html, player, vars)
            return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'404 not found')
        print(self.path, "404")

    def send_html(self, file, player, vars):
        content = open(file, "r", encoding="utf8").read()
        content = template(content, vars)

        nav = generate_nav(player)

        main = open(os.path.join("static", "main.html"), "r", encoding="utf8").read()
        page = template(main, {"content": content, "navigation": nav})

        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(page, encoding="utf8"))

    def send_file(self, file):
        file = open(file, "rb").read()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(file)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        params = parse_qs(body.decode())
        if "login" in params and "pass" in params:
            username = Api.check_user(params["login"][0], params["pass"][0])
            if username is None:
                print("Incorrect login", params["login"][0])
                # TODO
                return
            balance = Api.get_balance(username)
            session_id = generate_session(username)
            player = Player(username, session_id, balance)
            player.save()
            cookie = SimpleCookie()
            cookie["session_id"] = session_id
            cookie["session_id"]["expires"] = 90 * 86400
            print("Session created")
            self.redirect("/", cookie)
            return

        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())


httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
print("Server started")
httpd.serve_forever()
