#include<stdio.h>
#include<stdlib.h>
#include"pca9685.h"

#define SLAVE_ADDR 0x40

int main(int argc,char *argv[]){
	// initialize the bcm2835 
	bcm2835_init();

	// initialize the pca9685 and set the PWM frequency as 50 Hz
	pca9685_init(SLAVE_ADDR, 50);

	// set the duty cycle 10% of channel 0
	pca9685_setDutyCycle(SLAVE_ADDR, 0 , 10);


	return 0;
}


