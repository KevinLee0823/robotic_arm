#!/usr/bin/env python

# Released by rdb under the Unlicense (unlicense.org)
# Based on information from:
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt




## this class of the joystick_usb provide:
## blocking read API (read the event): read_raw()
## non-blocking read API (read the status): read()
## 
## after __init__ of this class, there would be a subprocess running
## for handling the usb joystick
##


import os, struct, array
from fcntl import ioctl
from multiprocessing import Process, Queue, queues
from time import sleep

# Iterate over the joystick devices.
print('Available devices:')


class joystick_usb:
    # We'll store the states here.
    axis_states = {}
    button_states = {}
    axis_map = []
    button_map = []
    cmd=[0,0,0,0,0,0,0,0,0] # [x1,y1,x2,y2,up,down,left,right]

    # These constants were borrowed from linux/input.h
    axis_names = {
        0x00 : 'x',
        0x01 : 'y',
        0x02 : 'z',
        0x03 : 'rx',
        0x04 : 'ry',
        0x05 : 'rz',
        0x06 : 'trottle',
        0x07 : 'rudder',
        0x08 : 'wheel',
        0x09 : 'gas',
        0x0a : 'brake',
        0x10 : 'hat0x',
        0x11 : 'hat0y',
        0x12 : 'hat1x',
        0x13 : 'hat1y',
        0x14 : 'hat2x',
        0x15 : 'hat2y',
        0x16 : 'hat3x',
        0x17 : 'hat3y',
        0x18 : 'pressure',
        0x19 : 'distance',
        0x1a : 'tilt_x',
        0x1b : 'tilt_y',
        0x1c : 'tool_width',
        0x20 : 'volume',
        0x28 : 'misc',
    }
    
    button_names = {
        0x120 : 'trigger',
        0x121 : 'thumb',
        0x122 : 'thumb2',
        0x123 : 'top',
        0x124 : 'top2',
        0x125 : 'pinkie',
        0x126 : 'base',
        0x127 : 'base2',
        0x128 : 'base3',
        0x129 : 'base4',
        0x12a : 'base5',
        0x12b : 'base6',
        0x12f : 'dead',
        0x130 : 'a',
        0x131 : 'b',
        0x132 : 'c',
        0x133 : 'x',
        0x134 : 'y',
        0x135 : 'z',
        0x136 : 'tl',
        0x137 : 'tr',
        0x138 : 'tl2',
        0x139 : 'tr2',
        0x13a : 'select',
        0x13b : 'start',
        0x13c : 'mode',
        0x13d : 'thumbl',
        0x13e : 'thumbr',
    
        0x220 : 'dpad_up',
        0x221 : 'dpad_down',
        0x222 : 'dpad_left',
        0x223 : 'dpad_right',
    
        # XBox 360 controller uses these codes.
        0x2c0 : 'dpad_left',
        0x2c1 : 'dpad_right',
        0x2c2 : 'dpad_up',
        0x2c3 : 'dpad_down',
    }
    

    ## after the init, there would be a subprocess running 
    def __init__(self, filename = "/dev/input/js0"):
        # Open the joystick device.
        self.fn = filename
        self.the_queue = Queue()
        self.process = Process(target=self.run, args=())
        self.process.start()
        
    def run(self):
        self.jsdev = open(self.fn, 'rb')
        print('Opening %s...' % self.fn)

        # Get the device name.
        buf = array.array('c', ['\0'] * 64)
        ioctl(self.jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
        self.js_name = buf.tostring()
        print('Device name: %s' % self.js_name)

        # Get number of axes and buttons.
        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a11, buf) # JSIOCGAXES
        self.num_axes = buf[0]

        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
        self.num_buttons = buf[0]

        # Get the axis map.
        buf = array.array('B', [0] * 0x40)
        ioctl(self.jsdev, 0x80406a32, buf) # JSIOCGAXMAP

        for axis in buf[:self.num_axes]:
            axis_name = self.axis_names.get(axis, 'unknown(0x%02x)' % axis)
            self.axis_map.append(axis_name)
            self.axis_states[axis_name] = 0.0

        # Get the button map.
        buf = array.array('H', [0] * 200)
        ioctl(self.jsdev, 0x80406a34, buf) # JSIOCGBTNMAP
        
        for btn in buf[:self.num_buttons]:
            btn_name = self.button_names.get(btn, 'unknown(0x%03x)' % btn)
            self.button_map.append(btn_name)
            self.button_states[btn_name] = 0

        print '%d axes found: %s' % (self.num_axes, ', '.join(self.axis_map))
        print '%d buttons found: %s' % (self.num_buttons, ', '.join(self.button_map))

        # Main event loop
        while True:
            evbuf = self.jsdev.read(8)
            if evbuf:
                time, value, type, number = struct.unpack('IhBB', evbuf)
        
                if type & 0x80:
                     print "(initial)",
        
                if type & 0x01:
                    button = self.button_map[number]
                    if button:
                        self.button_states[button] = value
                        if value:
                            msg = "%s 1" % button
                            self.the_queue.put(msg)
                        else:
                            msg = "%s 0" % button
                            self.the_queue.put(msg)
        
                if type & 0x02:
                    axis = self.axis_map[number]
                    if axis:
                        fvalue = value / 32767.0
                        self.axis_states[axis] = fvalue
                        msg = "%s %3d" % (axis, value / 256 )
                        self.the_queue.put(msg)

    # the function for main process

    ## non_blocking read the status of the joystick
    ## return the [x1,y1,x2,y2,up_btn,down_btn,left_btn,right_btn,mode_btn]
    def read(self):
        try:
            msg = self.the_queue.get_nowait().split()
            js_ctrl = msg[0]
            js_value = int(msg[1])

            if(js_ctrl == 'x'):
                self.cmd[0] = 128 + js_value 
            elif(js_ctrl == 'y'):
                self.cmd[1] =  128 + js_value * -1
            elif(js_ctrl == 'z'):
                self.cmd[2] =  128 + js_value 
            elif(js_ctrl == 'rz'):
                self.cmd[3] =  128 + js_value * -1

            elif(js_ctrl == 'hat0y'):
                if(js_value < 0 ): # up
                    self.cmd[4] = 1 
                    self.cmd[5] = 0
                elif(js_value > 0 ): # down
                    self.cmd[4] = 0
                    self.cmd[5] = 1
                else : 
                    self.cmd[4] = 0
                    self.cmd[5] = 0

            elif(js_ctrl == 'hat0x'):
                if(js_value < 0 ): # left 
                    self.cmd[6] = 1 
                    self.cmd[7] = 0
                elif(js_value > 0 ): # right 
                    self.cmd[6] = 0
                    self.cmd[7] = 1
                else : 
                    self.cmd[6] = 0
                    self.cmd[7] = 0


            elif(js_ctrl == 'thumb2'):
                self.cmd[8] = js_value

            return self.cmd
        except queues.Empty:
            return self.cmd

    ## block reading 
    ## return event 
    def read_raw(self):
        try:
            msg = self.the_queue.get()
            print msg
        except queues.Empyt:
            print "None"





## test main loop and the using example
##
if __name__ == '__main__':
    joystick = joystick_usb()
    while(1):
        sleep(0.1)
        msg = joystick.read()
        print  msg

