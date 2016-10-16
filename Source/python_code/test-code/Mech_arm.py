#!/usr/bin/env python

from PCA9685 import PCA9685
from time import sleep


class Mech_arm:
    stage_limit_up    = 12.5
    shoulder_limit_up = 12.5
    elbow_limit_up    = 12.5
    wrist_limit_up    = 12.5

    stage_limit_down    = 3.5
    shoulder_limit_down = 3.5
    elbow_limit_down    = 3.5
    wrist_limit_down    = 6.5

    def __init__(self, pca, motor_set_dic):
        self.pca = pca
        for key in motor_set_dic:
            self.setMotorChannel(key, motor_set_dic[key])
        self.moveMotorHome()

    def setMotorChannel(self, motor ,channel):
        if (channel < 0) or (channel > 15) :
            return 

        if(motor == 'stage'):
            self.stage_ch = channel
        elif(motor == 'shoulder'):
            self.shoulder_ch = channel
        elif(motor == 'elbow'):
            self.elbow_ch = channel
        elif(motor == 'wrist'):
            self.wrist_ch = channel

    def getMotorChannel(self, motor):
        if(motor == 'stage'):
            return self.stage_ch 
        elif(motor == 'shoulder'):
            return self.shoulder_ch ;
        elif(motor == 'elbow'):
            return self.elbow_ch 
        elif(motor == 'wrist'):
            return self.wrist_ch 
        else:
            return -1

    def moveMotorByDutyCycle(self, motor, duty_cycle):
        if(motor == 'stage'):
            if((duty_cycle > self.stage_limit_up) or (duty_cycle < self.stage_limit_down)):
                return 
            else :
                self.pca.chDuty(self.stage_ch, duty_cycle)

        elif(motor == 'shoulder'):
            if((duty_cycle > self.shoulder_limit_up) or (duty_cycle < self.shoulder_limit_down)):
                return 
            else :
                self.pca.chDuty(self.shoulder_ch, duty_cycle)

        elif(motor == 'elbow'):
            if((duty_cycle > self.elbow_limit_up) or (duty_cycle < self.elbow_limit_down)):
                return 
            else :
                self.pca.chDuty(self.elbow_ch, duty_cycle)

        elif(motor == 'wrist'):
            if((duty_cycle > self.wrist_limit_up) or (duty_cycle < self.wrist_limit_down)):
                return 
            else :
                self.pca.chDuty(self.wrist_ch, duty_cycle)

    def moveMotorByDutyCycleRelative(self, motor, duty_cycle):
        if(motor == 'stage'):
            duty_cycle += self.pca.getChDuty(self.stage_ch) 
            if(  (duty_cycle < self.stage_limit_down ) or (duty_cycle > self.stage_limit_up) ):
                return 
            else:
                self.pca.chDuty(self.stage_ch, duty_cycle)

        elif(motor == 'shoulder'):
            duty_cycle += self.pca.getChDuty(self.shoulder_ch) 
            if(  (duty_cycle < self.shoulder_limit_down ) or (duty_cycle > self.shoulder_limit_up) ):
                return 
            else:
                self.pca.chDuty(self.shoulder_ch, duty_cycle)

        elif(motor == 'elbow'):
            duty_cycle += self.pca.getChDuty(self.elbow_ch) 
            if(  (duty_cycle < self.elbow_limit_down ) or (duty_cycle > self.elbow_limit_up) ):
                return 
            else:
                self.pca.chDuty(self.elbow_ch, duty_cycle)

        elif(motor == 'wrist'):
            duty_cycle += self.pca.getChDuty(self.wrist_ch) 
            if(  (duty_cycle < self.wrist_limit_down ) or (duty_cycle > self.wrist_limit_up) ):
                return 
            else:
                self.pca.chDuty(self.wrist_ch, duty_cycle)

    def moveMotorHome(self):
        self.moveMotorByDutyCycle('stage',7.5);
        self.moveMotorByDutyCycle('shoulder',3.5);
        self.moveMotorByDutyCycle('elbow',12.5);
        self.moveMotorByDutyCycle('wrist',7.5);

if __name__ == '__main__':
    pca = PCA9685()
    pca.reset()
    pca.wakeup()
    motor_set_dic = {
            "stage": 15,
            "shoulder": 14,
            "elbow": 13,
            "wrist": 12
            }
    arm = Mech_arm(pca, motor_set_dic)

