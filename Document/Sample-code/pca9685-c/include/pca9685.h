#ifndef __PCA9685_H
#define __PCA9685_H

#include<bcm2835.h>
#include<stdint.h>
#include<sys/time.h>
//#include"libit_i2c.h"
#include<libit_i2c.h>

#define PCA9685_REG_MODE1         0x00
#define PCA9685_REG_MODE2         0x01
#define PCA9685_REG_SUBADR1       0x02
#define PCA9685_REG_SUBADR2       0x03
#define PCA9685_REG_SUBADR3       0x04
#define PCA9685_REG_PRESCALE      0xFE
#define PCA9685_REG_LED0_ON_L     0x06
#define PCA9685_REG_LED0_ON_H     0x07
#define PCA9685_REG_LED0_OFF_L    0x08
#define PCA9685_REG_LED0_OFF_H    0x09
#define PCA9685_REG_ALL_LED_ON_L  0xFA
#define PCA9685_REG_ALL_LED_ON_H  0xFB
#define PCA9685_REG_ALL_LED_OFF_L 0xFC
#define PCA9685_REG_ALL_LED_OFF_H 0xFD
#define PCA9685_PWM_FREQUENCY     50.0

/*
 * FUNCTION DECLARATION PART
 *
 * */

int  pca9685_init         (uint8_t slave_addr, long freq);
void pca9685_reset        (uint8_t slave_addr);
void pca9685_setPWMChannel(uint8_t slave_addr, uint8_t channel, uint16_t on, uint16_t off);
void pca9685_setDutyCycle (uint8_t slave_addr, uint8_t channel, float duty_cycle);
void pca9685_setPrescale  (uint8_t slave_addr, uint8_t pre_scale);
void pca9685_setPWMFreq   (uint8_t slave_addr, long _freq);
void pca9685_wakeup       (uint8_t slave_addr);
void pca9685_sleep        (uint8_t slave_addr);
void pca9685_read_ch      (uint8_t slave_addr, uint8_t ch, uint16_t * _on, uint16_t * _off);

void pca9685_delay_1ms    (long int count);

#endif 
