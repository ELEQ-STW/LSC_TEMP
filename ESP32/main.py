# Standard micropython libraries
import machine
from machine import SoftI2C, Pin
from time import time, sleep

# Local modules and variables
from sensor import BMP280, SETTINGS
from umqtt import MQTTClient
from wireless import WLAN, SSID, PASSWORD

# General settings for the ESP32
SETTINGS: dict = dict(FREQ=80_000_000)
INTERNET: dict = dict(
    SSID=SSID,
    PASSWORD=PASSWORD
)

# I2C Settings:
#   SDA: Data Pin  -> Data communication line
#   SCL: Clock Pin -> Clock line
#   CLK: Baudrate  -> Communication speed in Hz
I2C1: dict = dict(SDA=18, SCL=19, CLK=400_000)
I2C2: dict = dict(SDA=22, SCL=23, CLK=400_000)


def main():
    # Connecting ESP32 to the internet
    internet: object = WLAN(
        INTERNET['SSID'],
        INTERNET['PASSWORD'],
    )
    internet.connect()

    # Set clock speed
    machine.freq(SETTINGS['FREQ'])
    i2c_A = SoftI2C(
        scl=Pin(I2C1['SCL']),
        sda=Pin(I2C1['SDA']),
        freq=I2C1['CLK'],
    )
    print(f"BMP280 ADDRESSES: {list(map(hex, i2c_A.scan()))}")
    bmp280_A1 = BMP280(i2c_A, 0x76, timer_id=0)
    bmp280_A2 = BMP280(i2c_A, 0x77, timer_id=1)

    id1 = bmp280_A1.chip_id()[0]
    id2 = bmp280_A2.chip_id()[0]
    print(f"HEX: {hex(id1)}; INT: {int(id2)}; BIN: {bin(id1)}")
    print(f"HEX: {hex(id2)}; INT: {int(id2)}; BIN: {bin(id2)}")

if __name__ == '__main__':
    main()
