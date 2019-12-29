import sqlite3
import time

SQLITE_PATH = "db.sqlite3"


class DataStorage:
    def __init__(self):
        self.sqlite = sqlite3.connect(SQLITE_PATH)
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
        conn.commit()

    def get_connection(self):
        return self.sqlite.cursor(), self.sqlite


STORAGE = DataStorage()


class Player:
    def __init__(self, name, session_id='', balance=0):
        self.player = name
        self.session_id = session_id
        self.balance = balance

    def save(self):
        cursor, conn = STORAGE.get_connection()
        if Player.from_name(self.player) is None:
            if self.balance is None:
                self.balance = 0
            cursor.execute("INSERT INTO players (player, session, balance) VALUES ('{}', '{}', '{}')".format(
                self.player,
                self.session_id,
                self.balance
            ))
        else:
            if self.balance is not None:
                cursor.execute("UPDATE players SET balance = '{}' WHERE player = '{}'".format(self.balance, self.player))
            cursor.execute("UPDATE players SET session = '{}' WHERE player = '{}'".format(self.session_id, self.player))
        conn.commit()

    @staticmethod
    def from_name(name):
        if name is None:
            return None
        cursor, conn = STORAGE.get_connection()
        cursor.execute("SELECT player, session, balance FROM players WHERE player = '{}'".format(name))
        res = cursor.fetchall()
        for d in res:
            return Player(d[0], d[1], d[2])
        return None

    @staticmethod
    def from_session(session_id):
        if session_id is None:
            return None
        cursor, conn = STORAGE.get_connection()
        cursor.execute("SELECT player, session, balance FROM players WHERE session != '' AND session = '{}'".format(session_id))
        res = cursor.fetchall()
        for d in res:
            return Player(d[0], d[1], d[2])
        return None


class Lot:
    def __init__(self, id, player, item_id, price_start, buyer, price_now, price_end, last_changed=time.time()):
        self.id = id
        self.player = player
        self.item_id = item_id
        self.price_start = price_start
        self.price_now = price_now
        self.price_end = price_end
        self.last_changed = last_changed
        self.buyer = buyer

    @staticmethod
    def from_id(lot_id):
        cursor, conn = STORAGE.get_connection()
        cursor.execute(
            "SELECT id, player, item_id, price_start, buyer, price_now, price_end, last_changed FROM lots WHERE id = '{}'".format(
                lot_id
            )
        )
        res = cursor.fetchall()
        for d in res:
            return Lot(d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7])
        return None


class Item:
    def __init__(self, id, item, player, amount, extra, server):
        self.id = id
        self.player = player
        self.amount = amount
        self.item = item
        self.extra = extra
        self.server = server

    @staticmethod
    def from_lot(lot):
        cursor, conn = STORAGE.get_connection()
        cursor.execute("SELECT id, player, amount, item, extra, server FROM items WHERE id = '{}'".format(lot.item_id))
        res = cursor.fetchall()
        for d in res:
            return Item(d[0], d[1], d[2], d[3], d[4], d[5])
        return None

    @staticmethod
    def find_items_of_player(player):
        items = []
        cursor, conn = STORAGE.get_connection()
        cursor.execute("SELECT id, player, amount, item, extra, server FROM items WHERE player = '{}'".format(player))
        res = cursor.fetchall()
        for d in res:
            items.append(Item(d[0], d[1], d[2], d[3], d[4], d[5]))
        return items
