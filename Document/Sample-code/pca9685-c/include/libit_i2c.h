#ifndef __LIBIT_I2C_H
#define __LIBIT_I2C_H

#include<bcm2835.h>
#include<stdint.h>

uint8_t i2c_init();
uint8_t i2c_read_reg_byte (uint8_t slave_addr, uint8_t reg);
void    i2c_write_reg_byte(uint8_t slave_addr, uint8_t reg, uint8_t data);
void    i2c_end();

#endif
