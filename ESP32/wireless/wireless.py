# Standard micropython libraries
import machine
import network
from time import time


class WLAN:
    def __init__(self, ssid: str, pwd: str, timeout: int = 10) -> None:
        self.SSID: str = ssid
        self.PWD: str = pwd
        self.timeout: int = timeout
        self.wlan: object = network.WLAN(network.STA_IF)

    def active(self, state: bool = None) -> None | bool:
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

    def scan(self) -> list:
        return self.wlan.scan()

    def config(self) -> bytes:
        return self.wlan.config('mac')

    def isConnected(self) -> bool:
        return self.wlan.isconnected()

    def ifconfig(self) -> dict:
        return {
            param: value for param, value in
            zip(['IP', 'SUBNET', 'GATEWAY', 'DNS'], self.wlan.ifconfig())
        }

    def disconnect(self) -> None:
        self.wlan.disconnect()

    def status(self) -> int:
        return self.wlan.status()

    def connect(self) -> None:
        _time = time()
        self.active(True)
        if not self.isConnected():
            self.wlan.connect(self.SSID, self.PWD)
            while not self.isConnected():
                if time() - _time >= self.timeout:
                    print("ERROR: Connection timeout. Resetting device ...")
                    machine.reset()

    def __str__(self) -> str:
        return f"Network configuration: {self.ifconfig()}"
