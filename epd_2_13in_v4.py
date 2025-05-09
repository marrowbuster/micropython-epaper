import config

class EPD2in13v4:
    display_width = 250
    display_height = 122
    
    pins = {}
    
    def __init__(self):
        self.pins['rst_pin'] = config.pins['rst_pin']
        self.pins['dc_pin'] = config.pins['dc_pin']
        self.pins['cs_pin'] = config.pins['cs_pin']
        self.pins['busy_pin'] = config.pins['busy_pin']
        self.pins['mosi_pin'] = config.pins['mosi_pin']
        self.pins['sclk_pin'] = config.pins['sclk_pin']

    def reset(self):
        self.pins['rst_pin'].high()
        config.delay_ms(20)
        self.pins['rst_pin'].low()
        config.delay_ms(2)
        self.pins['rst_pin'].high()
        config.delay_ms(20)