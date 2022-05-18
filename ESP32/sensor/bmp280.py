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
            period=0.1,
            mode=Timer.ONE_SHOT,
            callback=self._rw_limiter
        )

    def _rw_limiter(self, *args):
        self.limiter = True

    def _read(self, reg_addr: int, size: int=1) -> ...:
        while self.limiter is not True:
            pass
        self._rw_limiter_init()
        # test = self._i2c.readfrom_mem(self._addr, reg_addr, size)
        # print(f"{type(test)=}")
        # return test
        return self._i2c.readfrom_mem(self._addr, reg_addr, size)

    def _read_bits(self, reg_addr: int, length: int, shift: int=0) -> int:
        return self._read(reg_addr)[0] >> shift & int('1' * length, 2)

    def _write(self, reg_addr: int, data: bytearray):
        if not type(data) == bytearray:
            data = bytearray([data])
        while self.limiter is not True:
            pass
        self._rw_limiter_init()
        # test = self._i2c.writeto_mem(self._addr, reg_addr, data)
        # print(f"{type(test)=}; {test=}")
        # return test
        return self._i2c.writeto_mem(self._addr, reg_addr, data)

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
            (msb << 12) + (lsb << 4) + (xlsb >> 4)
        )
        self.rawP, self.rawT = convert(*data[:3]), convert(*data[3:])
        self.fineT = (((
            ((self.rawT >> 3) - (self.tC[0] << 1))
            * self.tC[1]) >> 11)
            + ((((((self.rawT >> 4) - self.tC[0])
            * ((self.rawT >> 4) - self.tC[0])) >> 12)
            * self.tC[2]) >> 14))

    def _compensation(self, compensate: dict) -> list:
        return [
            unpack(comp[0], self._read(*comp[1:]))
            for comp in compensate.values()
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

    @property
    def fetch_temp(self) -> int:
        self._measurement()
        return ((self.fineT * 5 + 128) >> 8) / 100.0

    @property
    def fetch_pres(self) -> int:
        self._measurement()
        var1 = self.fineT - 128e3
        var2 = (var1**2 * self.pC[5]) + ((var1 * self.pC[4]) << 17)
        var2 += self.pC[3] << 35
        var1 = ((var1**2.0 * self.pC[2]) >> 8) + ((var1 * self.pC[1]) << 12)
        var1 = (((1 << 47) + var1) * self.pC[0]) >> 33

        # Try Except needed to catch a possible div 0 error.
        try:
            p = int(((((2.0**20 - self.rawP) << 31) - var2) * 5.0**5) / var1)
            var1 = (self.pC[8] * (p >> 13)**2.0) >> 25
            var2 = (self.pC[7] * p) >> 19
            p = ((p + var1 + var2) >> 8) + (self.pC[6] << 4)
            return float(p / 2**8)
        except:
            return 0

    @property
    def standby(self) -> int:
        return self._read_bits(REG.CONFIG, 3, shift=5)

    @standby.setter
    def standby(self, time: int) -> None:
        assert 0x00 < time < 0x07
        self._write_bits(REG.CONFIG, time, 3, shift=5)

    @property
    def iir(self) -> int:
        return self._read_bits(REG.CONFIG, 3, shift=2)

    @iir.setter
    def iir(self, mode: int) -> None:
        assert 0x00 < mode < 0x04
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
        assert 0x00 < temp_pres[0] < 0x05 and 0x00 < temp_pres[1] < 0x05
        self._write_bits(REG.CTRL_MEAS, temp_pres[0], 3, shift=2)
        self._write_bits(REG.CTRL_MEAS, temp_pres[1], 3, shift=5)

    @property
    def power(self) -> int:
        return self._read_bits(REG.CTRL_MEAS, 2, shift=0)
    
    @power.setter
    def power(self, mode: int) -> None:
        assert 0x00 < mode < 0x03
        self._write_bits(REG.CTRL_MEAS, mode, 2, shift=0)
