import requests

initialBtc = 0
initialEth = 200

chunk = 1
transCnt = 0

actBtc = initialBtc
actEth = initialEth

print("initial state:  BTC: "+str(initialBtc)+"  ETH: "+str(initialEth))


ammUrl = "http://localhost:5001"

# request = {"client":ammUrl, "from": "BTC", "to": "ETH", "amount": initialBtc}
# r = requests.post(ammUrl+'/transaction', json=request)

# if r.status_code == 200:

    # actEth = r.json()["recieved"]
    # actBtc -= initialBtc

while(actEth>0):
    transCnt += 1

    amount = chunk if actEth > chunk else actEth

    request = {"client":ammUrl, "from": "ETH", "to": "BTC", "amount": chunk}
    r = requests.post(ammUrl+'/transaction', json=request)

    if(r.status_code == 200):
        actEth -= amount
        actBtc += r.json()["recieved"]
    
request = {"client":ammUrl, "from": "BTC", "to": "ETH", "amount": actBtc}
actBtc = 0
r = requests.post(ammUrl+'/transaction', json=request)
actEth += r.json()["recieved"]

print("final state:  BTC: "+str(actBtc)+"  ETH: "+str(actEth))
print("Transaction count: "+str(transCnt))
