import requests

API_KEY = "723DFsd216G"
URL = "https://greatray.ru/"


class Api:
    @staticmethod
    def check_user(user, password):
        res = requests.get("{}authipb?login={}&password={}".format(URL, user, password))
        if res.text.startswith("OK:"):
            return res.text[3:]
        return None

    @staticmethod
    def get_item_server(item_id):
        return None

    @staticmethod
    def remove_item_server(item_id):
        return False

    @staticmethod
    def decrease_item_server(item_id, amount):
        return False

    @staticmethod
    def create_item_server(item):
        return False

    @staticmethod
    def find_items_of_player(player):
        return None