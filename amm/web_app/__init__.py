#!/usr/bin/env python
import os
import sys
import json
import logging
from flask import Flask

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
app = Flask(__name__)

config_file = open('web_app/config.json')
config = json.load(config_file)
currencies = {}
const_product_k = 1
const_sum_k = 0

for entry in config["currencies"]:
    currencies[entry["short"]] = {"amount":entry["amount"], "minimal_part": entry["minimal_part"]}
    const_product_k *= entry["amount"]
    const_sum_k += entry["amount"]


from web_app import routes