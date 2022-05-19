# Standard micropython libraries
import machine
import network
from time import time
from time import sleep


class WLAN:
    def __init__(self, ssid: str, pwd: str, timeout: int=10) -> None:
        self.SSID: str = ssid
        self.PWD: str = pwd
        self.timeout: int = timeout

    def connect(self) -> None:
        _time = time()
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('Connecting to network...')
            wlan.connect(self.SSID, self.PWD)
            while not wlan.isconnected():
                if time() - _time >= self.timeout:
                    print('RESET DEVICE...')
                    sleep(0.1)  # Give the ESP32 time to print the line before resetting
                    machine.reset()  # Reset ESP32

        print(f"Network configuration: {wlan.ifconfig()}")
