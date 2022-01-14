
import os

import spidev
import time
from CrRadio.lib_nrf24 import NRF24
import RPi.GPIO as GPIO
from CrRadio.RadioEnvironment import *



GPIO.setmode(GPIO.BCM)


pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 5)
time.sleep(1)
radio.setRetries(15, 15)
radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MIN)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()


radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])
radio.printDetails()

radio.startListening()
radio.stopListening()

radio.printDetails()

radio.startListening()
while True:
    while not radio.available([0]):
        pass
        #time.sleep(10000/1000000.0)
    print("recieved")
    buf = []
    radio.read(buf, 32)
    print(buf)
    if buf[0] == CrRadioCommand.StartImage:
        break

string = ""
with open("image.b64", "ab") as file:
    while not buf[0] == CrRadioCommand.FinishImage:
        while not radio.available([0]):
            pass
            #time.sleep(10000/1000000.0)
        # print("recieved")
        buf = []
        radio.read(buf, 32)
        file.write(buf[2:])

        
        

