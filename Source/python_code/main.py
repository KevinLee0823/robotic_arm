#!/usr/bin/env python

from multiprocessing import Process, Queue
from time import sleep
import signal, os

from PCA9685 import PCA9685
from Joystick_usb import joystick_usb
from Arm import Arm
from LCM import LCM1602


pwm = ''
system_stop = False


###################################
# signal handler 
###################################
def sigint_handler(signum, frame):
    system_stop = True
    signal.signal(signal.SIGINT, )






##################################
# main program START
##################################
if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)

    #########################
    # START PCA9685 module
    #########################
    pwm = PCA9685()
    pwm.reset()
    pwm.wakeup()


    #########################
    # setup the mech arm pwm channel
    #########################
    motor_set_dic = {
            "stage": 15,
            "shoulder": 14,
            "elbow": 13,
            "wrist": 12,
            "wrist_twist" : 11,
            "finger": 10,
            }
    arm = Arm(pwm, motor_set_dic)


    #########################
    # setup the Joystick
    #########################

    joystick = joystick_usb()

    ###########################
    # setup the LCM module
    # print the motor position
    ###########################

    mylcd = LCM1602(debug_mode = False)

    #########################
    # START Loop
    #########################

    while(not system_stop):
        msg = []
        motor_pos = []
        # this delay time control the response time of the arm
        sleep(0.02)
        if(arm.control_mode == 0):
            msg = arm.moveByJoystickPS2_mode0(joystick.read())
        elif(arm.control_mode == 1):
            msg = arm.moveByJoystickPS2_mode1(joystick.read())

        # send motor position information to LCM module
        for i in range(6):
            motor_pos.append(arm.pwm.getValChOff(15-i))
        mylcd.the_queue.put(motor_pos)


    ######################################
    # when system stop after accept ctrl+c
    ######################################

    joystick.close()


