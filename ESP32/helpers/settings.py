# Standard micropython libraries
from machine import SoftI2C
from machine import freq

# Local modules and variables
from sensor import BMP280
from wireless import WLAN


class Settings:
    def __init__(self,
                 esp32: dict = None,
                 i2c1: dict = None,
                 i2c2: dict = None,
                 timer_period: int = 15) -> None:
        """
        The Settings class is used to set up the ESP32 module, I2C bus(es), \
            and BMP280 modules.
        - arguments: None
        - keyword arguments:
            - esp32: `dict`. The ESP32 dictionary in the main.py file.
            - i2c1: `dict`. The I2C1 dictionary in the main.py file.
            - i2c2: `dict`. The I2C2 dictionary in the main.py file.
            - timer_period: `int`. The time in milliseconds between \
                consecutive measurements (minimum time interval).
        """
        self.esp32: dict = esp32
        self.i2c_A: object = SoftI2C(**i2c1)  # I2C bus setup
        self.i2c_B: object = SoftI2C(**i2c2)
        self.timer_period: int = timer_period

    def _esp32(self) -> None:
        """ General configuration of the device. """
        self.red_freq: int = 240_000_000
        freq(self.esp32['FREQ'])
        self.red_freq -= freq()

    def wireless(self, ssid, password) -> None:
        """ Connecting device to internet """
        self.internet = WLAN(ssid, password)
        self.internet.connect()

    def _sensor(self, BUS_A: bool = True, BUS_B: bool = False) -> None:
        if BUS_A:
            self.sensor_A1: object = BMP280(
                self.i2c_A, 0x76, timer_id=0, timer_period=self.timer_period)
            self.sensor_A2: object = BMP280(
                self.i2c_A, 0x77, timer_id=1, timer_period=self.timer_period)
        if BUS_B:
            self.sensor_B1: object = BMP280(
                self.i2c_B, 0x76, timer_id=2, timer_period=self.timer_period)
            self.sensor_B2: object = BMP280(
                self.i2c_B, 0x77, timer_id=3, timer_period=self.timer_period)

    def bmp280_setup(self, sensor: list, power: int = None, iir: int = None,
                     spi: bool = False, os: tuple = None) -> None:
        """
        Setup function for the BMP280 sensors.
        """
        for s in sensor:
            s.spi(state=spi)
            if power is not None:
                s.power(mode=power)
            if iir is not None:
                s.iir(mode=iir)
            if os is not None:
                s.oversampling(pres_temp=os)

    def settings(self,
                 BUS_A: bool = True,
                 BUS_B: bool = False) -> list[object]:
        """
        Configure the settings of the ESP32.

        - Arguments: `None`
        - Keyword Arguments:
            - BUS_A: `bool`. Activate two sensors on I2C bus A
            - BUS_B: `bool`. Activate two sensors on I2C bus B
        """
        assert [BUS_A, BUS_B] != [False, False]
        self._esp32()
        self._sensor(BUS_A=BUS_A, BUS_B=BUS_B)
        if BUS_A and BUS_B:
            return [
                self.sensor_A1, self.sensor_A2,
                self.sensor_B1, self.sensor_B2
            ]
        else:
            return [self.sensor_A1, self.sensor_A2] \
                if BUS_A else [self.sensor_B1, self.sensor_B2]

    def __str__(self) -> str:
        _scan: function = lambda val: list(map(hex, val.scan()))
        return "\n".join([
            f"\nESP32 FREQUENCY:",
            f"\tORIGINAL:   {(self.red_freq + freq())/1e6} MHz",
            f"\tREDUCED TO: {freq()/1e6} MHz",
            f"\tDIFFERENCE: {self.red_freq/1e6} MHz",
            f"\nWLAN:",
            "\n".join(f"\t{k}: {v}"
                      for k, v in self.internet.ifconfig().items()),
            f"\nI2C:",
            f"\tBUSES:          {[self.i2c_A, self.i2c_B]}",
            f"\tAVAILABLE ADDR: {[_scan(self.i2c_A), _scan(self.i2c_B)]}",
            f"\n",
        ])
