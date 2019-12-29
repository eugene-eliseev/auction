import random
import time

import os

from api_worker import Api
from models import Lot, Item, Player
import hashlib
import re


def order_lot(player, lot_id, price):
    lot = Lot.from_id(lot_id)
    if player.player == lot.buyer:
        return False, "Вы уже сделали ставку!"
    if player.balance < price:
        return False, "Недостаточно денег!"
    if lot.price_now > price:
        return False, "Нужно перебить текущую стоимость!"
    if lot.price_end >= price:
        item = Item.from_lot(lot)
        player.balance -= price
        if lot.buyer is not None:
            old_buyer = Player.from_name(lot.buyer)
            old_buyer.balance += lot.price_now
            old_buyer.save()
        item.player = player
        if Api.create_item_server(item):
            item.remove()
            lot.remove()
            player.save()
        else:
            item.save()
        return True, ""
    if lot.buyer is not None:
        old_buyer = Player.from_name(lot.buyer)
        old_buyer.balance += lot.price_now
        old_buyer.save()
    player.balance -= price
    player.save()
    lot.buyer = player
    lot.price_now = price
    lot.save()


def create_lot_from_external_item(external_id, amount, price_start, price_end):
    item = Api.get_item_server(external_id)
    if item is None:
        return False, "Предмет не найден или нет соединения с сервером!"
    if item.amount < amount:
        return False, "Нельзя выставить такое количество!"
    if item.amount != amount:
        success = Api.decrease_item_server(external_id, amount)
    else:
        success = Api.remove_item_server(external_id)
    if not success:
        return False, "Предмет не найден или нет соединения с сервером!"
    item.amount = amount
    item.save()
    lot = item.create_lot(price_start, price_end)
    lot.save()
    return lot, ""


def create_lot_from_internal_item(id, amount, price_start, price_end):
    item = Item.from_id(id)
    if item is None:
        return False, "Предмет не найден"
    if item.amount < amount:
        return False, "Нельзя выставить такое количество!"
    if item.amount != amount:
        item.amount -= amount
        item.save()
        item.id = None
    item.amount = amount
    item.save()
    lot = item.create_lot(price_start, price_end)
    lot.save()
    return lot, ""


def get_items(player):
    items = Item.find_items_of_player(player)
    items_external = Api.find_items_of_player(player)
    if items_external is not None:
        items.extend(items_external)
    return items


def create_lot(id, amount, price_start, price_end):
    if id.startswith('#'):
        return create_lot_from_external_item(id, amount, price_start, price_end)
    return create_lot_from_internal_item(id, amount, price_start, price_end)


def generate_session(username):
    m = hashlib.md5("T{}U{}R{}E".format(int(time.time()), username, random.randint(1, 100000)).encode('utf-8'))
    return m.hexdigest()


def template(data, vars):
    for key, value in vars.items():
        data = re.sub('{' + key + '}', str(value), data, flags=re.IGNORECASE)
    return data


def generate_nav(player):
    nav = open(os.path.join("static", "nav_bar.html"), "r", encoding="utf8").read()
    if player is None:
        player_name = "Гость"
        auth_block = open(os.path.join("static", "guest_user.html"), "r", encoding="utf8").read()
    else:
        player_name = player.player
        auth_block = open(os.path.join("static", "auth_user.html"), "r", encoding="utf8").read()
    return template(nav, {"user": player_name, "auth_block": auth_block})


def get_name_from_id(server, item_id):
    return "Неизвестный предмет"
