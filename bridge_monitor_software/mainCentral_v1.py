import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
import logging
import csv
import os
from datetime import datetime
from time import sleep, strftime, time


###########################################
##               Init Sequence           ##
###########################################

GPIO.setmode(GPIO.BCM)
pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

spi = spidev.SpiDev()

radio = NRF24(GPIO, spi)
radio.begin(0, 17)
spi.max_speed_hz = 1500000
radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MAX)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openReadingPipe(1, pipes[0])
radio.openWritingPipe(pipes[1])
radio.printDetails()

reportes_path = './reportes/'
csvfile_path = reportes_path + str(datetime.now().date()) + '.csv'
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
        sleep(1 / 100)

    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
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
    
if (os.path.isfile(str(csvfile_path))):
	exists_flag = 1
	print("El archivo ya existe!")
else:
	exists_flag = 0
	print("Archivo inexistente")
	
with open(csvfile_path, 'a') as csvfile:
	if (exists_flag == 0):
		csvfile.write("timestamp,sensor1\n")
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
			csvfile.write("{0},{1}\n".format(str(datetime.now()),str(message)))
			#START = 0
		else:
			print("No se recibieron datos")
		sleep(1/33)
