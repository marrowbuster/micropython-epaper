import machine
import time
import sys

from uctypes import *

pins = {'rst_pin': 17,
        'dc_pin': 25,
        'cs_pin': 8,
        'busy_pin': 24,
        'mosi_pin': 11,
        'sclk_pin': 10}

class RP2040PiZero:
    
    input_pins = {}
    output_pins = {}
    
    
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
                              mosi = Pin(pins['mosi_pin']),
                              miso = None)
        
        for pin in ['dc_pin', 'rst_pin']:
            self.output_pins[pins[pin]] = Pin(pins[pin],
                                                mode = Pin.OUT)
            
        # cs is active high, must lower the signal to select it
        # only for rp2040/2350, may not work on other microcontrollers
        self.output_pins[pins['cs_pin']] = Pin(pins['cs_pin'],
                                                 mode = Pin.OUT,
                                                 value = 1)
        
        # original waveshare code had this configured as a button, internal
        # pull-up resistor required.
        self.input_pins[pins['busy_pin']] = Pin(pins['busy_pin'],
                                                  mode = Pin.IN,
                                                  pull = Pin.PULL_UP)
    
    def spi_write(self, data):
        self.spi_device.write(data)
        
    def spi_read(self, num_bytes):
        return self.spi_device.read(num_bytes)
    
    def spi_write_readinto(self, write_data, read_data):
        if len(write_data) != len(read_data):
            raise ValueError('write and read buffers must be of the same length')
        self.spi_device.write_readinto(write_data, read_data)
    
    def select_chip(self):
        # as previously mentioned, cs is active high, must lower the signal to
        # select it only for rp2040/2350, may not work on other microcontrollers
        self.output_pins[pins['cs_pin']].low()
        
    def deselect_chip(self):
        self.output_pins[pins['cs_pin']].high()
    
    # should probably add functionality to use either pin name or number
    def digital_write(self, pin, level):
        if level not in range(0, 2):
            raise ValueError('level must be either 0 or 1')
        if pin in self.output_pins:
            self.output_pins[pins[pin]].value(level)
        else:
            raise ValueError(f'pin {pin} isn\'t configured as an output')

    def digital_read(self, pin):
        if pin in self.input_pins:
            return self.input_pins[pin].value()
        else:
            raise ValueError(f'pin {pin} isn\'t configured as an input')
        
    def delay_ms(self, ms):
        time.sleep(ms / 1000.0)

    def data_mode(self):
        self.digital_write(pins['dc_pin'], 1)

    def command_mode(self):
        self.digital_write(pins['dc_pin'], 0)

    def deinit(self):
        self.spi_device.deinit()

    

instance = RP2040PiZero()
for f in [d for d in dir(instance) if not d.startswith('_')]:
    setattr(sys.modules[__name__], f, getattr(instance, f))
    
    