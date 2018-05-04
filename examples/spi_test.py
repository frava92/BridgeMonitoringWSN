import spidev
from lib_nrf24 import NRF24

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 7629

buf = [0x05, 0xFF]
print("Read Buffer: ")
print(buf)
resp = spi.xfer2(buf)
print("SPI Response: ")
print(resp)


buf2 = [0x25, 0x60]
print("Write Buffer: ")
print(buf2)
resp2 = spi.xfer2(buf2)
print("SPI Response: ")
print(resp2)


buf3 = [0x05, 0xFF]
print("Read buffer: ")
print(buf3)
resp3 = spi.xfer2(buf3)
print("SPI Response: ")
print(resp3)
