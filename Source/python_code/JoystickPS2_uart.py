#!/usr/bin/env python

import serial
from time import sleep

class JoystickPS2_uart:

    def __init__(self, tty='/dev/ttyUSB0', baudrate = 115200):
        self.tty = tty
        self.baudrate = baudrate
        self.serial = serial.Serial(self.tty ,self.baudrate ,timeout = 0.1)

    def read(self):
        res = self.serial.readline().strip().split(',')
        if((res.__len__() >= 8)):
            try:
                return tuple([int(i) for i in res])
            except:
                pass
        return ()
        

    def close(self):
        self.serial.close()

if __name__ == '__main__':

    try:
        joy = JoystickPS2_uart()
        print 'yes'  if joy.__class__ == JoystickPS2_uart  else 'no'
        #while(1):
        #    joy.read()
        joy.close()

    except:
        joy.close()



