import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
import logging
import Adafruit_ADS1x15

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
radio.printDetails()

adc_input = Adafruit_ADS1x15.ADS1115()
GAIN = 1
#############################################
##           Configure log files           ##
#############################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('./logs/mainSensor_v1.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

START = 1
waitingRX_Counter = 0
#############################################
##           Configure Network             ##
#############################################


#############################################
##               Program Start             ##
#############################################
def getData():
    flex = adc_input.read_adc_difference(0, gain=GAIN)
    return str(flex)

def sendData(ID, value):
    radio.stopListening()
    time.sleep(0.25)
    message = list(ID) + list(value)
    print("About to send message.")
    radio.write(message)
    print("Sent the data")
    radio.startListening()

while(START):
    ackPL = [1]
    radio.writeAckPayload(1, ackPL, len(ackPL))
    while not radio.available(0):
		waitingRX_Counter = waitingRX_Counter + 1
		if waitingRX_Counter == 100:
			logger.error("Solicitud no recibida")
			waitingRX_Counter = 0
		time.sleep(1 / 100)
    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
    logger_info("Recibido: {}".format(receivedMessage))

    logger.info("Traduciendo el mensajeRecibido")
    string = ""
    for n in receivedMessage:
        # Decode into standard unicode set
        if (n >= 32 and n <= 126):
            string += chr(n)
    logger_info(string)

    # We want to react to the command from the master.
    command = string
    if command == "GET_DATA":
        logger.info("Solicitud de datos recibida")
        flexID = "flex_"
        flex = getData()
        sendData(flexID, flex)
        #START = 0
    command = ""

    radio.writeAckPayload(1, ackPL, len(ackPL))
    logger.info("Loaded payload reply of {}".format(ackPL))
    time.sleep(1)
