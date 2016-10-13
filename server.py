from twisted.internet import reactor, defer, ssl, utils
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web import server, resource
from twisted.web.static import File
from twisted.web.server import Site
from autobahn.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
import json
import re
import textwrap
from commands import getoutput

def async_sleep(seconds):
     d = defer.Deferred()
     reactor.callLater(seconds, d.callback, seconds)
     return d

class SetupWifiWebsocketProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def sendJsonMessage(self, id, data=''):
        jsonStr = json.dumps({'id': id, 'data': data})
        self.sendMessage(jsonStr, False)

    def onOpen(self):
        print("WebSocket connection open.")
        self.sendJsonMessage('hello')

    @inlineCallbacks
    def setWifiPasswd(self, ssid, passwd):
        config = r"""
        country=GB
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1

        network={
            ssid="%s"
            psk="%s"
        }
        """ % (ssid, passwd)

        config = textwrap.dedent(config)
        open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w').write(config)

        yield utils.getProcessOutput('/sbin/ifdown', ['wlan0'])
        yield utils.getProcessOutput('/sbin/ifup', ['wlan0'])

        ACK_ID = 'ack-set-ssid-passwd'
        MAX_TRIES = 20
        for i in range(MAX_TRIES):
            yield async_sleep(1)
            output = yield utils.getProcessOutput('/sbin/ifconfig', ['wlan0'])
            print '-'*60
            print output
            print '-'*60

            if 'inet addr:' in output:
                self.sendJsonMessage(ACK_ID, 'ok')
                returnValue(None)
            else:
                self.sendJsonMessage(ACK_ID, 'wait %d/%d' % (i+1, MAX_TRIES))

        self.sendJsonMessage(ACK_ID, 'failed')

    @inlineCallbacks
    def onMessage(self, payload, isBinary):
        obj = json.loads(payload)
        msgid = obj['id']

        if msgid == 'req-ssid-list':
            output = yield utils.getProcessOutput('/sbin/iwlist', ['wlan0', 'scan'])
            ssids = re.findall(r'ESSID:"(\S+)"', output) 
            # We seem to get some strange SSIDs with a whole bunch of \x00
            # characters (cell-towers?). This filters those out.
            ssids = [ssid for ssid in ssids if not ssid.startswith(r'\x00')]
            self.sendJsonMessage('ack-ssid-list', ssids)

        elif msgid == 'req-set-ssid-passwd':
            msgdata = obj['data']
            ssid = msgdata['ssid']
            passwd = msgdata['passwd']
            print 'Setting password for %s to %s' % (ssid, passwd)
            self.setWifiPasswd(ssid, passwd)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

def startServer():
    output = getoutput('ifconfig wlan0')
    if 'inet addr:' in output:
        print 'wlan0 already connected!'
        return

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = SetupWifiWebsocketProtocol
    reactor.listenTCP(9000, factory)

    reactor.run()

if __name__ == "__main__":
    startServer()
