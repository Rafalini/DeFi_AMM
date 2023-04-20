import requests
import time
import random
import numpy as np

time.sleep(2+random.random()*2)
print("consumer started...")

currencyFrom = "BTC"
currencyTo = "ETH"
amount = 0


def swap(x,y):
    return y,x


def analysis():
    return 0


rateHistory = []

while True:
    root = random.random() * 10

    # if int(root) % 2 == 0:
    #     currencyFrom, currencyTo = swap(currencyFrom, currencyTo)
    rateHistory.append(requests.get('http://192.168.10.1:8000/get-rates').json())
    if len(rateHistory) == 10:
        rateHistory.pop(0)

    for i in range(int(root) + 1): 
        amount = np.random.normal(3*root,root)
        rates = requests.get('http://192.168.10.1:8000/get-rates').json()



        r = requests.post('http://192.168.10.1:8000/transaction', json={"from": currencyFrom, "to": currencyTo, "amount": amount})
        # print(r.json)
        time.sleep(1+random.random()*2)