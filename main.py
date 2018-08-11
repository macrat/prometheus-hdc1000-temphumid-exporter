#!/usr/bin/python3

import http.server
import os
import struct
import time

import RPi.GPIO as gpio
import wiringpi


SHT31_ADDRESS = 0x40
READY_PIN_ID = 7

HTTP_HOST = ''
HTTP_PORT = 9100
TEMPERATURE_LABEL = 'sht31_temperature{}'
HUMIDITY_LABEL = 'sht31_humidity{}'


class TempHumid:
    def __init__(self):
        gpio.setmode(gpio.BOARD)
        gpio.setup(READY_PIN_ID, gpio.IN)

        wiringpi.wiringPiSetupSys()
        self.i2c = wiringpi.I2C()
        self.bus = self.i2c.setup(SHT31_ADDRESS)
        time.sleep(0.03)

    def read(self):
        self.i2c.writeReg8(self.bus, 0x00, 0x01)

        while gpio.input(READY_PIN_ID) == 1:
            time.sleep(0.01)

        temp, humid = struct.unpack('>2H', os.read(self.bus, 4))

        temp = temp * 165.0 / 65536.0 - 40.0
        humid = humid / 65536.0

        return temp, humid


class Handler(http.server.BaseHTTPRequestHandler):
    sensor = TempHumid()

    def do_GET(self):
        temp, humid = self.sensor.read()
        self.send_response(200)
        self.end_headers()
        self.wfile.write('{} {}\n{} {}\n'.format(
            TEMPERATURE_LABEL,
            temp,
            HUMIDITY_LABEL,
            humid,
        ).encode('utf-8'))


if __name__ == '__main__':
    http.server.HTTPServer((HTTP_HOST, HTTP_PORT), Handler).serve_forever()
