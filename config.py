import machine
import utime
import sys

from uctypes import *

class RP2040PiZero:
    
    pins = {'rst_pin': 17
            'dc_pin': 25
            'cs_pin': 8
            'busy_pin': 24
            'mosi_pin': 10
            'sclk_pin': 11}
    
    def __init__(self):
        from machine import SPI, Pin
        # GPIO10 and GPIO11 have an alternate function for SPI1
        self.spi_device = SPI(1,
                              baudrate = int(4e6), # lazy af
                              polarity = 1,
                              phase = 1,
                              bits = 8,
                              firstbit = SPI.MSB,
                              sck = Pin(pins['sclk_pin']),
                              mosi = Pin(pins['mosi_pin']))
        self.gpio_busy_pin = Pin(pins['busy_pin'],
                                 mode = Pin.IN,
                                 pull = Pin.PULL_UP)
        self.gpio_dc_pin = Pin(dc_pin,
                               mode = Pin.OUT)
        self.gpio_cs_pin = Pin(cs_pin,
                               mode = Pin.OUT,
                               value = Pin.HIGH);
        self.gpio_dc_pin = Pin(dc_pin,
                               mode = Pin.OUT);
    
    def spi_write(self, data):
        self.spi_device.write(data)
        
    def spi_read(self, num_bytes):
        return self.spi_device.read(num_bytes)
    
    def select_chip(self):
        # cs is active high, must lower the signal to select it
        # only for rp2040/2350, may not work on other microcontrollers
        self.gpio_cs_pin.low()
        
    def deselect_chip(self):
        self.gpio_cs_pin.high()
    
    