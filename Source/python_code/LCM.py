#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
from sys import argv
from multiprocessing import Process, Queue, queues
from threading import Thread

class LCM1602:
    def __init__(self, debug_mode = False):
        # use the BOARD mode pinout setup (the phy pins of 40)
        GPIO.setmode(GPIO.BOARD)
        # the pinset for "Rasp Pi I/O" sub board produced by ittraining.com.tw
        self.LCD_RS = 38
        self.LCD_RW = 40
        self.LCD_E  = 29
        self.LCD_D4 = 31
        self.LCD_D5 = 33
        self.LCD_D6 = 35
        self.LCD_D7 = 37
        self.CMD_DELAY = 0.0002
        self.CMD_CLEAR_DELAY = 0.001
        self.msg = [0,0,0,0,0,0,0,0,0]
        self.debug_mode = debug_mode 
        self.init()
        self.the_queue = Queue()
        self.process = Process(target=self.run_motor_position,args=())
        self.process.start()

    def write_byte(self , cmd , RS):
        GPIO.output(self.LCD_RS, RS)
        GPIO.output(self.LCD_RW, 0)
        GPIO.output(self.LCD_E , 0)

        # write high 4 bits
        if((cmd & 0x10) == 0x10):
            GPIO.output(self.LCD_D4, 1)
        else:
            GPIO.output(self.LCD_D4, 0)
        if((cmd & 0x20) == 0x20):
            GPIO.output(self.LCD_D5, 1)
        else:
            GPIO.output(self.LCD_D5, 0)
        if((cmd & 0x40) == 0x40):
            GPIO.output(self.LCD_D6, 1)
        else:
            GPIO.output(self.LCD_D6, 0)
        if((cmd & 0x80) == 0x80):
            GPIO.output(self.LCD_D7, 1)
        else:
            GPIO.output(self.LCD_D7, 0)

        sleep(0.000001)
        GPIO.output(self.LCD_E, 0)
        sleep(0.000001)
        GPIO.output(self.LCD_E, 1)
        sleep(0.000001)
        GPIO.output(self.LCD_E, 0)

        # write low 4 bits
        if((cmd & 0x01) == 0x01):
            GPIO.output(self.LCD_D4, 1)
        else:
            GPIO.output(self.LCD_D4, 0)
        if((cmd & 0x02) == 0x02):
            GPIO.output(self.LCD_D5, 1)
        else:
            GPIO.output(self.LCD_D5, 0)

        if((cmd & 0x04) == 0x04):
            GPIO.output(self.LCD_D6, 1)
        else:
            GPIO.output(self.LCD_D6, 0)

        if((cmd & 0x08) == 0x08):
            GPIO.output(self.LCD_D7, 1)
        else:
            GPIO.output(self.LCD_D7, 0)

        sleep(0.000001)
        GPIO.output(self.LCD_E, 0)
        sleep(0.000001)
        GPIO.output(self.LCD_E, 1)
        sleep(0.000001)
        GPIO.output(self.LCD_E, 0)

        sleep( self.CMD_DELAY )

    def write_data(self, data):
        self.write_byte(data, 1)

    def write_command(self, cmd):
        self.write_byte(cmd, 0)

    def set_pic(self,num,data):
        CG_ADDR = num * 8
        self.write_command(CG_ADDR + 0x40)
        for i in data:
            self.write_data(i)

    def init(self):
        # setup the pin out
        GPIO.setup(self.LCD_E,  GPIO.OUT) # E
        GPIO.setup(self.LCD_RS, GPIO.OUT) # RS
        GPIO.setup(self.LCD_RW, GPIO.OUT) # RW
        GPIO.setup(self.LCD_D4, GPIO.OUT) # DB4
        GPIO.setup(self.LCD_D5, GPIO.OUT) # DB5
        GPIO.setup(self.LCD_D6, GPIO.OUT) # DB6
        GPIO.setup(self.LCD_D7, GPIO.OUT) # DB7

        # initialize the level of all pin
        GPIO.output(self.LCD_D4,0)
        GPIO.output(self.LCD_D5,0)
        GPIO.output(self.LCD_D6,0)
        GPIO.output(self.LCD_D7,0)
        GPIO.output(self.LCD_RS,0)
        GPIO.output(self.LCD_RW,0)
        GPIO.output(self.LCD_E,0)
        
        sleep(0.1)
        GPIO.output(self.LCD_E,1)
        sleep(0.000001)
        GPIO.output(self.LCD_E,0)
        sleep(0.000001)

        ### reset the LCD and use the 4 bit (4-lines) mode
        sleep(0.002)
        self.write_byte(0x03,0)
        sleep(0.001)
        self.write_byte(0x03,0)
        sleep(0.0001)
        self.write_byte(0x03,0)
        sleep(0.0001)
        self.write_byte(0x02,0)
        sleep(0.0001)
        ### end reset procedure
        
        # function setup 
        self.write_command(0x28)
        
        self.write_command(0x0c)
        self.write_command(0x01)
        sleep(self.CMD_CLEAR_DELAY)

        self.write_command(0x06)
        sleep(0.001)
        pic01 = [0x4,0xe,0x1f,0x4,0x4,0x4,0x4,0x4]
        pic02 = [0x4,0x4,0x4,0x4,0x4,0x1f,0xe,0x4]
        pic03 = [0x2,0x6,0xe,0x1f,0x1f,0xe,0x6,0x2]
        pic04 = [0x8,0xc,0xe,0x1f,0x1f,0xe,0xc,0x8]
        pic05 = [0x0,0xe,0x11,0x11,0x11,0xe,0x0,0x0]
        pic06 = [0x0,0xe,0x1f,0x1f,0x1f,0xe,0x0,0x0]
        self.set_pic(0,pic01)
        self.set_pic(1,pic02)
        self.set_pic(2,pic03)
        self.set_pic(3,pic04)
        self.set_pic(4,pic05)
        self.set_pic(5,pic06)

    def move(self,line,col):
        _pos = 0x80 + (line-1) * 0x40 + (col-1)
        self.write_command(_pos)

    def writeStr(self,_str):
        ch_list = [ord(i) for i in _str]
        for i in ch_list:
            self.write_data(i)
    
    def close(self):
        GPIO.output(self.LCD_D4,0)
        GPIO.output(self.LCD_D5,0)
        GPIO.output(self.LCD_D6,0)
        GPIO.output(self.LCD_D7,0)
        GPIO.output(self.LCD_RS,0)
        GPIO.output(self.LCD_RW,0)
        GPIO.output(self.LCD_E,0)

    def clear(self):
        self.write_command(0x01)
        sleep(self.CMD_CLEAR_DELAY)

    def clear_line_1(self):
        self.move(1,1)
        self.writeStr('                 ')

    def clear_line_2(self):
        self.move(2,1)
        self.writeStr('                 ')

    def printLine1(self, msg):
        self.clear_line_1()
        self.move(1,1)
        self.writeStr(msg)

    def printLine2(self, msg):
        self.clear_line_2()
        slef.move(2,1)
        self.writeStr(msg)

    def the_queue_put(self, msg):
        self.the_queue.put(msg)

    def the_refresh_msg_loop(self):
        while(1):
            self.msg = self.the_queue.get()

    def run(self):
        self.thread = Thread(target = self.the_refresh_msg_loop, args=())
        self.thread.start()
        while(True):
            sleep(0.5)
            self.clear_line_2()
            self.move(2,1)
            
            if(self.msg[0] > (128 + 10)):
                self.write_data(0x03)
            elif(self.msg[0] < (128 - 10)):
                self.write_data(0x02)
            else:
                self.write_data(ord(' '))

            if(self.msg[1] > (128 + 10)):
                self.write_data(0x00)
            elif(self.msg[1] < (128 - 10)):
                self.write_data(0x01)
            else:
                self.write_data(ord(' '))

            if(self.msg[2] > (128 + 10)):
                self.write_data(0x03)
            elif(self.msg[2] < (128 - 10)):
                self.write_data(0x02)
            else:
                self.write_data(ord(' '))

            if(self.msg[3] > (128 + 10)):
                self.write_data(0x00)
            elif(self.msg[3] < (128 - 10)):
                self.write_data(0x01)
            else:
                self.write_data(ord(' '))

    def run_motor_position(self):
        self.thread = Thread(target = self.the_refresh_msg_loop, args=())
        self.thread.start()
        while(True):
            sleep(0.5)
            self.clear_line_1()
            self.clear_line_2()
            self.move(1,1)
            self.writeStr("%4d " % self.msg[0])
            self.writeStr("%4d " % self.msg[1])
            self.writeStr("%4d " % self.msg[2])
            self.move(2,1)
            self.writeStr("%4d " % self.msg[3])
            self.writeStr("%4d " % self.msg[4])
            self.writeStr("%4d " % self.msg[5])
            if(self.debug_mode):
                print self.msg

if __name__ == '__main__':
    mylcd = LCM1602()
    while(1):
        sleep(0.5)
        mylcd.move(2,1)
        mylcd.write_data(0x00)
        mylcd.write_data(0x01)
        mylcd.write_data(0x02)
        mylcd.write_data(0x03)
        mylcd.write_data(0x04)
        mylcd.write_data(0x05)
