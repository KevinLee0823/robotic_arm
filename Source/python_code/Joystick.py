#!/usr/bin/env python

import serial
from time import sleep

class Joystick:
    def __init__(self, tty='/dev/ttyUSB0', baudrate = 9600):
        self.tty = tty
        self.baudrate = baudrate
        self.serial = serial.Serial(self.tty ,self.baudrate ,timeout = 0.1)

    def read(self):
        self.serial.write('J')
        res = self.serial.readline().strip().split()
        if((res.__len__() == 8)):
            try:
                return tuple([int(i) for i in res])
            except:
                pass
        return ()
        

    def close(self):
        self.serial.close()

if __name__ == '__main__':
    try:
        joy = Joystick()
        while(1):
            sleep(0.2)
            print joy.read()
        joy.close()

    except:
        joy.close()



