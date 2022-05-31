# Standard micropython libraries
import machine
from machine import SoftI2C, Pin
from time import time, sleep

# Local modules and variables
from sensor import BMP280, SETTINGS
from umqtt import MQTTClient
from wireless import WLAN, SSID, PASSWORD

# General settings for the ESP32
ESP32: dict = dict(FREQ=80_000_000)

# I2C Settings:
#   sda:  Data Pin  -> Data communication line
#   scl:  Clock Pin -> Clock line
#   freq: Baudrate  -> Communication speed in Hz
I2C1: dict = dict(scl=Pin(19), sda=Pin(18), freq=100_000)
I2C2: dict = dict(scl=Pin(23), sda=Pin(22), freq=100_000)


def settings(debug=False) -> dict[object]:
    # Set clock speed
    machine.freq(ESP32['FREQ'])

    # Connecting ESP32 to the internet
    internet = WLAN(SSID, PASSWORD)
    internet.connect()

    # Setting up I2C Buses
    i2c_A = SoftI2C(**I2C1)
    i2c_B = SoftI2C(**I2C2)

    if debug:
        print(internet)
        # Scanning buses for devices
        for bus in [i2c_A, i2c_B]:
            print(f"BUS: {bus=};\n\tADDRESSES: {list(map(hex, bus.scan()))}")

    return dict(
        BUS_A=i2c_A,
        BUS_B=i2c_B,
    )


def main():
    # bmp280_A1, bmp280_A2, bmp280_B1, bmp280_B2 = settings()
    i2c = settings(debug=True)
    sensor_A1 = BMP280(i2c['BUS_A'], 0x76, timer_id=0)
    sensor_A2 = BMP280(i2c['BUS_A'], 0x77, timer_id=1)
    sensor_A1.power = SETTINGS().powerMode(2)
    sensor_A2.power = SETTINGS().powerMode(2)
    print(f"{sensor_A1.fetch()=}")
    print(f"{sensor_A2.fetch()=}")

if __name__ == '__main__':
    main()
