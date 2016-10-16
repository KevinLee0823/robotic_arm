#!/usr/bin/env python

from Mech_arm import Mech_arm
from PCA9685 import PCA9685
from time import sleep

if __name__ == '__main__':
    pca = PCA9685()
    motor_set_dic = {
            "stage": 15,
            "shoulder": 14,
            "elbow": 13,
            "wrist": 12
            }
    arm = Mech_arm(pca, motor_set_dic)
    for i in range(5):
        sleep(0.5)
        arm.moveMotorByDutyCycleRelative('stage', 0.5);
        arm.moveMotorByDutyCycleRelative('shoulder', 0.5);
        arm.moveMotorByDutyCycleRelative('elbow', 0.5);
        arm.moveMotorByDutyCycleRelative('wrist', 0.5);

    for i in range(5):
        sleep(0.5)
        arm.moveMotorByDutyCycleRelative('stage', -0.5);
        arm.moveMotorByDutyCycleRelative('shoulder', -0.5);
        arm.moveMotorByDutyCycleRelative('elbow', -0.5);
        arm.moveMotorByDutyCycleRelative('wrist', -0.5);

    arm.moveMotorHome()
