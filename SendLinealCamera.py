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


radio.openWritingPipe(pipes[1])
radio.openReadingPipe(1, pipes[0])

radio.printDetails()

#radio.startListening()


filePath = os.path.abspath("./test.b64")
if filePath.split(".")[-1] != "b64":
    raise TypeError(
        f"Wrong file type: .b64 expected, {filePath.split('.')[-1]} got")
with open(filePath, "r") as file:
    data = file.read()
    print(
        " ".join(["data len: ", str(len(data)), "\ndata:", ",".join(data)[:100]]))
    # file.close()
packedData = splitStringToPieces(data)[0]

print(
    f"Bytes to be transmitted: {len(data)}\nPackages to be transmitted: {len(packedData)}\nEstimated time: {estimateTime(packedData)}")
command = [CrRadioCommand.StartImage.value, splitPieceIndex(
    len(packedData))[0], splitPieceIndex(len(packedData))[1]]
command.extend([0]*(32-len(command)))
radio.write(command)

for index in range(len(packedData)):
    _toSend = []
    # * Adding the first byte so that the
    _toSend.append(CrRadioMessageType.ImagePiece.value)
    # *      reciever knows what the message contains
    _splitIndex = splitPieceIndex(index)
    # * Adding two bytes of package index
    _toSend.append(_splitIndex[0])
    _toSend.append(_splitIndex[1])

    # * Adding actual data to the package
    _toSend.extend(packedData[index])
    print(f"Prepared package: {packedData[index]}")
    package = preparePackage(_toSend)
    radio.write(_toSend)  # * Sending package
    time.sleep(1)
