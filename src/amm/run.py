from twisted.internet import reactor, endpoints
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet.protocol import DatagramProtocol
import socket, json, sys
import logging, os

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from ammDefinition import AmmClass

amm = AmmClass('config.json')
# pastTransactions = []
counter = 0
TRANS_MCAST_ADRR = os.getenv("TRANSACTION_BROADCAST").split(":")[0]
TRANS_MCAST_PORT = os.getenv("TRANSACTION_BROADCAST").split(":")[1]

ammAdrr = os.getenv("AMM_SERVER_ADDR")
NODE_MCAST_ADRR = os.getenv("NODE_BROADCAST").split(":")[0]
NODE_MCAST_PORT = os.getenv("NODE_BROADCAST").split(":")[1]
MULTICAST_TTL = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)


class BaseResource(Resource):
    isLeaf = True
    def setHeaders(self, request):
        request.setHeader(b'Content-Type', b'application/json')
        request.setResponseCode(200)
        global counter
        counter += 1
        # logger.info("req cont %s from %s", counter, request.path)
        # logger.info("Client %s connected to %s", request.getClientAddress(), request.path)
        

class GetCurrencies(BaseResource):
    def render_GET(self, request):
        self.setHeaders(request)
        return json.dumps(amm.getCurrencies()).encode('utf-8')
        # return json.dumps([]).encode('utf-8')

class GetChanges(BaseResource):
    def render_GET(self, request):
        self.setHeaders(request)
        return json.dumps(amm.lastTransactionChanges()).encode('utf-8')
        # return json.dumps([]).encode('utf-8')

    

class GetAmounts(BaseResource):
    def render_GET(self, request):
        self.setHeaders(request)
        return json.dumps(amm.getAmounts()).encode('utf-8')
        # return json.dumps([]).encode('utf-8')

    

class GetRates(BaseResource):
    def render_GET(self, request):
        self.setHeaders(request)
        return json.dumps(amm.getRates()).encode('utf-8')
        # return json.dumps([]).encode('utf-8')
    

class GetTransactions(BaseResource):
    def render_GET(self, request):
        self.setHeaders(request)
        # return json.dumps(amm.getTransactions()).encode('utf-8')
        return json.dumps([]).encode('utf-8')
    
class GetPublicKey(BaseResource):
    def render_GET(self, request):
        self.setHeaders(request)
        return json.dumps(amm.pem_public).encode('utf-8')

    
class PerformTransaction(BaseResource):
    def render_POST(self, request):
        data = request.content.read()
        request.json = json.loads(data.decode('utf-8'))
        # print(request.json)
        result = amm.performTransaction(request)
        if result:
            for blockChainTransaction in result:
                sock.sendto(bytes(json.dumps(blockChainTransaction), 'utf-8'), (TRANS_MCAST_ADRR, TRANS_MCAST_PORT))
                
            response = {"message": "ok", "recieved": result[1]["amount"], "currency": request.json["to"]}
        else:
            response = {"message": "no sufficient credits in pool"}
        
        self.setHeaders(request)
        return json.dumps(response).encode('utf-8')
        # return json.dumps([]).encode('utf-8')


class MyRootResource(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.putChild(b"get-currencies", GetCurrencies())
        self.putChild(b"get-changes", GetChanges())
        self.putChild(b"get-amounts", GetAmounts())
        self.putChild(b"get-rates", GetRates())
        self.putChild(b"get-transactions", GetTransactions())
        self.putChild(b"transaction", PerformTransaction())
        self.putChild(b"get-public-key", GetPublicKey())

class NodeMulticastListener(DatagramProtocol):
    def startProtocol(self):
        # Specify the multicast address to listen to
        self.transport.joinGroup(NODE_MCAST_ADRR)

    def datagramReceived(self, data, addr):
        # Handle the incoming multicast UDP datagram here
        logger.info("Received multicast UDP data: %d [b] from %s", len(data), addr)
        js = json.loads(data.decode('utf-8'))

        for trans in js["Transactions"]:
            self.processTransaction(trans)
            print(trans)
        # pastTransactions += js["Transactions"]
        # Add your logic to process the multicast UDP data
    
    def processTransaction(transaction):
        if transaction["reciever"] == ammAdrr:
            returnTransaction = {}
            returnTransaction["sender"] = ammAdrr
            returnTransaction["reciever"] = transaction["sender"]
            returnTransaction["reciever"] = transaction["sender"]
            ###TODO

class TransactionMulticastListener(DatagramProtocol):
    def startProtocol(self):
        # Specify the multicast address to listen to
        self.transport.joinGroup(NODE_MCAST_ADRR)

    def datagramReceived(self, data, addr):
        # Handle the incoming multicast UDP datagram here
        logger.info("Received multicast UDP data: %d [b] from %s", len(data), addr)
        js = json.loads(data.decode('utf-8'))

        # for trans in js["payments etccod"]:
        #     print(trans)
        # pastTransactions += js["Transactions"]
        # Add your logic to process the multicast UDP data
        pass

reactor.listenMulticast(int(NODE_MCAST_PORT), NodeMulticastListener())
reactor.listenMulticast(int(TRANS_MCAST_PORT), TransactionMulticastListener())

root = MyRootResource()
site = Site(root)

tcp_endpoint = endpoints.TCP4ServerEndpoint(reactor, 5000)
tcp_endpoint.listen(site)

reactor.run()