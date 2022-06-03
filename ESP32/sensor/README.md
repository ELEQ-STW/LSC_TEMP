# BMP280 Micropython library
This library is inspired by the work of [dafvid (GitHub)](https://github.com/dafvid/micropython-bmp280).

## Table of Content
1. [Usage](#usage)
    1. [Create Object](#create-object)
    2. [Read/Write to the Sensor](#readwrite-to-the-sensor)
        1. [Read/Write to Registers](#readwrite-to-registers)
        2. [Read Measurement Data](#read-measurement-data)
        3. [Read Compensation Data](#read-compensation-data)
2. [Python Files](#python-files)
    1. [Initialization File](#initialization-file)
    2. [Register File](#register-file)
    3. [Settings File](#settings-file)
    4. [BMP280 Control File](#bmp280-control-file)
3. [Revision History](#revision-history)

## Usage
This library can be used as follows:
- Create class object
- Reading/Writing to the sensor
    - Reading/Writing to registers
    - Reading measurement data

### Create Object
Before we create an `BMP280` class object, the following needs to be defined:
- Which pins will be used to communicate with the sensor?
- Which communication protocol will be used? [I<sup>2</sup>C]
- What will be the communication speed?

``` Python
""" In this example SoftI2C (I2C) is used """
from machine import Pin, SoftI2C
from sensor import BMP280

PIN_SCL: int = X  # Physical pin on the microcontroller
PIN_SDA: int = X  # Physical pin on the microcontroller
i2c_bus: object = SoftI2C(
    scl=Pin(PIN_SCL),  # Clock pin
    sda=Pin(PIN_SDA),  # Data pin
    freq=100_000,  # Communication speed in Hz
)
bmp280_sensor = BMP280(
    i2c=i2c_bus,  # i2c_bus object
    address=0x76 or 0x77  # I2C address of the sensor, dependent on the configuration
    timer_id=0 or 1 or 2 or 3 # Default: 0. Max 4 timers can be used on the ESP32. These will make sure the communication timeout is sufficient
    timer_period=10 <= x  # Timeout time in milliseconds 
)
```

### Read/Write to the Sensor
Before the sensor is accessed, make sure the BMP280 object is defined and accessible before continuing.

#### Read/Write to Registers
The following can be accessed:
- Reset [_Write_]
- Status [_Read_]
- Chip ID [_Read_]
- Standby Time [_Read_/_Write_]
- Infinite Impulse Response [_Read_/_Write_]
- SPI Mode [_Read_/_Write_]
- Oversampling Configuration [_Read_/_Write_]
- Power Mode [_Read_/_Write_]

``` Python
""" Writing to the Registers """
from sensor import SETTINGS
bmp280_sensor.reset()  # Resetting sensor
bmp280_sensor.standby(SETTINGS().standbyTime(int))  # Configuring standby time
bmp280_sensor.iir(SETTINGS().iirMode(int))  # Configuring IIR settings
bmp280_sensor.spi(bool)  # Turning on or off SPI
bmp280_sensor.oversampling(SETTINGS().osMode(int, int))  # Configuring oversampling modes for Pressure and Temperature measurements
bmp280_sensor.power(SETTINGS().powerMode(int))  # Configuring the power mode of the sensor

""" Reading data from the registers """
status: tuple[bool, bool] = bmp280_sensor.status()  # Fetch status of the sensor
chip_id: int = hex(bmp280_sensor.chip_id()[0])  # Fetch the ID of the sensor [0x58]
standby: int = bmp280_sensor.standby()  # Fetch standby configuration of the sensor
iir: int = bmp280_sensor.iir()  # Fetch IIR configuration for the measurements
spi: bool = bool(bmp280_sensor.spi())  # Fetch SPI status of the sensor
oversampling: list[int, int] = bmp280_sensor.oversampling()  # Fetch oversampling modes for the Pressure and Temperature measurements
power: int = bmp280_sensor.power()  # Fetch power mode configuration of the sensor  
```

#### Read Measurement Data
Reading the measurement data is quite simple.
``` Python
data: list[float, float] = bmp280_sensor.fetch()
temperature: float = data[0]  # Temperature in degrees Celsius
pressure: float = data[1]  # Pressure in Pascal [Pa]
pressure /= 100.0  # Pressure in Hectopascal [hPa]
```

#### Read Compensation Data
Reading the compensation data is also quite simple.
``` Python
print(bmp280_sensor)
```


## Python Files
The BMP280 library uses four files, of which three are mandatory:
| File Name       | Mandatory          | Description                                 |
| :-------------- | :----------------: | :-----------------------------------------: |
| `__init__.py`   | :x:                | [Initialization File](#initialization-file) |
| `registers.py`  | :heavy_check_mark: | [Register File](#register-file)             |
| `settings.py`   | :heavy_check_mark: | [Settings File](#settings-file)             |
| `bmp280.py`     | :heavy_check_mark: | [BMP280 Control File](#bmp280-control-file) |

### Initialization File
The initialization file, otherwise called `__init__`, initializes all files in the directory.
This file imports the other files so that the `main` code is cleaner.
``` Python
# main import: from sensor import BMP280
from .bmp280 import BMP280

# main import: from sensor import SETTINGS
from .settings import SETTINGS

# main import: from sensor import REGISTERS, PRESSURE, TEMPERATURE, COMPENSATION
from .registers import REGISTERS
from .registers import PRESSURE
from .registers import TEMPERATURE
from .registers import COMPENSATION
```
Otherwise the user has to call the files independently, which results in the following code:
``` Python
""" This code is as seen from the ESP32 folder """
from sensor.bmp280 import BMP280
from sensor.settings import SETTINGS
from sensor.registers import REGISTERS, PRESSURE, TEMPERATURE, COMPENSATION
```
Overall, it is recommended to use `__init__.py`. Usage without can go wrong, it has not been tested. __Use at your own risk!__

### Register File
The register file, otherwise known as `registers.py`, holds all the configuration registers of the BMP280 sensor. It is directly accessed by the `bmp280.py` file, hence the requirement.

The registers and details of it can be found in the following datasheet made by Bosch Sensortec: [datasheet][DATASHEET].

### Settings File
The settings file, otherwise known as `settings.py`, holds all possible configuration settings for the BMP280 registers. The user can use `settings.py` and `bmp280.py` to set specific registers.
Each function has some details about the settings. More information required? See the [datasheet][DATASHEET] made by Bosch Sensortec.


### BMP280 Control File
The BMP280 Control file, otherwise known as `bmp280.py`, is used to set and read registers (in combination with [settings.py](#settings-file) is recommended but not required) and read the _temperature_ and _pressure_ measurements.

The file is currently tested with the [I<sup>2</sup>C](https://en.wikipedia.org/wiki/I%C2%B2C) communication protocol, SPI can be broken. __Use SPI with precaution!__


## Revision History
| Release Name | Changed By      | Date       | Commit(s)      |
| :----------: | :-------------- | :--------: | :------------: |
| v1.1.0       | @DutchFakeTuber | 03-06-2022 | [c2def56][C11]
| v1.0.1       | @DutchFakeTuber | 02-06-2022 | [d6723b0][C10] |
| v1.0.0       | @DutchFakeTuber | 02-06-2022 | [7d9faaf][C9]  |
| v0.2.0       | @DutchFakeTuber | 02-06-2022 | [7b487c7][C8]  |
| v0.1.1       | @DutchFakeTuber | 01-06-2022 | [79f227e][C6], [f621ce5][C7] |
| v0.1.0       | @DutchFakeTuber | 31-05-2022 | [5edb810][C3], [160218e][C4] & [edbb93e][C5] |
| v0.0.2       | @DutchFakeTuber | 19-05-2022 | [43ad394][C2]  |
| v0.0.1       | @DutchFakeTuber | 18-05-2022 | [b3cf2fc][C1]  |

[DATASHEET]: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf
[C1]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/b3cf2fc4a86e30e3900b2d122a08b5f0eb52edff
[C2]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/43ad394e35e6b15b93872f4744bedda8bb6a366d
[C3]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/5edb8100a0f430d6b37bf4a54f1db9a857062a5c
[C4]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/160218eaaffb7b2a1381604113e40e463913de89
[C5]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/edbb93ee523c3776fec94e692209468bdfa48a29
[C6]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/79f227eef42b5ccded10e73e332a0f86721d172d
[C7]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/f621ce5c5c0a35a9ef34227ecce653acdb208cb2
[C8]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/7b487c7e944ff81359a6b463968a5d2d669eaba8
[C9]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/7d9faaf76b07cd3bf7b5533e8e1d8539565b1f2c
[C10]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/d6723b06b39d475efcfca9462cf4d536ca9a46f7
[C11]: https://github.com/DutchFakeTuber/LSC_TEMP/commit/c2def56f209a26948484e4632a9b97e2a74f0a48
