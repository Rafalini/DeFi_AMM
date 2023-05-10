import requests
import time
import json
import re
import random
import numpy as np
import threading
from flask import Response
from datetime import datetime
from web_app import app
from bs4 import BeautifulSoup

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


def getWth():
  url1 = 'https://api.coingecko.com/api/v3/simple/price'
  url2 = 'https://api.binance.com/api/v3/ticker/price'
  url3 = 'https://coinmarketcap.com/currencies/weth/'
  params1 = {
      'ids': 'weth',
      'vs_currencies': 'usd'
  }
  params2 = {
      'symbol': 'WETHUSD'
  }
  response1 = requests.get(url1, params=params1)
  response2 = requests.get(url2, params=params2)
  weth_price = 0

  if response1.status_code == 200:
      data = response1.json()
      # print(data)
      weth_price += data['weth']['usd']

  if response1.status_code == 200:
      data = response2.json()
      # print(data)
      # weth_price += data['price']
  
  page = requests.get(url3)
  soup = BeautifulSoup(page.content, "html.parser")
  elements = soup.find_all("div", class_="priceValue")

  # for entry in elements:
  #   if entry.text[0] == '$':
  #     # result = re.search('\$[0-9]+,[0-9]*\.[0-9]+<', elements)
  #     weth_price += float(entry.text[1:].replace(',', ''))
  #     break;

  return weth_price

# def getSingle():
#   url3 = 'https://coinmarketcap.com/currencies/weth/'
#   page = requests.get(url3)
#   soup = BeautifulSoup(page.content, "html.parser")
#   elements = soup.find_all("div", class_="priceValue")
#   print(elements)
#   for entry in elements:
#     print(entry.text)
#     if entry.text[0] == '$':
#       # result = re.search('\$[0-9]+,[0-9]*\.[0-9]+<', elements)
#       return float(entry.text[1:].replace(',', ''))


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
    for entry in data:
        if entry["id"] not in uniswapHistory:
          uniswapHistory[entry["id"]] = []
        if entry["token0"]["symbol"] not in uniformHistory:
          uniformHistory[entry["token0"]["symbol"]] = []
        valueEntry = {}
        valueEntry["dateTime"] = datetime.now().strftime("%H:%M:%S")
        valueEntry["token0name"] = entry["token0"]["symbol"]
        valueEntry["token0value"] = entry["token0Price"]
        valueEntry["token1name"] = entry["token1"]["symbol"]
        valueEntry["token1value"] = entry["token1Price"]
        uniswapHistory[entry["id"]].append(valueEntry)



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
        uniformEntry["price"] = entry["price"]

        balancerHistory[entry["symbol"]].append(valueEntry)
        uniformHistory[entry["symbol"]].append(uniformEntry)

def updateRates():
  while(True):
      pairs = getUniswapTokens(uniswapApiURL, uniswapQueryBody)
      addUniswapHistoryEntry(pairs)

      pairs = getBalancerTokens(balanceApiURL, balancerQueryBody)
      addBalancerHistoryEntry(pairs)

      time.sleep(3)
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
          response.append({"symbol" : entry, "price" : uniformHistory[entry][index]["price"], "updated": uniformHistory[entry][index]["dateTime"]})
    return Response(json.dumps(response), status=200, mimetype='application/json')