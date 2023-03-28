#!/usr/bin/env python
import os
import json
import logging
import random
import sys
import time
import math
from datetime import datetime

from flask import Flask, Response, render_template, request, stream_with_context
  
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
app = Flask(__name__)

config_file = open('config.json')
config = json.load(config_file)
currencies = {}
const_product_k = 1
const_sum_k = 0

for entry in config["currencies"]:
    currencies[entry["short"]] = {"amount":entry["amount"], "minimal_part": entry["minimal_part"]}
    const_product_k *= entry["amount"]
    const_sum_k += entry["amount"]



@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")


def getCurrentAmounts():
    client_ip = request.remote_addr
    try:
        logger.info("Client %s connected", client_ip)
        while True:

            data = {}
            data["time"] = datetime.now().strftime("%H:%M:%S")

            amounts = {}
            rates = {}
            for currency in currencies:
                amounts[currency] = currencies[currency]["amount"]
                if currency != "BTC":
                    rates[currency] = currencies[currency]["amount"] / currencies["BTC"]["amount"]

            data["amounts"] = amounts
            data["rates"] = rates

            yield f"data:{json.dumps(data)}\n\n"
            time.sleep(0.4)
    except GeneratorExit:
        logger.info("Client %s disconnected", client_ip)


@app.route("/chart-data", methods=['GET'])
def chartData() -> Response:
    response = Response(stream_with_context(getCurrentAmounts()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


def requestedByConstantProduct(request, const_k):
    # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
    deimalRoundingDigits = abs(round(math.log10(currencies[request.json["to"]]["minimal_part"])))
    requested = currencies[request.json["to"]]["amount"] - round(const_k / (request.json["amount"] + currencies[request.json["from"]]["amount"]), deimalRoundingDigits)
    return requested


def requestedByConstantSum(request, const_k):
    # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
    deimalRoundingDigits = abs(round(math.log10(currencies[request.json["to"]]["minimal_part"])))
    requested = currencies[request.json["to"]]["amount"] - round(const_k - (request.json["amount"] + currencies[request.json["from"]]["amount"]), deimalRoundingDigits)
    return requested


def proportional(request):
    # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
    deimalRoundingDigits = abs(round(math.log10(currencies[request.json["to"]]["minimal_part"])))
    factor = currencies[request.json["to"]]["amount"] / currencies[request.json["from"]]["amount"]
    requested = round(request.json["amount"] * factor, deimalRoundingDigits)
    return requested


@app.route("/transaction", methods=['GET', 'POST']) 
def transaction() -> Response:
    
    if request.json["to"] == request.json["from"]:
        return Response ({"message":"From and to tokens are equal"}, status=500, mimetype='application/json')

    requested = requestedByConstantProduct(request, const_product_k)
    # requested = requestedByConstantSum(request, const_sum_k)
    # requested = proportional(request)

    if currencies[request.json["to"]]["amount"] - requested > 0:
        
        currencies[request.json["from"]]["amount"] += request.json["amount"]
        currencies[request.json["to"]]["amount"] -= requested

        return Response ({"message":"ok", "recieved" : requested, "currency": request.json["to"]}, status=200, mimetype='application/json')
    else: 
        return Response ({"message":"no sufficient credits in pool"}, status=500, mimetype='application/json')


@app.route("/get-rates", methods=['GET'])
def getRates() -> Response:
    """ {
            "BTC": {
                "BTC": 1.0,
                "ETH": 0.367309696969697
            },
            "ETH": {
                "BTC": 2.72249823037615,
                "ETH": 1.0
            }
        } 
    """
    response = {}
    for currency in currencies:
        rates = {}
        for referenceCurrency in currencies:
            if referenceCurrency != currency:
                rates[referenceCurrency] = currencies[referenceCurrency]["amount"] / currencies[currency]["amount"]
        response[currency] = rates
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv("FLASK_SERVER_PORT"), debug=True)