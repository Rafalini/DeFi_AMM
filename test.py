# from twisted.web import server, resource
# from twisted.internet import reactor, endpoints

# class Counter(resource.Resource):
#     isLeaf = True
#     numberRequests = 0

#     def render_GET(self, request):
#         self.numberRequests += 1
#         request.setHeader(b"content-type", b"text/plain")
#         content = u"I am request #{}\n".format(self.numberRequests)
#         return content.encode("ascii")

# endpoints.serverFromString(reactor, "tcp:8080").listen(server.Site(Counter()))
# reactor.run()

from twisted.internet import reactor, protocol
from twisted.internet.protocol import DatagramProtocol

class TCPEcho(protocol.Factory):
    def buildProtocol(self, addr):
        return TCPEchoProtocol()

class TCPEchoProtocol(protocol.Protocol):
    def dataReceived(self, data):
        print(f"TCP Received: {data.decode()}")
        self.transport.write(data)

class UDPEcho(DatagramProtocol):
    def datagramReceived(self, data, addr):
        print(f"UDP Received: {data.decode()} from {addr}")
        self.transport.write(data, addr)

def main():
    # Create a TCP and a UDP server
    tcp_server = reactor.listenTCP(8888, TCPEcho())
    udp_server = reactor.listenUDP(8889, UDPEcho())

    reactor.run()

if __name__ == '__main__':
    main()







