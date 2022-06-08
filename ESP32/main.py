# Standard micropython libraries
from machine import Pin

# Local modules and variables
from helpers import Data
from helpers import Settings
from sensor import BMP280
from sensor import SETTINGS as S
from mqtt import Connector

# General settings for the ESP32
ESP32: dict = dict(
    FREQ=80_000_000,
    DEBUG=True  # Set this value to False if debug is not desired.
)

# I2C Settings:
#   sda:  Data Pin  -> Data communication line
#   scl:  Clock Pin -> Clock line
#   freq: Baudrate  -> Communication speed in Hz
I2C1: dict = dict(sda=Pin(18), scl=Pin(19), freq=100_000)
I2C2: dict = {"sda": Pin(22), "scl": Pin(23), "freq": 100_000}

# The timeout timer for the BMP280. This value is the least time in
# milliseconds between consecutive measurements on one BMP280 sensor.
TIMER: int = 75


def main(debug: bool=False):
    i2c = Settings(esp32=ESP32, i2c1=I2C1, i2c2=I2C2, timer_period=TIMER)
    sensor: list[BMP280] = i2c.settings()
    if debug: print('DEBUG IS ON\n', i2c)
    i2c.bmp280_setup(
        sensor,
        power=S().powerMode(2),
        iir=S().iirMode(3),
        spi=False,
        os=S().osMode(2, 4),
    )

    while True:
        data: object = Data(sensor, amount=10)
        _ = data.get()
        print(data)

if __name__ == '__main__':
    main(debug=ESP32["DEBUG"])
