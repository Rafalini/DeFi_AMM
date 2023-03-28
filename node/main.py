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

while True:
    root = random.random() * 10

    if int(root) % 2 == 0:
        currencyFrom, currencyTo = swap(currencyFrom, currencyTo)

    for i in range(int(root) + 1): 
        amount = np.random.normal(3*root,root)
        r = requests.post('http://192.168.10.1:8000/transaction', json={"from": currencyFrom, "to": currencyTo, "amount": amount})
        time.sleep(1+random.random()*2)