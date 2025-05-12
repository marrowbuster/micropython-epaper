# this assumes the config module has already been uploaded to the board's internal storage
import config

commands = {0x01, 0x03, 0x04, 0x08, 0x09, 0x0a, 0x0c, 0x10, 0x11, 0x12, 0x14, 0x15,
            0x18, 0x1a, 0x1b, 0x1c, 0x20, 0x21, 0x22, 0x24, 0x26, 0x27, 0x28, 0x29,
            0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x32, 0x34, 0x35, 0x36,
            0x37, 0x38, 0x39, 0x3c, 0x3f, 0x41, 0x44, 0x45, 0x46, 0x47, 0x4e, 0x4f,
            0x7f}

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
        # reset is active low
        config.digital_write(self.pins['rst_pin'], 1)
        config.delay_ms(20)
        config.digital_write(self.pins['rst_pin'], 0)
        config.delay_ms(2)
        config.digital_write(self.pins['rst_pin'], 1)
        config.delay_ms(20)
    
    def is_valid_command(self, command):
        if not isinstance(command, int):
            raise ValueError(f"command must be of type int, got {type(command)}")
        if command not in commands:
            raise ValueError("invalid command specified")
        return command
    
    def send_command(self, command):
        try:
            cmd = self.is_valid_command(command)
            # d/c means data/command, pull high for data, pull low for command
            config.command_mode()
            config.select_chip()
            config.spi_write([cmd])
            config.deselect_chip()
        except ValueError as e:
            print(f'command send error: {e}')

    def send_data(self, data):
        # d/c means data/command, pull high for data, pull low for command
        config.data_mode()
        config.select_chip()
        config.spi_write([data])
        config.deselect_chip()

    def busy(self):
        while config.digital_read(self.pins['busy_pin']):
            config.delay_ms(10)

    def set_display_window(self, x0, y0, x1, y1):
        # RAM is organised by byte
        self.send_command(0x44)
        self.send_data((x0 >> 3) & 0xff)
        self.send_data((x1 >> 3) & 0xff)

        # We first gotta send the lower 8 bits and then the upper 9th
        # bit of each y coord
        self.send_command(0x45)
        self.send_data(y0 & 0xff)
        self.send_data((y0 >> 8) & 0xff)
        self.send_data(y1 & 0xff)
        self.send_data((y1 >> 8) & 0xff)
        