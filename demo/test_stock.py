import requests
import random
from threading import Thread

def stock_func():
    url1 = "http://127.0.0.1:8000/v1/stock"
    url2 = "http://127.0.0.1:8001/v1/stock"
    url = random.choice([url1, url2])
    resp = requests.get(url=url)
    print(resp.text)

t_list = []
for i in range(30):
    t = Thread(target=stock_func)
    t_list.append(t)
    t.start()

for t in t_list:
    t.join()