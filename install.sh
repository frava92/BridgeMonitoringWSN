#!/bin/bash
sudo apt-get update
sudo apt-get install python-dev # python2
sudo apt-get install python3-dev # python3
cd ~/Downloads
wget https://github.com/Gadgetoid/py-spidev/archive/master.zip
unzip master.zip
rm master.zip
cd py-spidev-master
sudo python setup.py install # python2
sudo python3 setup.py install # python3
cd ~/Desktop
mkdir NRF24L01
cd NRF24L01
git clone -b Development https://github.com/frava92/BridgeMonitoringWSN.git
