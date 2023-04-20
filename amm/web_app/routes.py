from web_app import app, currencies, const_product_k, const_sum_k, logger, transactions, transactionCacheLimit
from flask import Response, request, render_template, stream_with_context

import math, json, time

from datetime import datetime

@app.route("/")
@app.route("/home")
def home():
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
            data["transactions"] = transactions

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

        # transactions = addTransaction(transactions, str(request.remote_addr)+" traded "+request.json["to"]["amount"] +" "+request.json["to"], transactionCacheLimit)
        transactions.append(str(request.remote_addr)+" traded "+str(round(requested,3)) +" "+str(request.json["to"]))
        if len(transactions) == transactionCacheLimit:
            transactions.pop(0)

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
    response["time"] = datetime.now().strftime("%H:%M:%S")
    for currency in currencies:
        rates = {}
        for referenceCurrency in currencies:
            if referenceCurrency != currency:
                rates[referenceCurrency] = currencies[referenceCurrency]["amount"] / currencies[currency]["amount"]
        response[currency] = rates
    return response