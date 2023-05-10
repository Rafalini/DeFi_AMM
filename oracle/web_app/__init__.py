#!/usr/bin/env python
import os
import sys
import json
import logging
from flask import Flask

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
app = Flask(__name__)

from web_app import routes