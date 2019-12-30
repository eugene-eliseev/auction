import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import time

from api_worker import Api
from functions import generate_session, template, generate_nav, get_items, create_lot, order_lot_by_time, order_lot
from lang import LANG
from models import Player, Lot, Item, get_name_from_id
from http.cookies import SimpleCookie
from urllib.parse import parse_qs


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def redirect(self, path, cookie=None):
        self.send_response(302)
        if cookie is not None:
            self.send_header("Set-Cookie", cookie.output(header=''))
        self.send_header("Location", path)
        self.end_headers()

    def get_player(self):
        cookies = SimpleCookie(self.headers.get("Cookie"))
        session_id = None
        if "session_id" in cookies:
            session_id = cookies["session_id"].value
        return Player.from_session(session_id)

    def do_GET(self):
        player = self.get_player()

        message = ""
        if len(self.path.split('?')) > 1:
            data = self.path.split('?')[1].split('=')
            message = {
                "status": LANG[data[0]],
                "info": LANG[data[1]]
            }

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
            print("Logout", player.player)
            player.session_id = ""
            player.save()
            self.redirect("/login")
            return

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
        if self.path == "all_lots":
            item_str = open(os.path.join("static", "all_lots_lot_item.html"), "r", encoding="utf8").read()
            lot_buyer = open(os.path.join("static", "lot_buyer.html"), "r", encoding="utf8").read()
            lot_usual = open(os.path.join("static", "lot_usual.html"), "r", encoding="utf8").read()
            vars["lots"] = ""
            lots = Lot.get_lots()
            for lot in lots:
                if lot.last_changed + 86400 < time.time():
                    order_lot_by_time(lot)
                    continue
                lot_change = ""
                if lot.buyer == player.player:
                    lot_change = template(lot_buyer, {"cost_now": lot.price_end, "buy_now_id": lot.id})
                elif lot.player != player.player:
                    lot_change = template(lot_usual, {"cost_now": lot.price_end, "buy_now_id": lot.id})
                item = Item.from_lot(lot)
                vars["lots"] += template(item_str, {
                    "id": lot.id,
                    "item_name": get_name_from_id(item.server, item.item),
                    "item_count": item.amount,
                    "item_id": item.item,
                    "user_name": lot.player,
                    "server_name": item.server,
                    "cost_start": lot.price_start,
                    "cost_current": lot.price_now,
                    "cost_end": lot.price_end,
                    "time_end": int(lot.last_changed + 86400 - time.time()),
                    "lot_change": lot_change
                })
        file_html = os.path.join("static", "{}.html".format(self.path))
        if os.path.exists(file_html):
            self.send_html(file_html, player, vars, message)
            return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'404 not found')
        print("404", self.path)

    def send_html(self, file, player, vars, message=""):
        if message != "":
            message_str = open(os.path.join("static", "message.html"), "r", encoding="utf8").read()
            message = template(message_str, message)

        content = open(file, "r", encoding="utf8").read()
        content = template(content, vars)

        nav = generate_nav(player, os.path.basename(file).split(".")[0])

        main = open(os.path.join("static", "main.html"), "r", encoding="utf8").read()
        page = template(main, {"message": message, "content": content, "navigation": nav})

        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(page, encoding="utf8"))

    def send_file(self, file):
        file = open(file, "rb").read()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(file)

    def do_POST(self):
        player = self.get_player()
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        params = parse_qs(body.decode())
        if "login" in params and "pass" in params:
            username = Api.check_user(params["login"][0], params["pass"][0])
            if username is None:
                print("Incorrect login", params["login"][0])
                self.redirect("/login?error=login_incorrect")
                return
            balance = Api.get_balance(username)
            session_id = generate_session(username)
            player = Player(username, session_id, balance)
            if player.from_name(username) is None:
                item_1 = Item(None, 4, player.player, 64, '', 'HiTech')
                item_2 = Item(None, 3, player.player, 64, '', 'HiTech')
                item_1.save()
                item_2.save()
                player.balance = 1000
            player.save()
            cookie = SimpleCookie()
            cookie["session_id"] = session_id
            cookie["session_id"]["expires"] = 90 * 86400
            print("Session created for user", username)
            self.redirect("/", cookie)
            return
        if player is None:
            self.redirect("/login")
            return
        res = None
        if "id" in params and "amount" in params and "price_start" in params and "price_end" in params:
            res, info = create_lot(
                params["id"][0],
                params["amount"][0],
                params["price_start"][0],
                params["price_end"][0]
            )
            os.system('echo "{},{},{},{},{},{}" >> log.log'.format(
                int(time.time()),
                player.player,
                params["id"][0],
                params["amount"][0],
                params["price_start"][0],
                params["price_end"][0]
            ))
        if "change_now_id" in params and "cost_current" in params:
            res, info = order_lot(player, params["change_now_id"][0], params["cost_current"][0])
        if "buy_now_id" in params:
            res, info = order_lot(player, params["buy_now_id"][0])
        if res is not None:
            if not res:
                self.redirect("/all_lots?error={}".format(info))
            else:
                self.redirect("/all_lots?success={}".format(info))
            return
        self.redirect("/")


httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
print("Server started")
httpd.serve_forever()
