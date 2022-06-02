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
        self.wlan: object = network.WLAN(network.STA_IF)

    def active(self, state: bool=None) -> None | str:
        """
        This method can be used to activate the networking module.
        It also can be used to fetch the current state of the module.

        Usage::

            # Activate module:
            WLAN().active(True)
            # Deactivate module:
            WLAN().active(False)
            # Fetch state:
            WLAN().active()
        """
        if state is None:
            return self.wlan.active()
        self.wlan.active(state)
    
    def scan(self):
        return self.wlan.scan()
    
    def config(self):
        return self.wlan.config('mac')
    
    def isConnected(self):
        return self.wlan.isconnected()
    
    def ifconfig(self) -> list:
        return self.wlan.ifconfig()

    def connect(self) -> None:
        _time = time()
        self.active(True)
        if not self.isConnected():
            print('Connecting to network...')
            self.wlan.connect(self.SSID, self.PWD)
            while not self.isConnected():
                if time() - _time >= self.timeout:
                    print('RESET DEVICE...')
                    machine.reset()

    def __str__(self) -> str:
        return f"Network configuration: {self.ifconfig()}"
