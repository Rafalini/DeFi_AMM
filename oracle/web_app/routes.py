import requests
import time
import json
import os
import threading
from flask import Response
from datetime import datetime
from web_app import app
from bs4 import BeautifulSoup
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense, Activation

checkpoint_path = "web_app/model_weights/cp.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)

model = Sequential()
model.add(LSTM(50, return_sequences = True, input_shape=(50, 1)))
model.add(LSTM(64, return_sequences = False))
model.add(Dense(1, activation='linear'))
model.compile(loss='mse', optimizer='rmsprop')
model.load_weights(checkpoint_path)

ammUrl = "http://192.168.10.1:8000"
uniswapApiURL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
sushiswApiURL = "https://api.thegraph.com/subgraphs/name/sushiswap/exchange"
balanceApiURL = "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer"
aaveApiURL = "https://api.thegraph.com/subgraphs/name/aave/protocol-multy-raw"

uniswapQueryBody = """
{
  pairs{
    id
    token0Price
    token0 {
      name
      symbol
    }
    token1 {
      name
      symbol
    }
    token1Price
  }
}
"""
# in $ by default
balancerQueryBody = """
{
  tokenPrices{
    name
    symbol
    price
    poolLiquidity
  }
}
"""


def getEthPrice():
  url1 = 'https://api.coingecko.com/api/v3/simple/price'
  url2 = 'https://api.binance.com/api/v3/ticker/price'
  url3 = 'https://api.binance.com/api/v3/avgPrice'

  params1 = {'ids': 'weth', 'vs_currencies': 'usd'}
  params2 = {'symbol': 'ETHUSDT'}

  response1 = requests.get(url1, params=params1)
  response2 = requests.get(url2, params=params2)
  response3 = requests.get(url3, params=params2)
  weth_price = 0

  if response1.status_code == 200:
      data = response1.json()
      weth_price += float(data['weth']['usd'])

  if response1.status_code == 200:
      data = response2.json()
      weth_price += float(data['price'])

  if response3.status_code == 200:
    data = response3.json()
    weth_price += float(data['price'])
  
  return weth_price / 3


uniswapHistory = {}
balancerHistory = {}
uniformHistory = {}

def getUniswapTokens(url, body):
    response = requests.post(url=url, json={"query": body})
    responseData = []
    if response.status_code == 200:
        data = json.loads(response.content.decode('utf8'))
        if "errors" not in data:
            responseData = data["data"]["pairs"]
    else:
        print(response.reason)
    return responseData

def getBalancerTokens(url, body):
    response = requests.post(url=url, json={"query": body})
    responseData = []
    if response.status_code == 200:
        data = json.loads(response.content.decode('utf8'))
        if "errors" not in data:
            responseData = data["data"]["tokenPrices"]
    else:
        print(response.reason)
    return responseData

def addUniswapHistoryEntry(data):
    ethPrice = getEthPrice()
    for entry in data:
        if entry["id"] not in uniswapHistory:
          uniswapHistory[entry["id"]] = []
        if entry["token0"]["symbol"] not in uniformHistory:
          uniformHistory[entry["token0"]["symbol"]] = []
        valueEntry = {}
        uniformEntry = {}
        valueEntry["dateTime"] = datetime.now().strftime("%H:%M:%S")
        valueEntry["token0name"] = entry["token0"]["symbol"]
        valueEntry["token0value"] = entry["token0Price"]
        valueEntry["token1name"] = entry["token1"]["symbol"]
        valueEntry["token1value"] = entry["token1Price"]
        uniswapHistory[entry["id"]].append(valueEntry)

        if valueEntry["token1name"] == "WETH":
          uniformEntry["dateTime"] = datetime.now().strftime("%H:%M:%S")
          uniformEntry["price"] = float(valueEntry["token0value"]) * ethPrice
          uniformHistory[entry["token0"]["symbol"]].append(uniformEntry)


def addBalancerHistoryEntry(data):
    for entry in data:
        if entry["symbol"] not in balancerHistory:
          balancerHistory[entry["symbol"]] = []

        if entry["symbol"] not in uniformHistory:
          uniformHistory[entry["symbol"]] = []

        valueEntry = {}
        uniformEntry = {}
        valueEntry["dateTime"] = datetime.now().strftime("%H:%M:%S")
        valueEntry["price"] = entry["price"]
        valueEntry["poolLiquidity"] = entry["poolLiquidity"]

        uniformEntry["dateTime"] = datetime.now().strftime("%H:%M:%S")
        uniformEntry["price"] = float(entry["price"])

        balancerHistory[entry["symbol"]].append(valueEntry)
        uniformHistory[entry["symbol"]].append(uniformEntry)

def updateRates():
  while(True):
      pairs = getUniswapTokens(uniswapApiURL, uniswapQueryBody)
      addUniswapHistoryEntry(pairs)

      pairs = getBalancerTokens(balanceApiURL, balancerQueryBody)
      addBalancerHistoryEntry(pairs)

      time.sleep(10)
      # print(history[pairs[0]["id"]][i]["token0value"])
      # print(balancerHistory[pairs[0]["symbol"]][i]["price"])

download_thread = threading.Thread(target=updateRates, name="updater")
download_thread.start()

@app.route("/get-values")
def getCurrencies():
    response = []
    for entry in uniformHistory:
        if len(uniformHistory[entry]) > 0:
          index = len(uniformHistory[entry]) - 1
          response.append({"symbol" : entry, "price" : round(uniformHistory[entry][index]["price"],4), "updated": uniformHistory[entry][index]["dateTime"]})
    resp = sorted(response, key=lambda d: d['price'])
    return Response(json.dumps(resp), status=200, mimetype='application/json')

@app.route("/")
@app.route("/get-symbols")
def getSymbols():
    response = []
    for entry in uniformHistory:
        if len(uniformHistory[entry]) > 0:
          # index = len(uniformHistory[entry]) - 1
          response.append(entry)
    return Response(json.dumps({"length" : len(response), "symbols" : response}), status=200, mimetype='application/json')

@app.route("/get-predictions")
def getPredictions():
    predictions = [{"currency":"BTC", "volumen": 1300, "futurePrice":123, "change":5, "volumenChange":8},
                   {"currency":"ETH", "volumen": 1300, "futurePrice":321, "change":-5,"volumenChange":8}]
    return Response(json.dumps(predictions), status=200, mimetype='application/json')