function log(msg) {
    $('#log').append(msg + '\n');
}

$(function searchForIp() {
    if ("WebSocket" in window) {
        // use WebSocket
    } else if ("MozWebSocket" in window) {
        WebSocket = MozWebSocket;
    }

    var foundSleepMonitor = false;
    var sleepMonitorIp = null;

    function tryIp(ipIdx) {
        var uri = "192.168.1." + ipIdx;
        var wsuri = "ws:" + uri + ":9000/ws";
        var sock = null;

        try {
            sock = new WebSocket(wsuri);
        } catch (err) {
            return;
        }

        if (sock) {
            sock.onopen = function() {
                log("Connected to " + wsuri);
            };

            sock.onclose = function(e) {
                sock = null;
            };

            sock.onmessage = function(e) {
                var data = e.data;
                if (data === "setup-sleep-monitor-hello") {
                    log("Found sleep monitor at " + uri + "!");
                    foundSleepMonitor = true;
                    sleepMonitorIp = uri;
                }
            };
        }
    }

    var curIdx = 2;
    function tryNextIp() {
        if (foundSleepMonitor === false && curIdx <= 255) {
            tryIp(curIdx);
            curIdx += 1;
            setTimeout(tryNextIp, 100);
        }
    }

    tryNextIp();
});
