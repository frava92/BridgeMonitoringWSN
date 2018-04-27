import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev

GPIO.setmode(GPIO.BCM)

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

spi = spidev.SpiDev()

radio = NRF24(GPIO, spi)
radio.begin(0, 17)
spi.max_speed_hz = 15000000
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

# radio.startListening()


def receiveData():
    print("Ready to receive data.")
    radio.startListening()

    while not radio.available(0):
        time.sleep(1 / 100)

    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())

    print("Translating receivedMessage into unicode characters...")
    string = ""
    for n in receivedMessage:
        # Decode into standard unicode set
        if (n >= 32 and n <= 126):
            string += chr(n)
    print("Our slave sent us: {}:".format(string))
    radio.stopListening()

while(1):
    command = "GET_TEMP"
    message = list(command)
    # message = list("Hello World")
    radio.write(message)
    print("We sent the message of {}".format(message))

    # Check if it returned ackPL
    if radio.isAckPayloadAvailable():
        returnedPL = []
        radio.read(returnedPL, radio.getDynamicPayloadSize())
        print("Our returned payload was {}".format(returnedPL))
        receiveData()
    else:
        print("No payload received")
    time.sleep(1)
