#include<lib_servo.h>


void servo_init(struct Servo * _servo, uint8_t sl_addr, uint8_t _ch, float th_max, float th_min, float _dcyc_0, float _rat )
{
	_servo->slave_addr = sl_addr;
	_servo->channel = _ch;
	_servo->th_max = th_max;
	_servo->th_min = th_min;
	_servo->dcyc_th_zero = _dcyc_0;
	_servo->ration = _rat;
}


// input : _servo
// output: th
// return: 0 == ok, other not ok
int servo_read_th(struct Servo * _servo, float * th)
{
	uint16_t _on;
	uint16_t _off;
	pca9685_read_ch(_servo->slave_addr, _servo->channel, &_on, &_off );
	*th = ( (float)(_off - _on) / 4096.0 - _servo->dcyc_th_zero ) / _servo->ration;
	return 0;
}
