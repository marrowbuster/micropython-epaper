# this assumes the config module has already been uploaded to the board's internal storage
import config
import utime
from machine import Pin, SPI

commands = {'DRIVER_OUTPUT_CONTROL': 0x01,
            'GATE_DRIVING_VOLTAGE_CONTROL': 0x03,
            'SOURCE_DRIVING_VOLTAGE_CONTROL': 0x04,
            'INITIAL_CODE_SETTING_OTP_PROGRAM': 0x08,
            'WRITE_INITIAL_CODE_SETTING_REGISTER': 0x09,
            'READ_INITIAL_CODE_SETTING_REGISTER': 0x0a,
            'BOOSTER_SOFT_START_CONTROL': 0x0c,
            'DEEP_SLEEP_MODE': 0x10,
            'DATA_ENTRY_MODE_SETTING': 0x11,
            'SW_RESET': 0x12,
            'HV_READY_DETECTION': 0x14,
            'VCI DETECTION': 0x15,
            'TEMPERATURE_SENSOR_CONTROL': 0x18,
            'WRITE_TO_TEMPERATURE_REGISTER': 0x1a,
            'READ_FROM_TEMPERATURE_REGISTER': 0x1b,
            'WRITE_COMMAND_TO_EXTERNAL_TEMPERATURE_REGISTER': 0x1c,
            'MASTER_ACTIVATION': 0x20,
            'DISPLAY_UPDATE_CONTROL_1': 0x21,
            'DISPLAY_UPDATE_CONTROL_2': 0x22,
            'WRITE_RAM_BW': 0x24,
            'WRITE_RAM_RED': 0x26,
            'READ_RAM': 0x27,
            'VCOM_SENSE': 0x28,
            'VCOM_SENSE_DURATION': 0x29,
            'PROGRAM_VCOM_OTP': 0x2a,
            'WRITE_VCOM_CONTROL_REGISTER': 0x2b,
            'WRTIE_VCOM_REGISTER': 0x2c,
            'WRITE_OTP_DISPLAY_OPTION_REGISTER': 0x2d,
            'USER_ID_READ': 0x2e,
            'STATUS_BIT_READ': 0x2f,
            'PROGRAM_WS_OTP': 0x30,
            'LOAD_WS_OTP': 0x31,
            'WRITE_LUT_REGISTER': 0x32,
            'CRC_CALCULATION': 0x34,
            'CRC_STATUS_READ': 0x35,
            'PROGRAM_OTP_SELECTION': 0x36,
            'WRITE_DISPLAY_OPTION_REGISTER': 0x37,
            'WRITE_USER_ID_REGISTER': 0x38,
            'OTP_PROGRAM_MODE': 0x39,
            'BORDER_WAVEFORM_CONTROL': 0x3c,
            'END_OPTION': 0x3f,
            'READ_RAM_OPTION': 0x41,
            'SET_START_AND_END_X': 0x44,
            'SET_START_AND_END_Y': 0x45,
            'AUTO_WRITE_REGULAR_PATTERN_INTO_RED_RAM': 0x46,
            'AUTO_WRITE_REGULAR_PATTERN_INTO_BW_RAM': 0x47,
            'SET_X_ADDRESS_COUNTER': 0x4e,
            'SET_Y_ADDRESS_COUNTER': 0x4f,
            'NOP': 0x7f}

display_dimensions = {'x': 250,
                      'y': 122}

rotations = {'0': 0,
             '90': 1,
             '180': 2,
             '270': 3}

class EPD:
    
    def __init__(self, rst, dc, cs, busy, sck, pico):
        self.rst_pin = rst
        self.rst_pin.mode(Pin.OUT)

        self.dc_pin = dc
        self.dc_pin.mode(Pin.OUT)

        self.cs_pin = cs
        self.cs_pin.mode(Pin.OUT)
        self.cs_pin.pull(Pin.PULL_UP)

        self.busy_pin = busy
        self.busy_pin.mode(Pin.IN)

        self.spi_device = SPI(1,
                              baudrate = int(4e6), # lazy af
                              polarity = 1,
                              phase = 1,
                              bits = 8,
                              firstbit = SPI.MSB,
                              sck = sck,
                              mosi = pico,
                              miso = None)
        
        self.width = display_dimensions['x']
        self.height = display_dimensions['y']
        self.rotate = rotations['0']

    def reset(self):
        # reset is active low
        self.rst_pin(False)
        self.delay_ms(200)
        self.rst_pin(True)
        self.delay_ms(200)

    def delay_ms(self, interval):
        utime.sleep_ms(interval)
    
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
            self.dc_pin(False)
            self.cs_pin(False)
            self.spi_device.write(cmd)
        except ValueError as e:
            print(f'command send error: {e}')
        finally:
            self.cs_pin(True)

    def send_data(self, data):
        # d/c means data/command, pull high for data, pull low for command
        try:
            self.dc_pin(True)
            self.cs_pin(False)
            self.spi_device.write(data)
        finally:
            self.cs_pin(True)

    def busy(self):
        while self.busy_pin():
            self.delay_ms(100)

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
    
    def set_cursor(self, x, y):
        self.send_command(0x4e)
        self.send_data(x & 0xff)

        self.send_command(0x4f)
        self.send_data(y & 0xff)
        self.send_data((y >> 8) & 0xff)
    
    def startup(self):
        self.reset()

        self.busy()
        self.send_command(0x12)
        self.busy()

        self.send_command(0x01)
        # 249 in decimal, datasheet specifies the number of lines for
        # the driver, 250 (due to a vertical resolution of 250px) which
        # is defined in the datasheet as "MUX[8:0] + 1" (page 34)
        self.send_data(0xf9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)
        self.send_command(0x03)

        self.set_display_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(0x3c)
        self.send_data(0x05)

        self.send_command(0x18)
        self.send_data(0x80)
        self.send_data(0x80)

        self.busy()