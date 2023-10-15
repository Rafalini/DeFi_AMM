import time
import socket
import json


MCAST_GRP = '239.192.168.10'
MCAST_PORT = 5007

MULTICAST_TTL = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

for i in range(10):
    time.sleep(0.1)

    # data = {}
    # data["type"] = "transaction"
    transaction = {}

    transaction["sender"] = "0x123"+str(i)
    transaction["reciever"] = "0x321"
    transaction["amount"] = 5
    transaction["token"] = "ECR17"
    transaction["sender_signature"] = "sigsig"+str(i)
    # data["data"] = transaction

    data_string = json.dumps(transaction) #data serialized
    print(data_string)
    sock.sendto(bytes(data_string, 'utf-8'), (MCAST_GRP, MCAST_PORT))
    # print("sent "+str(i))
