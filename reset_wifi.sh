#!/bin/sh

cat > /etc/wpa_supplicant/wpa_supplicant.conf << EOF
country=GB
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
EOF
ifdown wlan0
ifup wlan0
