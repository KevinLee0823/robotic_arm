#!/usr/bin/env python

from PCA9685 import PCA9685
from Joystick import Joystick
from JoystickPS2_uart import JoystickPS2_uart
from LCM import LCM1602
from time import sleep
import signal, os

pca = ''
system_stop = False


class Arm:
    stage_limit_up    = 12.5
    shoulder_limit_up = 12.5
    elbow_limit_up    = 12.5
    wrist_limit_up    = 12.5
    wrist_tw_limit_up = 12.5
    finger_limit_up   = 7.0

    stage_limit_down    = 3.5
    shoulder_limit_down = 3.5
    elbow_limit_down    = 3.5
    wrist_limit_down    = 6.5
    wrist_tw_limit_down = 3.5
    finger_limit_down   = 3.5

    control_mode = 0
    pre_mode_btn = 0
    pre_run_script_btn = 0

    def __init__(self, pwm, motor_set_dic):
        self.pwm = pwm
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
        elif(motor == 'wrist_twist'):
            self.wrist_tw_ch = channel
        elif(motor == 'finger'):
            self.finger_ch = channel


    def getMotorChannel(self, motor):
        if(motor == 'stage'):
            return self.stage_ch 
        elif(motor == 'shoulder'):
            return self.shoulder_ch ;
        elif(motor == 'elbow'):
            return self.elbow_ch 
        elif(motor == 'wrist'):
            return self.wrist_ch 
        elif(motor == 'wrist_twist'):
            return self.wrist_tw_ch
        elif(motor == 'finger'):
            return self.finger_ch
        else:
            return -1

    def moveMotorByDutyCycle(self, motor, duty_cycle):
        if(motor == 'stage'):
            if((duty_cycle > self.stage_limit_up) or (duty_cycle < self.stage_limit_down)):
                return 
            else :
                self.pwm.chDuty(self.stage_ch, duty_cycle)

        elif(motor == 'shoulder'):
            if((duty_cycle > self.shoulder_limit_up) or (duty_cycle < self.shoulder_limit_down)):
                return 
            else :
                self.pwm.chDuty(self.shoulder_ch, duty_cycle)

        elif(motor == 'elbow'):
            if((duty_cycle > self.elbow_limit_up) or (duty_cycle < self.elbow_limit_down)):
                return 
            else :
                self.pwm.chDuty(self.elbow_ch, duty_cycle)

        elif(motor == 'wrist'):
            if((duty_cycle > self.wrist_limit_up) or (duty_cycle < self.wrist_limit_down)):
                return 
            else :
                self.pwm.chDuty(self.wrist_ch, duty_cycle)

        elif(motor == 'wrist_twist'):
            if((duty_cycle > self.wrist_tw_limit_up) or (duty_cycle < self.wrist_tw_limit_down)):
                return 
            else :
                self.pwm.chDuty(self.wrist_tw_ch, duty_cycle)

        elif(motor == 'finger'):
            if((duty_cycle > self.finger_limit_up) or (duty_cycle < self.finger_limit_down)):
                return 
            else :
                self.pwm.chDuty(self.finger_ch, duty_cycle)


    def moveMotorByDutyCycleRelative(self, motor, duty_cycle):
        if(motor == 'stage'):
            duty_cycle += self.pwm.getChDuty(self.stage_ch) 
            if(  (duty_cycle < self.stage_limit_down ) or (duty_cycle > self.stage_limit_up) ):
                return 
            else:
                self.pwm.chDuty(self.stage_ch, duty_cycle)

        elif(motor == 'shoulder'):
            duty_cycle += self.pwm.getChDuty(self.shoulder_ch) 
            if(  (duty_cycle < self.shoulder_limit_down ) or (duty_cycle > self.shoulder_limit_up) ):
                return 
            else:
                self.pwm.chDuty(self.shoulder_ch, duty_cycle)

        elif(motor == 'elbow'):
            duty_cycle += self.pwm.getChDuty(self.elbow_ch) 
            if(  (duty_cycle < self.elbow_limit_down ) or (duty_cycle > self.elbow_limit_up) ):
                return 
            else:
                self.pwm.chDuty(self.elbow_ch, duty_cycle)

        elif(motor == 'wrist'):
            duty_cycle += self.pwm.getChDuty(self.wrist_ch) 
            if(  (duty_cycle < self.wrist_limit_down ) or (duty_cycle > self.wrist_limit_up) ):
                return 
            else:
                self.pwm.chDuty(self.wrist_ch, duty_cycle)

        elif(motor == 'wrist_twist'):
            duty_cycle += self.pwm.getChDuty(self.wrist_tw_ch) 
            if(  (duty_cycle < self.wrist_tw_limit_down ) or (duty_cycle > self.wrist_tw_limit_up) ):
                return 
            else:
                self.pwm.chDuty(self.wrist_tw_ch, duty_cycle)

        elif(motor == 'finger'):
            duty_cycle += self.pwm.getChDuty(self.finger_ch) 
            if(  (duty_cycle < self.finger_limit_down ) or (duty_cycle > self.finger_limit_up) ):
                return 
            else:
                self.pwm.chDuty(self.finger_ch, duty_cycle)


    def moveMotorHome(self):
        self.moveMotorByDutyCycle('stage',7.5);
        self.moveMotorByDutyCycle('shoulder',3.5);
        self.moveMotorByDutyCycle('elbow',12.5);
        self.moveMotorByDutyCycle('wrist',10.5);
        self.moveMotorByDutyCycle('wrist_twist',7.5);
        self.moveMotorByDutyCycle('finger',4);
    

    ## mode default
    ## Stage          motor move depending on x1
    ## Shoulder       motor move depending on y1
    ## Wrist_twist    motor move depending on x2
    ## Elbow & Wrist  motor move depending on y2
    ##
    ## onionys, 2015-04-01 : 
    ##              add the run script button function
    ##              it's real, not an April fool joke.
    ## 
    def moveByJoystickPS2_mode0(self, joystick_pos):
        try:
            x1 = joystick_pos[0]
            y1 = joystick_pos[1]
            x2 = joystick_pos[2]
            y2 = joystick_pos[3]
            up_btn = joystick_pos[4]
            down_btn = joystick_pos[5]
            left_btn = joystick_pos[6]
            right_btn = joystick_pos[7]
            mode_btn = joystick_pos[8]

            # Stage Motor
            if(x1 > (128 + 10) ):
                self.moveMotorByDutyCycleRelative('stage', -0.1)
            elif(x1 < (128 - 10) ):
                self.moveMotorByDutyCycleRelative('stage',0.1)

            # Shoulder Motor
            if(y1 > (128 + 10) ):
                self.moveMotorByDutyCycleRelative('shoulder',0.1)
            elif(y1 < (128 - 10) ):
                self.moveMotorByDutyCycleRelative('shoulder', -0.1)

            # Elbow & Wrist Motor

            if(x2 > (128 + 10) ):
                self.moveMotorByDutyCycleRelative('wrist_twist', -0.1)
            elif(x2 < (128 - 10) ):
                self.moveMotorByDutyCycleRelative('wrist_twist', 0.1)

            if(y2 > (128 + 10) ):
                self.moveMotorByDutyCycleRelative('elbow',0.1)
                self.moveMotorByDutyCycleRelative('wrist',0.1)
            elif(y2 < (128 - 10) ):
                self.moveMotorByDutyCycleRelative('elbow', -0.1)
                self.moveMotorByDutyCycleRelative('wrist', -0.1)

            # Finger Motor
            if( left_btn ):
                self.moveMotorByDutyCycleRelative('finger', 0.1)
            elif( right_btn ):
                self.moveMotorByDutyCycleRelative('finger', -0.1)

            # change mode
            if( (mode_btn == 1) and (self.pre_mode_btn == 0)):
                print 'change mode to 1'
                self.control_mode = 1
            self.pre_mode_btn = mode_btn

            # run script 
            if( (up_btn == 1) and (self.pre_run_script_btn == 0)):
                print 'run script'
                self.run_script()
            self.pre_run_script_btn = up_btn

            return joystick_pos

        except:
            pass


    ## mode: lock the shoulder
    ##       elbow motor move depending on y1
    ##       write motor move depending on y2
    ##       nothing change else.
    def moveByJoystickPS2_mode1(self,joystick_pos):
        try:
            x1 = joystick_pos[0]
            y1 = joystick_pos[1]
            x2 = joystick_pos[2]
            y2 = joystick_pos[3]
            up_btn = joystick_pos[4]
            down_btn = joystick_pos[5]
            left_btn = joystick_pos[6]
            right_btn = joystick_pos[7]
            mode_btn = joystick_pos[8]

            # Stage Motor
            if(x1 > (128 + 10) ):
                self.moveMotorByDutyCycleRelative('stage', -0.1)
            elif(x1 < (128 - 10) ):
                self.moveMotorByDutyCycleRelative('stage',0.1)

            # Shoulder Motor locked

            # Elbow Motor
            if(y1 > (128 + 10) ):
                self.moveMotorByDutyCycleRelative('elbow',0.1)
            elif(y1 < (128 - 10) ):
                self.moveMotorByDutyCycleRelative('elbow', -0.1)


            # Wrist Motor
            if(x2 > (128 + 10) ):
                self.moveMotorByDutyCycleRelative('wrist_twist', -0.1)
            elif(x2 < (128 - 10) ):
                self.moveMotorByDutyCycleRelative('wrist_twist', 0.1)

            if(y2 > (128 + 10) ):
                self.moveMotorByDutyCycleRelative('wrist',0.1)
            elif(y2 < (128 - 10) ):
                self.moveMotorByDutyCycleRelative('wrist', -0.1)

            # Finger Motor
            if(  left_btn == 1  ):
                self.moveMotorByDutyCycleRelative('finger', 0.1)
            elif( right_btn == 1):
                self.moveMotorByDutyCycleRelative('finger', -0.1)

            # change mode
            if( (mode_btn == 1) and (self.pre_mode_btn == 0)):
                print 'change mode to 0'
                self.control_mode = 0
            self.pre_mode_btn = mode_btn

            # run script 
            if( (up_btn == 1) and (self.pre_run_script_btn == 0)):
                print 'run script'
                self.run_script()
            self.pre_run_script_btn = up_btn
            return joystick_pos
        except:
            pass

    ## Script List Definition:
    ## [
    ##  [stage],
    ## ]
    ## 
    def run_script(self):
        script_ = [
                [387,164,510,511,145,146,1],
                [387,164,380,487,373,146,1],
                [387,208,389,493,373,146,1],
                [387,275,371,463,373,146,2],
                [387,275,371,463,373,238,1],
                [382,147,371,463,373,238,1],
                [382,147,463,463,373,238,1],
                [171,147,463,463,373,238,1],
                [171,159,496,496,373,238,1],
                [171,223,449,451,365,238,2],
                [171,223,449,451,365,180,1],
                [171,223,449,451,365,165,1],
                [171,223,449,451,365,146,1],
                [171,144,391,391,373,143,1],
                ]
        for i in script_:
            cmd_dic = {}
            cmd_dic[15] = i[0]
            cmd_dic[14] = i[1]
            cmd_dic[13] = i[2]
            cmd_dic[12] = i[3]
            cmd_dic[11] = i[4]
            cmd_dic[10] = i[5]
            self.pwm.setByCountDic(cmd_dic)
            sleep(i[6])

    def run_script_file(self,filename):
        script_ = []
        try:
            with open(filename,'r') as _line:
                script_.append( [int(i) for i in _line.split()] )

        #script_ = [
        #        [387,164,510,511,145,146,1],
        #        [387,164,380,487,373,146,1],
        #        [387,208,389,493,373,146,1],
        #        [387,275,371,463,373,146,2],
        #        [387,275,371,463,373,238,1],
        #        [382,147,371,463,373,238,1],
        #        [382,147,463,463,373,238,1],
        #        [171,147,463,463,373,238,1],
        #        [171,159,496,496,373,238,1],
        #        [171,223,449,451,365,238,2],
        #        [171,223,449,451,365,180,1],
        #        [171,223,449,451,365,165,1],
        #        [171,223,449,451,365,146,1],
        #        [171,144,391,391,373,143,1],
        #        ]
            for i in script_:
                cmd_dic = {}
                cmd_dic[15] = i[0]
                cmd_dic[14] = i[1]
                cmd_dic[13] = i[2]
                cmd_dic[12] = i[3]
                cmd_dic[11] = i[4]
                cmd_dic[10] = i[5]
                self.pwm.setByCountDic(cmd_dic)
                sleep(i[6])
        except:
            print "ERROR: load script %s failed." % filename
            return

def sigint_handler(signum, frame):
    system_stop = True
    signal.signal(signal.SIGINT, )


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)

    #########################
    # START LCD module
    #########################
    lcd = LCM1602()
    lcd.init()
    lcd.move(1,1)
    lcd.writeStr("START")


    #########################
    # START PCA9685 module
    #########################
    pca = PCA9685()
    pca.reset()
    pca.wakeup()


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
    arm = Arm(pca, motor_set_dic)


    #########################
    # setup the Joystick
    #########################

    #joystick = Joystick()
    joystick_ps2 = JoystickPS2_uart()
    arm.setJoystick(joystick_ps2)


    #########################
    # START Loop
    #########################

    while(not system_stop):
        if(arm.control_mode == 0):
            arm.moveByJoystickPS2_mode0()
        elif(arm.control_mode == 1):
            arm.moveByJoystickPS2_mode1()

    ## when system stop
    joystick.close()


