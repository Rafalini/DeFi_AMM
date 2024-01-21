import json
import os
from flask import Response, request
from web_app import app
# from bs4 import BeautifulSoup
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from web_app.oracle import Oracle
ora = Oracle()

@app.route("/get-values")
def getCurrencies():
    return Response(json.dumps(ora.pricesTable), status=200, mimetype='application/json')

@app.route("/get-prices")
def getSymbols():
  modifiedValues = []
  for entry in ora.pricesTable:
     modifiedValues.append({"symbol":entry["symbol"], "usdprice":entry["usdprice"] + entry["modificator"]})
  return Response(json.dumps(modifiedValues), status=200, mimetype='application/json')

@app.route("/set-modifier")
def setModifier():
  for entry in ora.pricesTable:
     print(entry["symbol"])
     if entry["symbol"] == request.args.get('token'):
        entry["modificator"] = float(request.args.get('value'))
        return Response("New value: "+str(entry["usdprice"] + entry["modificator"]), status=200)
  return Response("Error", status=400)

# @app.route("/get-predictions")
# def getPredictions():
#     predictions = [{"currency":"BTC", "volumen": 1300, "futurePrice":123, "change":5, "volumenChange":8},
#                    {"currency":"ETH", "volumen": 1300, "futurePrice":321, "change":-5,"volumenChange":8}]
#     return Response(json.dumps(predictions), status=200, mimetype='application/json')