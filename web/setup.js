$(function searchForIp() {
    if ("WebSocket" in window) {
        // use WebSocket
    } else if ("MozWebSocket" in window) {
        WebSocket = MozWebSocket;
    }

    var foundSleepMonitor = false;

    function tryIp(ipIdx) {
        var uri = "192.168.1." + ipIdx;
        var wsuri = "ws://" + uri + ":9000/ws";
        var sock = null;

        try {
            sock = new WebSocket(wsuri);
        } catch (err) {
            return;
        }

        if (sock) {
            sock.onopen = function() {
                console.log("Connected to " + wsuri);
            };

            sock.onclose = function(e) {
                sock = null;
            };

            sock.onmessage = function(e) {
                var msg = JSON.parse(e.data);
                
                if (msg.id === "hello") {
                    console.log("Found sleep monitor at " + uri + "!");

                    foundSleepMonitor = true;
                    sendJsonMessage('req-ssid-list', {});

                } else if (msg.id == 'ack-ssid-list') {
                    var ssidList = msg.data;
                    console.log(ssidList);

                    $('#ssid-list-container').show();

                    var el = $("#wifi-ssid-selector");
                    el.empty();
                    $.each(ssidList, function(idx, ssid) {
                        el.append($("<option>").attr('value', ssid).text(ssid));
                    });

                    $('#wifi-connect').click(function() {
                        var ssid = $('#wifi-ssid-selector').val();
                        var passwd = $('#wifi-password').val();
                        sendJsonMessage('req-set-ssid-passwd', {ssid: ssid, passwd: passwd});
                        $('#set-ssid-passwd-status-container').show();
                    });

                } else if (msg.id == 'ack-set-ssid-passwd') {
                    var status = msg.data;
                    console.log(status);

                    $('#set-ssid-passwd-status').text(status);
                    if (status === 'ok') {
                        $('#step3').show();
                    }
                }
            };
        }

        function sendJsonMessage(id, data) {
            sock.send(JSON.stringify({id: id, data: data}));
        }
    }


    var MIN_IP = 2;
    var MAX_IP = 255;

    var curIdx = MIN_IP;
    function tryNextIp() {
        if (foundSleepMonitor === false && curIdx <= MAX_IP) {
            tryIp(curIdx);
            curIdx += 1;
            setTimeout(tryNextIp, 100);
        }
    }

    $('#step2-button').click(function() {
        $('#step2').show();
        tryNextIp();
    });
});
