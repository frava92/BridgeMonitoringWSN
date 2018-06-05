from __future__ import division

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import RPi.GPIO as GPIO
from lib.lib_nrf24 import NRF24
import spidev
import logging
import csv
import Adafruit_ADS1x15
from datetime import datetime
from time import sleep, strftime, time

GPIO.setmode(GPIO.BCM)
pipes = [[0x78, 0x78, 0x78, 0x78, 0x78], [0xb3, 0xb4, 0xb5, 0xb6, 0xF1], [0xcd], [0xa3], [0x0f], [0x05]]

spi = spidev.SpiDev()

radio = NRF24(GPIO, spi)
radio.begin(0, 17)
spi.max_speed_hz = 7629
radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MAX)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe(pipes[1])
radio.openReadingPipe(1, pipes[1])

radio.printDetails()
radio.startListening()

unique_ID = "1_"

reportes_path = '../reportes/'
csvfile_path = reportes_path + str(datetime.now().date()) + '.csv'

################# ADC Setup #################
adc_input = Adafruit_ADS1x15.ADS1115()
GAIN = 1

def readSensor():
    flex = adc_input.read_adc_difference(0, gain=GAIN)
    return str(flex)
    
def sendData(ID, value):
    radio.stopListening()
    time.sleep(0.25)
    message = list(ID) + list(value)
    logger.info("Iniciando envio de datos.")
    radio.write(message)
    logger.info("Datos enviados")
    radio.startListening()

def main():
	while(1):
		ackPL = [1]
		radio.writeAckPayload(1, ackPL, len(ackPL))
		while not radio.available(0):
			sleep(1 / 100)
		receivedMessage = []
		radio.read(receivedMessage, radio.getDynamicPayloadSize())
		print("Recibido: {}".format(receivedMessage))
		
		print("Traduciendo el mensaje recibido...")
		string = ""
		for n in receivedMessage:
			# Decode into standard unicode set
			if (n >= 32 and n <= 126):
				string += chr(n)
		print(string)
		
		# We want to react to the command from the master.
		command = string
		if command == "GET_DATA":
			logger.info("Solicitud de datos recibida")
			flex = readSensor()
			sendData(receiver_ID, flex)
		elif command == "HEY_LISTEN":
			print("Secuencia de autoconfiguracion")
			radio.stopListening()
			sleep(0.25)
			radio.writeAckPayload(1, ackPL, len(ackPL))
			radio.startListening()
		command = ""
		radio.writeAckPayload(1, ackPL, len(ackPL))
		print("Cargando respuesta de carga {}".format(ackPL))
		
if __name__ == "__main__":
	main()
