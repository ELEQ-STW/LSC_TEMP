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
        self.limiter = False
        Timer(self.timer_id).init(
            period=100,
            mode=Timer.ONE_SHOT,
            callback=self._rw_limiter
        )

    def _rw_limiter(self, *args):
        self.limiter = True

    def _read(self, reg_addr: int, size: int=1) -> bytes:
        while not self.limiter: pass
        self._rw_limiter_init()
        return self._i2c.readfrom_mem(self._addr, reg_addr, size)

    def _read_bits(self, reg_addr: int, length: int, shift: int=0) -> int:
        return self._read(reg_addr)[0] >> shift & int('1' * length, 2)

    def _write(self, reg_addr: int, data: bytearray) -> None:
        if not isinstance(data, bytearray):
            data = bytearray([data])
        while not self.limiter: pass
        self._rw_limiter_init()
        self._i2c.writeto_mem(self._addr, reg_addr, data)

    def _write_bits(self, reg_addr: int, value: int, length: int, shift: int=0):
        data: int = self._read(reg_addr)[0]
        val: int = int('1' * length, 2) << shift
        data &= ~val  # data && inverse val = bit value (0, 1)
        data |= val & value << shift  # data || (val && value) << shift
        self._write(reg_addr, data)

    def _measurement(self):
        # Read all data at once. The data bytes are at 0xF7:0xFC (6 bytes)
        data: list = self._read(PRES.MSB, size=6)
        # Converting function. Bit shifts three values to one (20-bit value)
        convert: function = lambda msb, lsb, xlsb: (
            (msb << 12) + (lsb << 4) + (xlsb >> 4))
        self.rawP, self.rawT = convert(*data[:3]), convert(*data[3:])

        self.fineT = (
            (self.rawT / 2.0**14.0 - self.tC[0] / 2.0**10.0)
            * self.tC[1]
            + ((self.rawT / 2.0**17.0 - self.tC[0] / 2.0**13.0)**2.0)
            * self.tC[2]
        )

    def _temperature(self) -> float:
        return self.fineT / ((2.0**9.0) * 10.0)
    
    def _pressure(self) -> float:
        var1 = ((1.0 + (self.pC[2] * (self.fineT / 2.0 - 64e3)**2.0 
               / 2.0**19.0 + self.pC[1] * (self.fineT / 2.0 - 64e3))
               / 2.0**19.0 / 2.0**15.0) * self.pC[0])
        var2 = (((((self.fineT / 2.0 - 64e3)**2.0 * self.pC[5] / 2.0**15.0)
               + (self.fineT / 2.0 - 64e3) * self.pC[4] * 2.0) / 4.0)
               + (self.pC[3] * 2.0**16.0))

        try:
            p = (((2.0**20.0 - self.rawP) - (var2 / 2.0**12.0))
                * (5.0**4.0)*10.0 / var1)
            var1 = self.pC[8] * p**2.0 / 2.0**31.0
            var2 = p * self.pC[7] / 2.0**15.0
            p = p + (var1 + var2 + self.pC[6]) / 2.0**4.0
            return p
        except:
            return 0.0

    def _compensation(self, compensate: dict) -> list:
        return [
            unpack(comp[0], self._read(*comp[1:]))[0]
            for comp in compensate
        ]

    def reset(self):
        self._write(REG.RESET, 0xB6)

    def print_compensation(self):
        for pos, temp in enumerate(self.tC):
            print(f"T{pos+1}: {temp=}; {type(temp)=}")
        for pos, pres in enumerate(self.pC):
            print(f"P{pos+1}: {pres=}; {type(pres)=}")

    def status(self) -> tuple[bool, bool]:
        """Returns: tuple(updating, measuring)"""
        return tuple(
            self._read_bits(REG.STATUS, 1, shift=0),
            self._read_bits(REG.STATUS, 1, shift=3),
        )

    def chip_id(self) -> int:
        return self._read(REG.IDENTIFICATION, size=2)

    def fetch(self, temp: bool=True, pres: bool=True) -> tuple[int|None]:
        self._measurement()
        if temp and pres:
            return self._temperature(), self._pressure()
        elif not temp and pres:
            return self._pressure()
        elif temp and not pres:
            return self._temperature()
        else:
            return None

    @property
    def standby(self) -> int:
        return self._read_bits(REG.CONFIG, 3, shift=5)

    @standby.setter
    def standby(self, time: int) -> None:
        assert 0x00 <= time <= 0x07
        self._write_bits(REG.CONFIG, time, 3, shift=5)

    @property
    def iir(self) -> int:
        return self._read_bits(REG.CONFIG, 3, shift=2)

    @iir.setter
    def iir(self, mode: int) -> None:
        assert 0x00 <= mode <= 0x04
        self._write_bits(REG.CONFIG, mode, 3, shift=2)

    @property
    def spi(self) -> int:
        return self._read_bits(REG.CONFIG, 1, shift=0)

    @spi.setter
    def spi(self, state: bool) -> None:
        assert type(state) == bool
        self._write_bits(REG.CONFIG, int(state), 1, shift=0)

    @property
    def oversampling(self) -> list[int, int]:
        """returns: list[temp, pres]"""
        return [
            self._read_bits(REG.CTRL_MEAS, 3, shift=5),
            self._read_bits(REG.CTRL_MEAS, 3, shift=2),
        ]

    @oversampling.setter
    def oversampling(self, temp_pres: tuple) -> None:
        assert 0x00 <= temp_pres[0] <= 0x05 and 0x00 <= temp_pres[1] <= 0x05
        self._write_bits(REG.CTRL_MEAS, temp_pres[0], 3, shift=2)
        self._write_bits(REG.CTRL_MEAS, temp_pres[1], 3, shift=5)

    @property
    def power(self) -> int:
        return self._read_bits(REG.CTRL_MEAS, 2, shift=0)
    
    @power.setter
    def power(self, mode: int) -> None:
        assert 0x00 <= mode <= 0x03
        self._write_bits(REG.CTRL_MEAS, mode, 2, shift=0)
