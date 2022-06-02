# Standard micropython libraries
from ustruct import unpack
from machine import Timer

# Local modules and variables
from sensor.registers import REGISTERS as REG
from sensor.registers import PRESSURE as PRES
from sensor.registers import COMPENSATION as COMP


class BMP280:
    def __init__(self, i2c: object, address: int, timer_id: int=0) -> None:
        self._i2c: object = i2c
        self._addr: int = address

        # Variables for the read/write limiter
        self.timer_id = timer_id
        self.limiter = True

        # Compensation data for temperature and pressure
        self.tC: list = self._compensation(COMP.TEMP)
        self.pC: list = self._compensation(COMP.PRES)

        # Variables for handling output
        self.rawT: float = 0.0
        self.fineT: float = 0.0
        self.rawP: float = 0.0

    def _rw_limiter_init(self):
        """
        Initialization function for the Read/Write limiter.
        The function makes sure that the BMP280 cannot be accessed quicker
        than the period time described in the Timer function.

        The current limiter is set at 25 milliseconds (40 Hz).

        This is not a 'sleep' function. The code will continue unless a quick
        access is desired. Then it will wait until the timer has run out.
        """
        self.limiter: bool = False
        Timer(self.timer_id).init(
            period=25,
            mode=Timer.ONE_SHOT,
            callback=self._rw_limiter
        )

    def _rw_limiter(self, *args) -> None:
        """ Set the limiter at True (Timer has passed). """
        self.limiter: bool = True

    def _read(self, reg_addr: int, size: int=1) -> bytes:
        while not self.limiter: pass
        self._rw_limiter_init()
        return self._i2c.readfrom_mem(self._addr, reg_addr, size)

    def _read_bits(self, reg_addr: int, length: int, shift: int=0) -> int:
        return self._read(reg_addr)[0] >> shift & int('1' * length, 2)

    def _write(self, reg_addr: int, data: bytearray) -> None:
        if not isinstance(data, bytearray):
            data: bytearray = bytearray([data])
        while not self.limiter: pass
        self._rw_limiter_init()
        self._i2c.writeto_mem(self._addr, reg_addr, data)

    def _write_bits(self, reg_addr: int, value: int,
                    length: int, shift: int=0) -> None:
        data: int = self._read(reg_addr)[0]
        val: int = int('1' * length, 2) << shift
        data &= ~val  # data && inverse val = bit value (0, 1)
        data |= val & value << shift  # data || (val && value) << shift
        self._write(reg_addr, data)

    def _measurement(self) -> None:
        # Read all data at once. The data bytes are at 0xF7:0xFC (6 bytes)
        data: list = self._read(PRES.MSB, size=6)
        # Converting function. Bit shifts three values to one (20-bit value)
        convert: function = lambda msb, lsb, xlsb: (
            (msb << 12) + (lsb << 4) + (xlsb >> 4))
        self.rawP, self.rawT = convert(*data[:3]), convert(*data[3:])

        self.fineT: float = (
            (self.rawT / 2.0**14.0 - self.tC[0] / 2.0**10.0)
            * self.tC[1]
            + ((self.rawT / 2.0**17.0 - self.tC[0] / 2.0**13.0)**2.0)
            * self.tC[2]
        )

    def _temperature(self) -> float:
        return self.fineT / ((2.0**9.0) * 10.0)
    
    def _pressure(self) -> float:
        var1: float = ((1.0 + (self.pC[2] * (self.fineT / 2.0 - 64e3)**2.0 
               / 2.0**19.0 + self.pC[1] * (self.fineT / 2.0 - 64e3))
               / 2.0**19.0 / 2.0**15.0) * self.pC[0])
        var2: float = (((((self.fineT / 2.0 - 64e3)**2.0 * self.pC[5] / 2.0**15.0)
               + (self.fineT / 2.0 - 64e3) * self.pC[4] * 2.0) / 4.0)
               + (self.pC[3] * 2.0**16.0))

        try:
            p: float = (((2.0**20.0 - self.rawP) - (var2 / 2.0**12.0))
                * (5.0**4.0)*10.0 / var1)
            p += (((self.pC[8] * p**2.0 / 2.0**31.0)
                 + (p * self.pC[7] / 2.0**15.0) + self.pC[6]) / 2.0**4.0)
        except:
            p: float = 0.0
        finally:
            return p

    def _compensation(self, compensate: list) -> list:
        return [
            unpack(comp[0], self._read(*comp[1:]))[0]
            for comp in compensate
        ]

    def reset(self) -> None:
        """ This function resets the BMP280. """
        self._write(REG.RESET, 0xB6)

    def print_compensation(self) -> None:
        printFunc: function = lambda c, num, val: print(
            f"\t{c}{num+1}: {val}, {type(val)=}"
        )
        print('Temperature Compensation Values:')
        [printFunc('T', pos, temp) for pos, temp in enumerate(self.tC)]
        print('Pressure Compensation Values:')
        [printFunc('P', pos, pres) for pos, pres in enumerate(self.pC)]

    def status(self) -> tuple[bool, bool]:
        """
        This function fetches the status bits of the BMP280.
        
        The function returns two values in a tuple:
        - Updating [bool]
        - Measuring [bool]

        More info? See chapter 4.3.3 of the datasheet.
        """
        return tuple(
            self._read_bits(REG.STATUS, 1, shift=0),
            self._read_bits(REG.STATUS, 1, shift=3),
        )

    def chip_id(self) -> bytearray:
        """
        This function returns the Chip ID in bytearray.
        The ID is (according to the datasheet, see chapter 4.3.1)
        always `0x58`. To read out the value as an integer, make sure to
        read out the first value of the list (`[0]`).
        """
        return self._read(REG.IDENTIFICATION, size=2)

    def fetch(self, temp: bool=True, pres: bool=True) -> list[int|None]:
        """
        Read temperature and/or pressure values from the BMP280.
        The temperature and pressure values can be selected for returning.

        Usage::

            # Fetch both values
            temperature, pressure = BMP280().fetch()
            # Fetch only temperature
            temperature = BMP280().fetch(pres=False)
            # Fetch only pressure
            pressure = BMP280().fetch(temp=False)

            # An empty string is returned if both kwargs are set as False.
        """
        self._measurement()
        return [
            value for value in [
                self._temperature() if temp else None,
                self._pressure() if pres else None
            ] if value is not None
        ]

    def standby(self, time: int=None) -> int | None:
        """
        Read/Write function for the standby time.
        
        Usage::

            from sensor import SETTINGS
            # Read mode
            value = BMP280().standby()
            # Write mode
            BMP280().standby(time=SETTINGS().standbyTime(0 <= x <= 7))
        
        See `ESP32\\sensor\\settings.py` for more information.
        """
        if not time:
            return self._read_bits(REG.CONFIG, 3, shift=5)
        assert 0x00 <= time <= 0x07
        self._write_bits(REG.CONFIG, time, 3, shift=5)

    def iir(self, mode: int=None) -> int | None:
        """
        Read/Write function for the Infinite Impulse Response (IIR) settings.

        Usage::

            from sensor import SETTINGS
            # Read mode
            value = BMP280().iir()
            # Write mode
            BMP280().iir(mode=SETTINGS().iirMode(0 <= x <= 4))
        
        See `ESP32\\sensor\\settings.py` for more information.
        """
        if not mode:
            return self._read_bits(REG.CONFIG, 3, shift=2)
        assert 0x00 <= mode <= 0x04
        self._write_bits(REG.CONFIG, mode, 3, shift=2)

    def spi(self, state: bool=None) -> int | None:
        """
        Read/Write function for the SPI settings.

        Usage::

            # Read mode
            value = BMP280().spi()
            # Write mode
            BMP280().spi(state=True or False)
        
        See `ESP32\\sensor\\registers.py` for more information.
        """
        if state is None:
            return self._read_bits(REG.CONFIG, 1, shift=0)
        assert isinstance(state, bool)
        self._write_bits(REG.CONFIG, int(state), 1, shift=0)

    def oversampling(self, pres_temp: tuple=None) -> list[int] | None:
        """
        Read/Write function for the oversampling settings.
        This function sets the pressure and temperature oversampling settings
        at once.

        Usage::

            from sensor import SETTINGS
            # Read mode
            pres, temp = BMP280().oversampling()
            # Write mode
            BMP280().oversampling(pres_temp=SETTINGS().osMode(
                0 <= x <= 5, 0 <= y <= 5
            ))
        
        See `ESP32\\sensor\\settings.py` for more information.
        """
        if not pres_temp:
            return [
                self._read_bits(REG.CTRL_MEAS, 3, shift=2),
                self._read_bits(REG.CTRL_MEAS, 3, shift=5),
            ]
        assert 0x00 <= pres_temp[0] <= 0x05 and 0x00 <= pres_temp[1] <= 0x05
        self._write_bits(REG.CTRL_MEAS, pres_temp[0], 3, shift=2)
        self._write_bits(REG.CTRL_MEAS, pres_temp[1], 3, shift=5)

    def power(self, mode: int=None) -> int | None:
        """
        Read/Write function for the power settings.

        Usage::

            from sensor import SETTINGS
            # Read mode
            value = BMP280().power()
            # Write mode
            BMP280().power(SETTINGS().powerMode(0 <= x <= 2))
        
        See `ESP32\\sensor\\settings.py` for more information.
        """
        if not mode:
            return self._write_bits(REG.CTRL_MEAS, 2, shift=0)
        assert 0x00 <= mode <= 0x03
        self._write_bits(REG.CTRL_MEAS, mode, 2, shift=0)
