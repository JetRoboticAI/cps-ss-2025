import smbus2
from time import sleep

# Define some device parameters
I2C_ADDR = 0x27  # Adjust to your I2C address
LCD_WIDTH = 16   # Characters per line

# Define some device constants
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

LCD_BACKLIGHT = 0x08  # On
ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

bus = smbus2.SMBus(1)  # Rev 2 Pi uses bus 1

class Lcd:
    def __init__(self):
        self.lcd_init()

    def lcd_init(self):
        self.lcd_byte(0x33, LCD_CMD)
        self.lcd_byte(0x32, LCD_CMD)
        self.lcd_byte(0x06, LCD_CMD)
        self.lcd_byte(0x0C, LCD_CMD)
        self.lcd_byte(0x28, LCD_CMD)
        self.lcd_byte(0x01, LCD_CMD)
        sleep(E_DELAY)

    def lcd_byte(self, bits, mode):
        bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

        bus.write_byte(I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)

        bus.write_byte(I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
        sleep(E_DELAY)
        bus.write_byte(I2C_ADDR, (bits | ENABLE))
        sleep(E_PULSE)
        bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
        sleep(E_DELAY)

    def lcd_display_string(self, message, line):
        message = message.ljust(LCD_WIDTH, " ")
        if line == 1:
            self.lcd_byte(LCD_LINE_1, LCD_CMD)
        elif line == 2:
            self.lcd_byte(LCD_LINE_2, LCD_CMD)

        for char in message:
            self.lcd_byte(ord(char), LCD_CHR)

    def lcd_clear(self):
        self.lcd_byte(0x01, LCD_CMD)
