#!/usr/bin/env python
import os
import json
import logging
import random
import sys
import time
from datetime import datetime
from typing import Iterator

from flask import Flask, Response, render_template, request, stream_with_context
  
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
app = Flask(__name__)

config_file = open('config.json')
config = json.load(config_file)

@app.route("/")
def index():
    return render_template("index.html")

def generate_random_data():
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr or ""

    try:
        logger.info("Client %s connected", client_ip)
        while True:
            json_data = json.dumps(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "BTC": 40 + random.random() * 10,
                    "ETH": 60 + random.random() * 5,
                }
            )
            yield f"data:{json_data}\n\n"
            time.sleep(0.4)
    except GeneratorExit:
        logger.info("Client %s disconnected", client_ip)

@app.route("/chart-data")
def chart_data() -> Response:
    response = Response(stream_with_context(generate_random_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv("FLASK_SERVER_PORT"), debug=True)