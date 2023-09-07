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
    # print(rateHistory)
    # for idx, entry in enumerate(rateHistory[:-1]):
        # if entry[currency][referenceCurrency] > rateHistory[idx+1][currency][referenceCurrency]:
        #     tendency += 1
        # else:
        #     tendency -= 1
        # tendency -= rateHistory[idx][currency][referenceCurrency] - rateHistory[idx+1][currency][referenceCurrency]
    return rateHistory[len(rateHistory)-1][currency][referenceCurrency]


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
            if currency != referenceCurrency:
                profitability.append({"key":analysis(currency, referenceCurrency), "from":currency, "to":referenceCurrency})

    profitability = sorted(profitability, key=lambda d: d['key']) 
    # print(profitability)

    # amount = np.random.normal(10*root,root)
    amount = random.randrange(1,1000)

    r = requests.post('http://192.168.10.1:8000/transaction', json={"from": profitability[len(profitability)-1]["from"], "to": profitability[len(profitability)-1]["to"], "amount": amount})
    # print(r.json)
    time.sleep(2+random.random()*10)