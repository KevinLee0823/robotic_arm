#ifndef __LIB_SERVO_H
#define __LIB_SERVO_H

//#include"pca9685.h"
#include<pca9685.h>

struct Servo {
	uint8_t slave_addr;
	uint8_t channel;
	float   th_max;
	float   th_min;
	float   dcyc_th_zero;
	float   ration;
};

void servo_init(struct Servo * _servo, uint8_t sl_addr, uint8_t _ch, float th_max, float th_min, float _dcyc_0, float _rat);
int servo_read_th(struct Servo * _servo, float * th);

#endif 
