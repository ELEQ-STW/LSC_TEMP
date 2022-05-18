# Standard micropython libraries
import machine
import I2C
from time import time, sleep

# Local modules and variables
from sensor import BMP280, SETTINGS
from umqtt import MQTTClient
from .wireless import WLAN
from .boot import SETTINGS, INTERNET, I2C1, I2C2


def main():
    internet: object = WLAN(
        INTERNET['SSID'],
        INTERNET['PASSWORD'],
    )
    internet.connect()
    
    sleep(1)

    print('DONE!')

if __name__ == '__main__':
    main()