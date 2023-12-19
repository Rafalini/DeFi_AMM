import requests
import time
import json
import os
import threading
from flask import Response
from datetime import datetime
from web_app import app
# from bs4 import BeautifulSoup
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

checkpoint_path = "./weights"

print("Initialization of prediction model...")

# model = Sequential()
# model.add(LSTM(50, return_sequences = True, input_shape=(50, 1)))
# model.add(LSTM(64, return_sequences = False))
# model.add(Dense(1, activation='linear'))
# model.compile(loss='mse', optimizer='rmsprop')
# model.load_weights(checkpoint_path)

print("Initialization done.")

addr = os.getenv("AMM_SERVER_ADDR")
port = int(os.getenv("AMM_SERVER_PORT"))

ammUrl = "http://"+addr+":"+str(port)

def getCurrencies():
  url1 = ammUrl+"/get-currencies"
  ids = ""
  try:
    response1 = requests.get(url1)
    for entry in response1["currencies"]:
       ids += entry["id"]+","

  except Exception:
    pass
  
  return ids

currencyIds = getCurrencies()
print(currencyIds)

def getPricesAndAmounts():
    API_KEY = os.getenv("APIKEY")
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    # url2 = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'


    parameters = {
        'id': '1027,1518,5176',
        # 'limit': 5000
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }

    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()
    usdPrices = []
    
    # usdPrices.append({"symbol" : data["data"]["1"]["symbol"], "usdprice" : data["data"]["1"]["quote"]["USD"]["price"] })
    usdPrices.append({"symbol" : data["data"]["1027"]["symbol"], "usdprice" :  data["data"]["1027"]["quote"]["USD"]["price"] })
    usdPrices.append({"symbol" : data["data"]["1518"]["symbol"], "usdprice" :  data["data"]["1518"]["quote"]["USD"]["price"] })
    usdPrices.append({"symbol" : data["data"]["5176"]["symbol"], "usdprice" :  data["data"]["5176"]["quote"]["USD"]["price"] })

    return usdPrices
pricesTable = getPricesAndAmounts()

def updateRates():
  while(True):
      # pairs = getUniswapTokens(uniswapApiURL, uniswapQueryBody)
      # addUniswapHistoryEntry(pairs)

      # pairs = getBalancerTokens(balanceApiURL, balancerQueryBody)
      # addBalancerHistoryEntry(pairs)
      global pricesTable
      pricesTable = getPricesAndAmounts()
      time.sleep(60)
      # print(history[pairs[0]["id"]][i]["token0value"])
      # print(balancerHistory[pairs[0]["symbol"]][i]["price"])

download_thread = threading.Thread(target=updateRates, name="updater")
download_thread.start()

@app.route("/get-values")
def getCurrencies():
    return Response(json.dumps(pricesTable), status=200, mimetype='application/json')

# @app.route("/")
@app.route("/get-prices")
def getSymbols():
  return Response(json.dumps(pricesTable), status=200, mimetype='application/json')

# @app.route("/get-predictions")
# def getPredictions():
#     predictions = [{"currency":"BTC", "volumen": 1300, "futurePrice":123, "change":5, "volumenChange":8},
#                    {"currency":"ETH", "volumen": 1300, "futurePrice":321, "change":-5,"volumenChange":8}]
#     return Response(json.dumps(predictions), status=200, mimetype='application/json')