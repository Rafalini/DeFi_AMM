import requests
import time
import random
import numpy as np

ammUrl = "http://192.168.10.1:8000"

time.sleep(2+random.random()*2)
print("consumer started...")

amount = 0
rateHistory = []

currencies = requests.get('http://192.168.10.1:8000/get-currencies').json()


def analysis(currency, referenceCurrency):
    tendency = 0
    for idx, entry in enumerate(rateHistory[:-1]):
        # if entry[currency][referenceCurrency] > rateHistory[idx+1][currency][referenceCurrency]:
        #     tendency += 1
        # else:
        #     tendency -= 1
        tendency -= rateHistory[idx][currency][referenceCurrency] - rateHistory[idx+1][currency][referenceCurrency]
    return tendency


while True:
    root = random.random() * 10

    # if int(root) % 2 == 0:
    #     currencyFrom, currencyTo = swap(currencyFrom, currencyTo)
    rateHistory.append(requests.get(ammUrl+'/get-rates').json())
    if len(rateHistory) == 10:
        rateHistory.pop(0)

    profitability = []
    for currency in currencies:
        for referenceCurrency in currencies:
            profitability.append({"key":analysis(currency, referenceCurrency), "from":currency, "to":referenceCurrency})

    profitability = sorted(profitability, key=lambda d: d['key']) 

    amount = np.random.normal(3*root,root)

    r = requests.post('http://192.168.10.1:8000/transaction', json={"from": currencies[0], "to": currencies[1], "amount": amount})
    # print(r.json)
    time.sleep(1+random.random()*2)