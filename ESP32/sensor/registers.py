"""
This module holds all the registers and its settings for
the BMP280 sensor from Bosch Sensortec.

The module can ultimately be used to control
and adjust the behavior of the BMP280 sensor.

MADE BY: Sybrand van Loenen
"""
# All register location and settings are directly from the datasheet.
# URL: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf

# Standard micropython libraries
# None

# Local modules and variables
# None

class REGISTERS:
    '''
    REGISTERS:
    - `0xD0`: IDENTIFICATION  [7:0]           [`R`]
        - Always holds 0x58. Therefore, very useful for debugging
          the connection.

    - `0xE0`: RESET           [7:0]           [`R`/`W`]
        - Write `0xB6` to register to reset
        - Register always contains `0x00` when read

    - `0xF3`: STATUS          [3, 0]          [`R`]
        - Bit `3`: Measuring status.
            - Value `1`: Measuring
            - Value `0`: Not measuring
        - Bit `0`: Update status
            - Value `1`: Updating
            - Value `0`: Not updating

    - `0xF4`: CTRL_MEAS       [7:5, 4:2, 1:0] [`R`/`W`]
        - Bits `7:5`: Oversampling Temperature data settings
        - Bits `4:2`: Oversampling Pressure data settings
        - Bits `1:0`: Power mode of the device

    - `0xF5`: CONFIG          [7:5, 4:2, 0]   [`R`/`W`]
        - Bits `7:5`: Standby duration settings
        - Bits `4:2`: IIR Filter time constant
        - Bit `0`: Enable/Disable 3-wire SPI
            - Value `1`: Enable
            - Value `0`: Disable
    '''
    IDENTIFICATION: int = 0xD0   # CHAPTER 4.3.1
    RESET: int = 0xE0            # CHAPTER 4.3.2
    STATUS: int = 0xF3           # CHAPTER 4.3.3
    CTRL_MEAS: int = 0xF4        # CHAPTER 4.3.4
    CONFIG: int = 0xF5           # CHAPTER 4.3.5

# Pressure registers [CHAPTER 4.3.6]
class PRESSURE:
    '''
    REGISTERS:
    - `0xF7`: MSB (Most Significant Bit)        [7:0] [`R`]
        - Contains the bits `19:12` of the raw pressure data
    - `0xF8`: LSB (Least Significant Bit)       [7:0] [`R`]
        - Contains the bits `11:4` of the raw pressure data
    - `0xF9`: XLSB (Xtra Least Significant Bit) [7:4] [`R`]
        - Contains the bits `3:0` of the raw pressure data
          Content depends on the pressure resolution
    '''
    MSB: int = 0xF7
    LSB: int = 0xF8
    XLSB: int = 0xF9

# Temperature registers [CHAPTER 4.3.7]
class TEMPERATURE:
    '''
    REGISTERS:
    - `0xFA`: MSB (Most Significant Bit)        [7:0] [`R`]
        - Contains the bits `19:12` of the raw temperature data
    - `0xFB`: LSB (Least Significant Bit)       [7:0] [`R`]
        - Contains the bits `11:4` of the raw temperature data
    - `0xFC`: XLSB (Xtra Least Significant Bit) [7:4] [`R`]
        - Contains the bits `3:0` of the raw temperature data
          Content depends on the temperature resolution
    '''
    MSB: int = 0xFA
    LSB: int = 0xFB
    XLSB: int = 0xFC

# Compensation registers [CHAPTER 3.11]
class COMPENSATION:
    '''
    The values in the compensation registers are used to get the
    most accurate data from the BMP280 sensor.

    The compensation values are stored as 16-bit integers,
    which requires two bytes of storage.

    TEMPERATURE [`0x88:0x8D`]:
        - dig_T1: [`0x88:0x89`] unsigned short
        - dig_T2: [`0x8A:0x8B`] signed short
        - dig_T3: [`0x8C:0x8D`] signed short

    PRESSURE: [`0x8E:0x9F`]:
        - dig_P1: [`0x8E:0x8F`] unsigned short
        - dig_P2: [`0x90:0x91`] signed short
        - dig_P3: [`0x92:0x93`] signed short
        - dig_P4: [`0x94:0x95`] signed short
        - dig_P5: [`0x96:0x97`] signed short
        - dig_P6: [`0x98:0x99`] signed short
        - dig_P7: [`0x9A:0x9B`] signed short
        - dig_P8: [`0x9C:0x9D`] signed short
        - dig_P9: [`0x9E:0x9F`] signed short
    '''
    TEMP: dict = dict(
        T1=['<H', 0x88, 2],
        T2=['<h', 0x8A, 2],
        T3=['<h', 0x8C, 2],
    )
    PRES: dict = dict(
        P1=['<H', 0x8E, 2],
        P2=['<h', 0x90, 2],
        P3=['<h', 0x92, 2],
        P4=['<h', 0x94, 2],
        P5=['<h', 0x96, 2],
        P6=['<h', 0x98, 2],
        P7=['<h', 0x9A, 2],
        P8=['<h', 0x9C, 2],
        P9=['<h', 0x9E, 2],
    )
    