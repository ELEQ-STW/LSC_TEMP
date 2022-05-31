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
        self.wlan: object = None

    def __str__(self) -> str:
        return f"Network configuration: {self.wlan.ifconfig()}"

    def connect(self) -> None:
        _time = time()
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print('Connecting to network...')
            self.wlan.connect(self.SSID, self.PWD)
            while not self.wlan.isconnected():
                if time() - _time >= self.timeout:
                    print('RESET DEVICE...')
                    sleep(0.1)  # Give the ESP32 time to print the line before resetting
                    machine.reset()  # Reset ESP32
