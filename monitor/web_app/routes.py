from web_app import amm, app, logger, sock, MCAST_GRP, MCAST_PORT
from flask import Response, request, render_template, stream_with_context

import json, time, requests

from datetime import datetime

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", changes=amm.getCurrencies())


@app.route("/get-currencies")
def getCurrencies():
    return Response(json.dumps(amm.getCurrencies()), status=200, mimetype='application/json')


def getChanges():
    client_ip = request.remote_addr
    try:
        while True:
            yield f"data:{json.dumps(amm.lastTransactionChanges())}\n\n"
            time.sleep(1)
    except GeneratorExit:
        logger.info("Client %s disconnected", client_ip)


def getCurrentAmounts():
    client_ip = request.remote_addr
    try:
        logger.info("Client %s connected", client_ip)
        while True:

            data = {}
            data["time"] = datetime.now().strftime("%H:%M:%S")
            data["amounts"] = amm.getAmounts()
            data["rates"] = amm.getRates()
            data["transactions"] = amm.getTransactions()

            try:
                response = requests.get('http://192.168.10.2:8000/get-values')
                data["prices"] = response.json()
            except:
                pass

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


@app.route("/changes-data", methods=['GET'])
def changesData() -> Response:
    response = Response(stream_with_context(getChanges()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@app.route("/transaction", methods=['GET', 'POST'])
def transaction() -> Response:
    
    result = amm.performTransaction(request)
    
    if result:
        for blockChainTransaction in result:
            sock.sendto(bytes(json.dumps(blockChainTransaction), 'utf-8'), (MCAST_GRP, MCAST_PORT))
            
        return Response({"message": "ok", "recieved": result[1]["amount"], "currency": request.json["to"]}, status=200,
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
    return amm.getRates()