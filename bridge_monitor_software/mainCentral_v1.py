import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
import logging
import csv
from pathlib import Path
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

<<<<<<< HEAD
reportes_path = './reportes/'
csvfile_path = reportes_path + str(datetime.now().date()) + '.csv'
=======
>>>>>>> 96d5ee141f991a610937bfd3ecff2003ea22e808
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

<<<<<<< HEAD
with open(csvfile_path, 'a') as csvfile:
	if (os.path.exists(csvfile) == False):
        csvfile.write("timestamp,sensor1\n")
=======
my_report = Path("./reportes/test2.csv")
with open('./reportes/test2.csv', 'a') as csvfile:
	if (os.path.isfile(csvfile) == False):
		csvfile.write("timestamp,sensor1\n")
>>>>>>> 96d5ee141f991a610937bfd3ecff2003ea22e808
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
			csvfile.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(message)))
			#START = 0
		else:
			print("No se recibieron datos")
		sleep(1/33)
