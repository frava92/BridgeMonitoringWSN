import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
import logging
import csv
import os
from datetime import datetime

###########################################
##               Init Sequence           ##
###########################################

GPIO.setmode(GPIO.BCM)
pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

spi = spidev.SpiDev()

radio = NRF24(GPIO, spi)
radio.begin(0, 17)
spi.max_speed_hz = 7529
radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MIN)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openReadingPipe(1, pipes[0])
radio.openWritingPipe(pipes[1])
radio.write_register(NRF24.EN_RXADDR, 0x07)
radio.write_register(NRF24.RF_SETUP, 0x08)
radio.write_register(NRF24.FEATURE, 0x06)
radio.printDetails()

csvfile = open('./reportes/test.csv', 'a')
if os.stat("./reportes/test.csv.csv").st_size == 0:
        file.write("Time,Sensor1\n")
#############################################
##           Configure log files           ##
#############################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('./logs/mainCentral_v1.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

START = 1

#############################################
##           Configure Network             ##
#############################################

def receiveData():
    print("Ready to receive data.")
    radio.startListening()

    while not radio.available(0):
        time.sleep(1 / 100)

    receivedMessage = []
    radio.read(receivedMessage, (radio.getDynamicPayloadSize()+2))
    print("Received: {}".format(receivedMessage))
    print("Translating receivedMessage into unicode characters...")
    string = ""
    for n in receivedMessage:
        # Decode into standard unicode set
        if (n >= 32 and n <= 126):
            string += chr(n)
    print("Our slave sent us: {}:".format(string))
	return string
    radio.stopListening()

while(START):
    command = "GET_DATA"
    message = list(command)
    radio.write(message)
    print("El mensaje enviado fue {} ".format(command) + "{}".format(message))

    # Check if it returned ackPL
    if radio.isAckPayloadAvailable():
        returnedPL = []
        radio.read(returnedPL, radio.getDynamicPayloadSize())
        print("Los datos recibidos son: {} ".format(returnedPL))
        message = receiveData()
		file.write(str(datetime.now)+","+str(string))
        #START = 0
    else:
        print("No se recibieron datos")
    time.sleep(1/33)
