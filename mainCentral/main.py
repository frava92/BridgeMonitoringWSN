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

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(0, pipes[0])
radio.openReadingPipe(1, pipes[1])
radio.openReadingPipe(2, pipes[2])
radio.openReadingPipe(3, pipes[3])
radio.openReadingPipe(4, pipes[4])
radio.openReadingPipe(5, pipes[5])

radio.printDetails()

unique_ID = "0_"

refreshRate = 30
WakeUpRetriesCount = 0
MaxRetriesWakeUp = 5
NodesUpCount = 0
NodesUpPipe = []
NodeCount = 1
exists_flag = 0
csvHeading = "Timestamp,"
reportes_path = '../reportes/'
csvfile_path = reportes_path + str(datetime.now().date()) + '.csv'


def receiveData():
    print("Listo para recibir los datos.")
    radio.startListening()

    while not radio.available(0):
        sleep(1 / 100)

    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())

    print("Traduciendo el mensaje...")
    string = ""
    for n in receivedMessage:
        # Decode into standard unicode set
        if (n >= 32 and n <= 126):
            string += chr(n)
    print("EL mensaje recibido fue: {}".format(string))
    radio.stopListening()
    return string

print ("Iniciando secuencia de autoconfiguracion")
for pipeCount in range(0, len(pipes)-1):
	WakeUpRetriesCount = 0
	radio.openWritingPipe(pipes[pipeCount])
	print("Abriendo pipes de transmision")
	radio.print_address_register("TX_ADDR", NRF24.TX_ADDR)
	while (WakeUpRetriesCount <= MaxRetriesWakeUp):
		print("Enviando mensaje de busqueda")
		print("Mensaje enviado: HEY_LISTEN")
		radio.write(list("HEY_LISTEN"))
		if radio.isAckPayloadAvailable():
			print("Nodo encontrado!")
			returnedPL = []
			radio.read(returnedPL, radio.getDynamicPayloadSize())
			print("Los datos recibidos son: {} ".format(returnedPL))
			NodesUpPipe.append(pipes[pipeCount])
			NodesUpCount += 1
			break
		else:
			print("No hubo respuesta... Reintentando")
			if WakeUpRetriesCount == MaxRetriesWakeUp:
				print("Nodo no esta activo en el pipe, intentando en otro pipe")
			WakeUpRetriesCount += 1
			sleep(1)
delay = 1/(NodesUpCount*refreshRate)
print("Configuracion finalizada... {0} Nodos activos".format(str(NodesUpCount)))
print("Tiempo de retardo: {}".format(str(delay)))

if (os.path.isfile(str(csvfile_path))):
	exists_flag = 1
	print("El archivo ya existe!")
else:
	exists_flag= 0
	print("Archivo inexistente!")
	print("Creando archivo nuevo")

while (NodeCount <= NodesUpCount):
	if NodeCount == NodesUpCount:
		csvHeading = csvHeading+"Sensor"+str(NodeCount)+"\n"
	else:
		csvHeading = csvHeading+"Sensor"+str(NodeCount)+","
	NodeCount += 1

def main():
	with open(csvfile_path, 'a') as csvfile:
		if (exists_flag == 0):
			csvfile.write(csvHeading)
		print("Iniciando Toma de Datos")
		while(1):
			command = "GET_DATA"
			print(NodesUpCount)
			for pipeCount in range(0, NodesUpCount):
				radio.openWritingPipe(NodesUpPipe[pipeCount])
				radio.write(list(command))
				print("Mensaje enviado: {}".format(list(command)))
				if radio.isAckPayloadAvailable():
					returnedPL = []
					radio.read(returnedPL, radio.getDynamicPayloadSize)
					print("Recibido: {}".format(returnedPL))
					message = receiveData()
					#crear array para escribir, escribir al final del ciclo de nodos
					csvfile_stream = str(datetime.now())+","+str(message)
					print(csvfile_stream)
					
					#csvfile.write("{0},{1}\n".format(str(datetime.now()),str(message)))
				else:
					print("No se recibieron datos")
				sleep(delay)
			print("DEBUG: final del ciclo")
			sleep(1)

if __name__ == "__main__":
	main()
