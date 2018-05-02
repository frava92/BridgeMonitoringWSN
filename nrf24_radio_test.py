#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example program to send packets to the radio link
#

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

def _BV(x):
    return 1 << x
print(radio.read_register(NRF24.EN_RXADDR))
print(_BV(NRF24.child_pipe_enable[1]))
print(radio.read_register(NRF24.EN_RXADDR) | _BV(NRF24.child_pipe_enable[1]))
