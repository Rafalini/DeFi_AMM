#!/usr/bin/env python
import os
import sys
import json
import logging
import socket
from flask import Flask
from web_app.ammDefinition import AmmClass

MCAST_GRP = '239.192.168.10'
MCAST_PORT = 5007

MULTICAST_TTL = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
app = Flask(__name__)
amm = AmmClass('web_app/config.json')

from web_app import routes