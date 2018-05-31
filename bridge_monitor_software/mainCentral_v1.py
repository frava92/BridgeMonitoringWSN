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
pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2], [0xC3], [0xC4], [0xC5], [0xC6]]

spi = spidev.SpiDev()

radio = NRF24(GPIO, spi)
radio.begin(0, 17)
spi.max_speed_hz = 15000000
radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MAX)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openReadingPipe(0, pipes[0])
radio.openReadingPipe(1, pipes[1])
radio.openReadingPipe(2, pipes[2])
radio.openReadingPipe(3, pipes[3])
radio.openReadingPipe(4, pipes[4])
radio.openReadingPipe(5, pipes[5])
radio.openWritingPipe(pipes[1])
radio.printDetails()

WakeUpRetriesCount = 0
MaxRetriesWakeUp = 5
NodesUp = 0
NodeCount = 1
csvHeading = "Timestamp,"

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
    logger.info("Listo para recibir datos")
    radio.startListening()

    while not radio.available(0):
        sleep(1 / 100)

    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
    logger.info("Recibido: {}".format(receivedMessage))
    logger.info("Traduciendo el mensaje recibido...")
    string = ""
    for n in receivedMessage:
        # Decode into standard unicode set
        if (n >= 32 and n <= 126):
            string += chr(n)
    logger.info("El sensor envia: {}:".format(string))
    return string
    radio.stopListening()

<<<<<<< HEAD

for pipeCount in range(0, len(pipes)-1):
    WakeUpRetriesCount = 0
    radio.openWritingPipe(pipes[pipeCount])
    while (WakeUpRetriesCount <= MaxRetriesWakeUp):
        radio.write(list("WAKE_UP"))
        if radio.isAckPayloadAvailable():
            NodesUp += 1
            break
        else:
            WakeUpRetriesCount += 1
            time.sleep(1)



=======
>>>>>>> 407850e35a5369d63d6580d9e30e8c3e7c7598f0
if (os.path.isfile(str(csvfile_path))):
	exists_flag = 1
	logger.warning("El archivo ya existe!")
else:
	exists_flag = 0
	logger.warning("Archivo inexistente!")
    logger.info("Creando archivo nuevo")

<<<<<<< HEAD
while (NodeCount <= NodesUp):
    if NodeCount == NodesUp:
        csvHeading = csvHeading+"Sensor"+str(NodeCount)+"\n"
    else:
        csvHeading = csvHeading+"Sensor"+str(NodeCount)+","
    NodeCount += 1

=======
>>>>>>> 407850e35a5369d63d6580d9e30e8c3e7c7598f0
with open(csvfile_path, 'a') as csvfile:
	if (exists_flag == 0):
		csvfile.write(csvHeading)
    for pipeCount in range(0, len(pipes)-1):
        radio.openWritingPipe(pipes[pipeCount])
    while (WakeUpRetriesCount <= MaxRetriesWakeUp):
        radio.write(list("WAKE_UP"))
        if radio.isAckPayloadAvailable():
            NodesUp += 1
            break
        else:
            WakeUpRetriesCount += 1
            time.sleep(1)
	while(START):
		command = "GET_DATA"
		message = list(command)
		radio.write(message)
		logger.info("El mensaje enviado fue {} ".format(command) + "{}".format(message))

		# Check if it returned ackPL
		if radio.isAckPayloadAvailable():
			returnedPL = []
			radio.read(returnedPL, radio.getDynamicPayloadSize())
			logger.info("Los datos recibidos son: {} ".format(returnedPL))
			message = receiveData()
			csvfile.write("{0},{1}\n".format(str(datetime.now()),str(message)))
			#START = 0
		else:
			logger.error("No se recibieron datos")
		sleep(1/10)
