#!/bin/sh

CURDIR=`pwd`

# Python requirements
sudo apt-get install -y python-twisted \
    python-dateutil \
    python-autobahn

# sudo cp ./init.d/sleep-monitor /etc/init.d/
sudo sed -i "/exit 0/ i sudo python ${CURDIR}/servery.py &\n\
	" /etc/rc.local
