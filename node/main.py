import requests, time, random, socket, os

addr = os.getenv("AMM_SERVER_ADDR")
port = int(os.getenv("AMM_SERVER_PORT"))

ammUrl = "http://"+addr+":"+str(port)
# ammUrl = "http://localhost:5678"

time.sleep(2+random.random()*2)
print("consumer started...")

amount = 0
count = 0
rateHistory = []
currencies = requests.get(ammUrl+'/get-currencies').json()

def getlocalIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

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

localIp = getlocalIp()

while True:
    count += 0

    root = random.random() * 10
   
    try:
        rateHistory.append(requests.get(ammUrl+'/get-rates').json())
    except:
        pass

    if count % 5 == 0:

        profitability = []
        for currency in currencies:
            for referenceCurrency in currencies:
                if currency != referenceCurrency:
                    profitability.append({"key":analysis(currency, referenceCurrency), "from":currency, "to":referenceCurrency})

        profitability = sorted(profitability, key=lambda d: d['key']) 
    # print(profitability)

    # amount = np.random.normal(10*root,root)
    amount = random.randrange(0,10)
    request = {"client":localIp, "from": profitability[len(profitability)-1]["from"], "to": profitability[len(profitability)-1]["to"], "amount": amount}
    # print(request)
    try:
        r = requests.post(ammUrl+'/transaction', json=request)
    except:
        time.sleep(30)
    # print(r.json())
    # time.sleep(random.random())
    time.sleep(0.7)