from twisted.internet import reactor, defer, ssl
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web import server, resource
from twisted.web.static import File
from autobahn.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

def async_sleep(seconds):
     d = defer.Deferred()
     reactor.callLater(seconds, d.callback, seconds)
     return d

class SetupWifiWebsocketProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        self.sendMessage('setup-sleep-monitor-hello', False)

    @inlineCallbacks
    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        for i in range(10):
            yield async_sleep(1)
            self.sendMessage(payload, isBinary)

        returnValue(None)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

def startServer():
    contextFactory = ssl.DefaultOpenSSLContextFactory('keys/server.key', 'keys/server.crt')

    factory = WebSocketServerFactory(u"wss://127.0.0.1:9000")
    factory.protocol = SetupWifiWebsocketProtocol

    reactor.listenWS(9000, factory, contextFactory)

    reactor.run()

if __name__ == "__main__":
    startServer()
