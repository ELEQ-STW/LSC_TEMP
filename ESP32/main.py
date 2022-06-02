# Standard micropython libraries
import machine
from machine import SoftI2C, Pin
from time import time_ns

# Local modules and variables
from sensor import BMP280
from sensor import SETTINGS as S
from umqtt import MQTTClient
from wireless import WLAN, SSID, PASSWORD

# General settings for the ESP32
ESP32: dict = dict(
    FREQ=80_000_000,
    DEBUG=True  # Set this value to False if debug is not desired.
)

# I2C Settings:
#   sda:  Data Pin  -> Data communication line
#   scl:  Clock Pin -> Clock line
#   freq: Baudrate  -> Communication speed in Hz
I2C1: dict = dict(scl=Pin(19), sda=Pin(18), freq=100_000)
I2C2: dict = dict(scl=Pin(23), sda=Pin(22), freq=100_000)


class Settings:
    def __init__(self, i2c1: dict=I2C1, i2c2: dict=I2C2) -> None:
        self.i2c_A: object = SoftI2C(**i2c1) # I2C bus setup
        self.i2c_B: object = SoftI2C(**i2c2)
    
    def _esp32(self, esp32: dict=ESP32) -> None:
        """ General configuration of the device. """
        self.red_freq: int = 240_000_000
        machine.freq(esp32['FREQ'])
        self.red_freq -= machine.freq()
    
    def _wireless(self) -> None:
        """ Connecting device to internet """
        self.internet = WLAN(SSID, PASSWORD)
        self.internet.connect()
    
    def _sensor(self) -> None:
        self.sensor_A1: object = BMP280(self.i2c_A, 0x76, timer_id=0)
        self.sensor_A2: object = BMP280(self.i2c_A, 0x77, timer_id=1)
        # self.sensor_B1: object = BMP280(self.i2c_B, 0x76, timer_id=2)
        # self.sensor_B2: object = BMP280(self.i2c_B, 0x77, timer_id=3)

    def bmp280_setup(self, sensor: list) -> None:
        for s in sensor:
            s.power(mode=S().powerMode(2))
            s.iir(mode=S().iirMode(3))
            s.spi(state=False)
            s.oversampling(pres_temp=S().osMode(2, 4))
        
    def settings(self) -> dict[object]:
        self._esp32()
        self._wireless()
        self._sensor()
        return [
            self.sensor_A1, self.sensor_A2,
            # self.sensor_B1, self.sensor_B2
        ]
    
    def __str__(self) -> str:
        _scan: function = lambda val: list(map(hex, val.scan()))
        return "\n".join([
            f"\nESP32 FREQUENCY:",
            f"\tORIGINAL:   {(self.red_freq + machine.freq())/1e6} MHz",
            f"\tREDUCED TO: {machine.freq()/1e6} MHz",
            f"\tDIFFERENCE: {self.red_freq/1e6} MHz",
            f"\nWLAN:",
            "\n".join(f"\t{k}: {v}" for k, v in self.internet.ifconfig().items()),
            f"\nI2C:",
            f"\tBUSES:          {[self.i2c_A, self.i2c_B]}",
            f"\tAVAILABLE ADDR: {[_scan(self.i2c_A), _scan(self.i2c_B)]}",
            f"\n",
        ])

class Data:
    def __init__(self, sensor: list[object], amount: int=15):
        self._sum: function = lambda data, num: [
            sum(val[num][pos] for val in data)/len(data) for pos in [0, 1]
        ]
        self.sensor: list = sensor
        self.amount: int = amount
        self.processed: list = []
    
    def _fetch(self) -> None:
        self.data: list = [
            [s.fetch() for s in self.sensor]
            for _ in range(self.amount)
        ]
    
    def get(self) -> list:
        self._fetch()
        self.processed: list = [
            self._sum(self.data, num)
            for num in range(len(self.data[0]))
        ]
        return self.processed

    def __str__(self) -> str:
        if self.processed == []:
            _ = self.get()
        return "\n".join([
            f"""{sensor._i2c} [{hex(sensor._addr)}]
            Temperature: {self.processed[num][0]} \u00b0C
            Pressure:    {self.processed[num][1]/100.0} hPa
            """
            for num, sensor in enumerate(self.sensor)
        ])


def main(debug: bool=False):
    i2c = Settings()
    sensor: list[object] = i2c.settings()
    if debug: print('DEBUG IS ON\n', i2c)
    i2c.bmp280_setup(sensor)

    data: object = Data(sensor, amount=15)
    _ = data.get()
    print(data)

if __name__ == '__main__':
    main(debug=ESP32["DEBUG"])
