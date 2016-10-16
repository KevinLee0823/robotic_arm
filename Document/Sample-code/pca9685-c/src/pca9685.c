#include<pca9685.h>
#include<stdio.h>
#include<stdlib.h>

/*
 * FUNCTION IMPLEMENT PART
 *
 * */

int pca9685_init(uint8_t slave_addr, long freq){
	int res = i2c_init();
	pca9685_reset(slave_addr);
	pca9685_setPWMFreq(slave_addr, freq);
	return res;
}

void pca9685_setPWMChannel(uint8_t slave_addr,uint8_t channel, uint16_t on, uint16_t off){
	uint8_t on_byte_low   = on & 0x00ff;
	uint8_t on_byte_high  = on >> 8;
	uint8_t off_byte_low  = off & 0x00ff;
	uint8_t off_byte_high = off >> 8;

	uint8_t on_reg_low  = channel * 4 + PCA9685_REG_LED0_ON_L;
	uint8_t on_reg_high = channel * 4 + PCA9685_REG_LED0_ON_H;

	uint8_t off_reg_low  = channel * 4 + PCA9685_REG_LED0_OFF_L;
	uint8_t off_reg_high = channel * 4 + PCA9685_REG_LED0_OFF_H;

	i2c_write_reg_byte(slave_addr, on_reg_low, on_byte_low);
	i2c_write_reg_byte(slave_addr, on_reg_high, on_byte_high);

	i2c_write_reg_byte(slave_addr, off_reg_low, off_byte_low);
	i2c_write_reg_byte(slave_addr, off_reg_high, off_byte_high);
}

void pca9685_setDutyCycle(uint8_t slave_addr,uint8_t channel, float duty_cycle){
	uint16_t count = 4096.0 / 100.0 * duty_cycle;
	//printf("count:%ld\n",count);
	pca9685_setPWMChannel(slave_addr, channel, 0, count );
}

void pca9685_setPrescale(uint8_t slave_addr, uint8_t pre_scale){
	uint8_t now_pre_scale = i2c_read_reg_byte(slave_addr, PCA9685_REG_PRESCALE);
	if(now_pre_scale != pre_scale){

		uint8_t oldmode1 = i2c_read_reg_byte(slave_addr, PCA9685_REG_MODE1);
		uint8_t newmode1 = oldmode1 | (1<<4); // mode to sleep

		i2c_write_reg_byte(slave_addr, PCA9685_REG_MODE1, newmode1) ; // sleep
		i2c_write_reg_byte(slave_addr, PCA9685_REG_PRESCALE, pre_scale) ; // set prescale
		i2c_write_reg_byte(slave_addr, PCA9685_REG_MODE1, oldmode1) ; // recover the old mode
		pca9685_delay_1ms(5);
		i2c_write_reg_byte(slave_addr, PCA9685_REG_MODE1, oldmode1 | 0x80) ; // restart
	}
}

// input 
void pca9685_setPWMFreq(uint8_t slave_addr, long _freq){
	uint8_t prescale = ( 25.e6/ 4096. / _freq - 1) ;
	pca9685_setPrescale(slave_addr, prescale);
}

void pca9685_reset(uint8_t slave_addr){
	i2c_write_reg_byte(slave_addr, PCA9685_REG_ALL_LED_ON_L, 0 );
	i2c_write_reg_byte(slave_addr, PCA9685_REG_ALL_LED_ON_H, 0 );
	i2c_write_reg_byte(slave_addr, PCA9685_REG_ALL_LED_OFF_L, 0 );
	i2c_write_reg_byte(slave_addr, PCA9685_REG_ALL_LED_OFF_H, 0 );
	i2c_write_reg_byte(slave_addr, PCA9685_REG_MODE2, 0x04 );
	i2c_write_reg_byte(slave_addr, PCA9685_REG_MODE1, 0x01 );
	pca9685_delay_1ms(5);
}

void pca9685_delay_1ms(long int count){
	struct timeval start;
	struct timeval now;
	long int diff_us = 0;
	count *= 1000;

	gettimeofday(&start,NULL);
	while(diff_us <= count){
		gettimeofday(&now,NULL);
		diff_us = 1000000 * (now.tv_sec - start.tv_sec) - (now.tv_usec - now.tv_usec);
	}
}

void pca9685_wakeup(uint8_t slave_addr){
	uint8_t oldmode1 = i2c_read_reg_byte(slave_addr, PCA9685_REG_MODE1);
	uint8_t newmode1 = oldmode1 &~ (1<<4) ;
	i2c_write_reg_byte(slave_addr, PCA9685_REG_MODE1, newmode1);
}

void pca9685_sleep(uint8_t slave_addr){
	uint8_t oldmode1 = i2c_read_reg_byte(slave_addr, PCA9685_REG_MODE1);
	uint8_t newmode1 = oldmode1 | (1<<4) ;
	i2c_write_reg_byte(slave_addr, PCA9685_REG_MODE1, newmode1);
}

void pca9685_read_ch(uint8_t slave_addr, uint8_t ch, uint16_t * _on, uint16_t * _off){
	uint8_t _reg = 0;
	uint16_t data = 0;

	// read the ON of the channel
	_reg = PCA9685_REG_LED0_ON_L + ch * 4;
	data += i2c_read_reg_byte(slave_addr, _reg);
	_reg = PCA9685_REG_LED0_ON_H + ch * 4;
	data +=  i2c_read_reg_byte(slave_addr, _reg) << 8;
	//chbuf->on = data;
	*_on = data;
	

	// read the OFF of the channel
	data = 0;
	_reg = PCA9685_REG_LED0_OFF_L + ch * 4;
	data += i2c_read_reg_byte(slave_addr, _reg);
	_reg = PCA9685_REG_LED0_OFF_H + ch * 4;
	data +=  i2c_read_reg_byte(slave_addr, _reg) << 8;
	//chbuf->off = data;
	*_off = data;
}
