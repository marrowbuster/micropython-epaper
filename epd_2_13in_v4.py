from . import config

class EPD2in13v4:
    display_width = 250
    display_height = 250
    
    def __init__(self):
        self.rst_pin = config.rst_pin
        self.dc_pin = config.dc_pin
        self.cs_pin = config.cs_pin
        self.busy_pin = config.busy_pin
        self.mosi_pin = config.mosi_pin
        self.sclk_pin = config.sclk_pin
        
    
        
        