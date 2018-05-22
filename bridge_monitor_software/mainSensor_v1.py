import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
import logging
import Adafruit_ADS1x15

###########################################
##               Init Sequence           ##
###########################################

############### Radio Setup ###############
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

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])
radio.write_register(NRF24.EN_RXADDR, 0x07)
radio.write_register(NRF24.RF_SETUP, 0x08)
radio.write_register(NRF24.FEATURE, 0x06)
radio.printDetails()
receiver_ID = "1"

################# ADC Setup #################
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
waitingREQ_Counter = 0
#############################################
##           Configure Network             ##
#############################################


#############################################
##               Program Start             ##
#############################################
def readSensor():
    flex = adc_input.read_adc_difference(0, gain=GAIN)
    return str(flex)

def sendData(ID, value):
    radio.stopListening()
    time.sleep(0.25)
    message = list(ID) + list(value)
    print("Iniciando envio de datos.")
    radio.write(message)
    print("Datos enviados")
    radio.startListening()

while(START):
    ackPL = [1]
    radio.writeAckPayload(1, ackPL, len(ackPL))
    while not radio.available(0):
		#waitingREQ_Counter = waitingREQ_Counter + 1
		#if waitingREQ_Counter == 100:
			#print("Solicitud no recibida")
			#waitingREQ_Counter = 0
		time.sleep(1 / 100)
    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
    print("Recibido: {}".format(receivedMessage))
    print("Traduciendo el mensajeRecibido")
    string = ""
    for n in receivedMessage:
        # Decode into standard unicode set
        if (n >= 32 and n <= 126):
            string += chr(n)
    print(string)

    # We want to react to the command from the master.
    command = string
    if command == "GET_DATA":
        print("Solicitud de datos recibida")
        flex = readSensor()
        sendData(receiver_ID, flex)
    elif command == "HEY_LISTEN":
        print("")
        sendData(receiver_ID,)
    command = ""

    radio.writeAckPayload(1, ackPL, len(ackPL))
    print("Loaded payload reply of {}".format(ackPL))
    #time.sleep(1)
