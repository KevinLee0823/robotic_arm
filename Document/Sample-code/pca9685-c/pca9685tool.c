#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<stdint.h>
#include<bcm2835.h>
#include"pca9685.h"

#define SLAVE_ADD 0x40

void showRegs();
const char *byte_to_binary(int x);

int main(int argc,char *argv[]){

	bcm2835_init();

	if(argc == 1){
		printf("pca9685 [option] \n\n");
		printf("[option]: \n");
		printf("	dcyc         : set duty cycle (0~100) of channel\n");
		printf("	init         : reset the pca9685\n");
		printf("	setCh        : set the on (0~4095) and off (0~4095) of channel\n");
		printf("	setPWMFreq   : set the PWM repeat frequency (Hz) , default value : 50 Hz\n");
		printf("	showRegs     : show all reg data in the pca9685 chip\n");
		printf("	readCh       : read on and off value in channel\n");
		return 0;
	}

	if(strcmp(argv[1], "reset") == 0) {
		pca9685_reset(SLAVE_ADD);
		return 0;
	}

	if(strcmp(argv[1], "dcyc") == 0) {
		if(argc == 4){
			int ch = atoi(argv[2]);
			float dcyc = atof(argv[3]);
			pca9685_setDutyCycle(SLAVE_ADD, ch, dcyc);
			return 0;
		}
		printf("pca9685tool dcyc [channel] [duty cycle]\n");
		return 0;
	}

	if(strcmp(argv[1], "init") == 0) {
		pca9685_init(SLAVE_ADD,50 );
		return 0;
	}

	if(strcmp(argv[1], "setCh") == 0) {
		if(argc == 5){
			int ch = atoi(argv[2]);
			long on = atol(argv[3]);
			long off = atol(argv[4]);
			pca9685_setPWMChannel(SLAVE_ADD, ch, on, off);
		}
		else{
			printf("pca9685tool setCh [channel] [on] [off]\n");
		}
		return 0;
	}

	if(strcmp(argv[1], "setPWMFreq") == 0) {
		if(argc==3)
		{
			long _freq = atol(argv[2]);
			pca9685_setPWMFreq(SLAVE_ADD, _freq);
		}else
		{
			printf("set up the repeat frequency (Hz) of PWM\n");
			printf("pca9685tool setPWMFreq [Frequency]\n");
		}
	}

	if(strcmp(argv[1], "showRegs") == 0) {
		showRegs();
	}

	if(strcmp(argv[1], "readCh") == 0) {
		if(argc == 3){
			int ch = atoi(argv[2]);
			//PCA9685ch ch_data;
			//pca9685_read_ch(SLAVE_ADD, ch, &ch_data);
			uint16_t _on, _off;
			pca9685_read_ch(SLAVE_ADD, ch, &_on, &_off);
			printf("ch:%d\ton:%ld\toff:%ld\n", ch, _on, _off);
		}else{
			printf("show the data in the channel\n");
			printf("pca9685tool readCh [channel]\n");
		}
	}

	return 0;
}

const char *byte_to_binary(int x)
{
	static char b[9];
	b[0] = '\0';
	int z;
	for (z = 128; z > 0; z >>= 1){
		strcat(b, ((x & z) == z) ? "1" : "0");
	}
	return b;
}

void showRegs(){
	int i = 0;
	for(i  = 0;i< 70 ;i++ ){
		uint8_t data = i2c_read_reg_byte(SLAVE_ADD, i);
		printf("Reg %03d : %s \n",i, byte_to_binary(data));
	}

	for(i  = 250 ; i <= 255 ;i++ ){
		uint8_t data = i2c_read_reg_byte(SLAVE_ADD, i);
		printf("Reg %03d : %s \n",i, byte_to_binary(data));
	}
}
