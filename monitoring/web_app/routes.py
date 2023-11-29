from web_app import app, currencies, const_product_k, const_sum_k, logger, transactions, transactionCacheLimit
from flask import Response, request, render_template, stream_with_context

import math, json, time, requests, socket

from datetime import datetime

MCAST_GRP = '239.192.168.10'
MCAST_PORT = 5007

MULTICAST_TTL = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

@app.route("/")
@app.route("/home")
def home():
    curr = []
    for entry in currencies:
        print(entry)
        curr.append({"currency": entry})
    return render_template("index.html", changes=curr)


@app.route("/get-currencies")
def getCurrencies():
    response = []
    for entry in currencies:
        response.append(entry)
    return Response(json.dumps(response), status=200, mimetype='application/json')


def getChanges():

    try:
        while True:
            changes = []
            if len(transactions) > 0:
                transaction = transactions[0]
                price = currencies[transaction["from"]]["amount"] / currencies[transaction["to"]]["amount"]
                lastPrice = (currencies[transaction["from"]]["amount"] - transaction["amountFrom"]) / (currencies[transaction["to"]]["amount"] + transaction["amountTo"])

                volumeChange = transaction["amountFrom"] / currencies[transaction["from"]]["volume"]
                priceChange = (price - lastPrice)/price

                changes.append({"currency":transaction["from"], "volume": round(currencies[transaction["from"]]["volume"],3), "volumeChange": round(volumeChange*100,5),
                                "price": round(price,3), "change": round(priceChange*100, 3)})

                price = currencies[transaction["to"]]["amount"] / currencies[transaction["from"]]["amount"]
                lastPrice = (currencies[transaction["to"]]["amount"] - transaction["amountTo"]) / (currencies[transaction["from"]]["amount"] + transaction["amountFrom"])

                volumeChange = transaction["amountTo"] / currencies[transaction["to"]]["volume"]
                priceChange = (lastPrice - price)/price

                changes.append({"currency":transaction["to"], "volume": round(currencies[transaction["to"]]["volume"],3), "volumeChange": round(volumeChange*100,5),
                                "price": round(price,3), "change": round(priceChange*100, 3)})

            yield f"data:{json.dumps(changes)}\n\n"
            time.sleep(1)
    except GeneratorExit:
        pass


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

            response = requests.get('http://192.168.10.2:8000/get-values')
            # sortedResponse = response.json().sort(key=lambda x: float(x["price"]))

            data["prices"] = response.json()
            data["amounts"] = amounts
            data["rates"] = rates
            data["transactions"] = transactions

            yield f"data:{json.dumps(data)}\n\n"
            time.sleep(4)
    except GeneratorExit:
        logger.info("Client %s disconnected", client_ip)

# how to make it once
@app.route("/chart-data", methods=['GET']) 
def chartData() -> Response:
    # response = Response(stream_with_context(getCurrentAmounts()), mimetype="text/event-stream")
    response = Response()
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


# @app.route("/changes-data", methods=['GET'])
# def changesData() -> Response:
#     response = Response(stream_with_context(getChanges()), mimetype="text/event-stream")
#     response.headers["Cache-Control"] = "no-cache"
#     response.headers["X-Accel-Buffering"] = "no"
#     return response


def requestedByConstantProduct(request, const_k):
    # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
    deimalRoundingDigits = abs(round(math.log10(currencies[request.json["to"]]["minimal_part"])))
    requested = currencies[request.json["to"]]["amount"] - round(
        const_k / (request.json["amount"] + currencies[request.json["from"]]["amount"]), deimalRoundingDigits)
    return requested


def requestedByConstantSum(request, const_k):
    # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
    deimalRoundingDigits = abs(round(math.log10(currencies[request.json["to"]]["minimal_part"])))
    requested = currencies[request.json["to"]]["amount"] - round(
        const_k - (request.json["amount"] + currencies[request.json["from"]]["amount"]), deimalRoundingDigits)
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
        return Response({"message": "From and to tokens are equal"}, status=500, mimetype='application/json')

    requested = requestedByConstantProduct(request, const_product_k)
    # requested = requestedByConstantSum(request, const_sum_k)
    # requested = proportional(request)

    if currencies[request.json["to"]]["amount"] - requested > 0:

        currencies[request.json["from"]]["amount"] += request.json["amount"]
        currencies[request.json["from"]]["volume"] += abs(request.json["amount"])
        currencies[request.json["to"]]["amount"] -= requested
        currencies[request.json["to"]]["volume"] += abs(requested)



        # transactions = addTransaction(transactions, str(request.remote_addr)+" traded "+request.json["to"]["amount"] +" "+request.json["to"], transactionCacheLimit)
        transactions.insert(0,
                            {"peer": str(request.remote_addr), "from": request.json["from"], "to": request.json["to"],
                             "amountFrom": request.json["amount"], "amountTo": requested})
        # transactions.insert(0, str(request.remote_addr)+" traded "+str(round(requested,3)) +" "+str(request.json["to"])+"\n")
        if len(transactions) == transactionCacheLimit:
            transactions.pop(len(transactions) - 1)

        blockChainTransaction={}
        blockChainTransaction["sender"] = request.json["client"]
        blockChainTransaction["reciever"] = "0xAMM"
        blockChainTransaction["amount"] = request.json["amount"]
        blockChainTransaction["token"] = "ECR17"
        blockChainTransaction["sender_signature"] = "singature"
        data_string = json.dumps(blockChainTransaction) #data serialized
        sock.sendto(bytes(data_string, 'utf-8'), (MCAST_GRP, MCAST_PORT))

        blockChainTransaction["sender"] = "0xAMM"
        blockChainTransaction["reciever"] = request.json["client"]
        blockChainTransaction["amount"] = requested
        blockChainTransaction["token"] = "ECR3"
        blockChainTransaction["sender_signature"] = "singature"
        data_string = json.dumps(blockChainTransaction) #data serialized
        sock.sendto(bytes(data_string, 'utf-8'), (MCAST_GRP, MCAST_PORT))

        return Response({"message": "ok", "recieved": requested, "currency": request.json["to"]}, status=200,
                        mimetype='application/json')
    else:
        return Response({"message": "no sufficient credits in pool"}, status=500, mimetype='application/json')


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
            # if referenceCurrency != currency:
            rates[referenceCurrency] = currencies[referenceCurrency]["amount"] / currencies[currency]["amount"]
        response[currency] = rates
    return response
