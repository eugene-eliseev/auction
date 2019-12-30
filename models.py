import sqlite3
import time

SQLITE_PATH = "db.sqlite3"


class DataStorage:
    def __init__(self):
        self.sqlite = sqlite3.connect(SQLITE_PATH)
        self.items = {}
        cursor, conn = self.get_connection()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS players (player VARCHAR(20) PRIMARY KEY, session VARCHAR(32), balance DECIMAL(9,2))"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, item VARCHAR(255), player VARCHAR(20), amount INTEGER, extra TEXT, server VARCHAR(255))"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS lots (id INTEGER PRIMARY KEY, player VARCHAR(20), item_id INTEGER, price_start DECIMAL(9,2), buyer VARCHAR(20), price_now DECIMAL(9,2), price_end DECIMAL(9,2), last_changed DECIMAL(11,3))"
        )
        with open("items.txt", "r", encoding="utf8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                data = line.split("<:>")
                item = ':'.join(data[:2])
                icon = data[2]
                name = data[3]
                self.items[item] = (name, icon)
                if data[1] == '0':
                    self.items[data[0]] = (name, icon)
        conn.commit()

    def get_connection(self):
        return self.sqlite.cursor(), self.sqlite


STORAGE = DataStorage()


def get_name_from_id(server, item_id):
    if server == "HiTech" and item_id in STORAGE.items:
        return STORAGE.items[item_id][0]
    return "Неизвестный предмет"


class Player:
    def __init__(self, name, session_id='', balance=0):
        self.player = name
        self.session_id = session_id
        if balance is None:
            balance = 0
        self.balance = float(balance)

    def save(self):
        cursor, conn = STORAGE.get_connection()
        if Player.from_name(self.player) is None:
            if self.balance is None:
                self.balance = 0
            cursor.execute("INSERT INTO players (player, session, balance) VALUES (?, ?, ?)", [
                self.player,
                self.session_id,
                self.balance
            ])
        else:
            if self.balance is not None:
                cursor.execute("UPDATE players SET balance = ? WHERE player = ?", [self.balance, self.player])
            cursor.execute("UPDATE players SET session = ? WHERE player = ?", [self.session_id, self.player])
        conn.commit()

    @staticmethod
    def from_name(name):
        if name is None:
            return None
        cursor, conn = STORAGE.get_connection()
        cursor.execute("SELECT player, session, balance FROM players WHERE player = ?"[name])
        res = cursor.fetchall()
        for d in res:
            return Player(d[0], d[1], d[2])
        return None

    @staticmethod
    def from_session(session_id):
        if session_id is None:
            return None
        cursor, conn = STORAGE.get_connection()
        cursor.execute(
            "SELECT player, session, balance FROM players WHERE session != '' AND session = ?", [session_id])
        res = cursor.fetchall()
        for d in res:
            return Player(d[0], d[1], d[2])
        return None


class Lot:
    def __init__(self, id, player, item_id, price_start, buyer, price_now, price_end, last_changed=time.time()):
        if id is not None:
            id = int(id)
        self.id = id
        self.player = player
        self.item_id = item_id
        self.price_start = float(price_start)
        self.price_now = float(price_now)
        self.price_end = float(price_end)
        self.last_changed = float(last_changed)
        if buyer is None:
            self.buyer = ""
        else:
            self.buyer = buyer

    def remove(self):
        cursor, conn = STORAGE.get_connection()
        cursor.execute("DELETE FROM lots WHERE id = ?", [self.id])
        conn.commit()

    def save(self):
        cursor, conn = STORAGE.get_connection()
        if Lot.from_id(self.id) is None:
            cursor.execute(
                "INSERT INTO lots (player, item_id, price_start, buyer, price_now, price_end, last_changed) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    self.player,
                    self.item_id,
                    self.price_start,
                    self.buyer,
                    self.price_now,
                    self.price_end,
                    time.time()
                ]
            )
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE lots SET player = ?, item_id = ?, price_start = ?, buyer = ?, price_now = ?, price_end = ?, last_changed = ? WHERE id = ?",
                [
                    self.player,
                    self.item_id,
                    self.price_start,
                    self.buyer,
                    self.price_now,
                    self.price_end,
                    time.time(),
                    self.id
                ]
            )
        conn.commit()

    @staticmethod
    def from_id(lot_id):
        if lot_id is None:
            return None
        cursor, conn = STORAGE.get_connection()
        cursor.execute(
            "SELECT id, player, item_id, price_start, buyer, price_now, price_end, last_changed FROM lots WHERE id = ?",
            [lot_id]
        )
        res = cursor.fetchall()
        for d in res:
            return Lot(d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7])
        return None

    @staticmethod
    def find_lots_of_player(player_name):
        lots = []
        cursor, conn = STORAGE.get_connection()
        cursor.execute(
            "SELECT id, player, item_id, price_start, buyer, price_now, price_end, last_changed FROM lots WHERE player = ?",
            [player_name]
        )
        res = cursor.fetchall()
        for d in res:
            lots.append(Lot(d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7]))
        return lots

    @classmethod
    def get_lots(cls):
        lots = []
        cursor, conn = STORAGE.get_connection()
        cursor.execute("SELECT id, player, item_id, price_start, buyer, price_now, price_end, last_changed FROM lots")
        res = cursor.fetchall()
        for d in res:
            lots.append(Lot(d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7]))
        return lots


class Item:
    def __init__(self, id, item, player, amount, extra, server):
        if id is not None:
            id = int(id)
        self.id = id
        self.player = player
        self.amount = int(amount)
        self.item = item
        self.extra = extra
        self.server = server

    def remove(self):
        cursor, conn = STORAGE.get_connection()
        cursor.execute("DELETE FROM items WHERE id = ?", [self.id])
        conn.commit()

    def save(self):
        cursor, conn = STORAGE.get_connection()
        if Item.from_id(self.id) is None:
            cursor.execute(
                "INSERT INTO items (item, player, amount, extra, server) VALUES (?, ?, ?, ?, ?)",
                [
                    self.item,
                    self.player,
                    self.amount,
                    self.extra,
                    self.server
                ]
            )
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE items SET item = ?, player = ?, amount = ?, extra = ?, server = ? WHERE id = ?",
                [
                    self.item,
                    self.player,
                    self.amount,
                    self.extra,
                    self.server,
                    self.id
                ]
            )
        conn.commit()

    def create_lot(self, price_start, price_end):
        return Lot(None, self.player, self.id, price_start, "", price_start, price_end, time.time())

    @staticmethod
    def from_id(id):
        if id is None:
            return None
        cursor, conn = STORAGE.get_connection()
        cursor.execute("SELECT id, item, player, amount, extra, server FROM items WHERE id = ?", [id])
        res = cursor.fetchall()
        for d in res:
            return Item(d[0], d[1], d[2], d[3], d[4], d[5])
        return None

    @staticmethod
    def from_lot(lot):
        return Item.from_id(lot.item_id)

    @staticmethod
    def find_items_of_player(player):
        items = []
        cursor, conn = STORAGE.get_connection()
        cursor.execute("SELECT id, item, player, amount, extra, server FROM items WHERE player = ?", [player])
        res = cursor.fetchall()
        for d in res:
            items.append(Item(d[0], d[1], d[2], d[3], d[4], d[5]))
        return items
