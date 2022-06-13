# Standard micropython libraries
from time import time_ns

# Local modules and variables
from sensor import BMP280  # Only used for typing


class Data:
    def __init__(self,
                 sensor: list[BMP280],
                 samples: int = None,
                 period: int = None
                 ) -> None:
        """
        # The Data class is used to fetch BMP280 sensor data.
        - ### arguments:
            - sensor: `list`. The function is using the BMP280 objects \
                directly to fetch temperature and pressure data from the \
                sensor. Make sure the objects (`SoftI2C` & `BMP280`) are \
                called and configured before using this class.
        - ### keyword arguments:
            - samples: `int`. Set the amount of sample points to be fetched. \
                The class will return the average of the fetched amount. \
                The timeout time can be configured during the initialization \
                of the `BMP280` object. See `timer_period` in `BMP280`.
            - period: `int`. Default: `None`. Set the time in milliseconds \
                to measure as much data as possible. This method can be used \
                instead of `samples`. The amount of data points fetched also \
                depends on the `timer_period` setting in `BMP280`. \
                It is recommended to increase the `timer_period` if the \
                `period` is set `1_000 < period`. \


        #### The amount of data points taken is capped at 50. This is to \
        limit the storage space taken by the data.

        #### Example::

            # Get 25 data points in approx. 25*`timer_period`.
            Data(list(BMP280), samples=25)  # 25 samples

            # Get `x` data points in approx. `period`/`timer_period`.
            Data(list(BMP280), period=1_000)  # 1 second

            # If both keyword arguments are used,
            # period will be overruled by samples.
            Data(list(BMP280), samples=25, period=1_000)
            # Is equal to:
            Data(list(BMP280), samples=25)
        """
        self._sum: function = lambda data, num: [
            sum(val[num][pos] for val in data)/len(data) for pos in [0, 1]
        ]
        self.sensor: list[BMP280] = sensor
        self.samples: int = samples
        self.period: int = period if samples is None else None
        self.processed: list = []

    def _fetch(self) -> None:
        """
        Fetch function.
        This function fetches the temperature and pressure data `x` \
            amount of times:
        - `sample` amount of times
        - As many times in `period`. Also depends on the delay between \
            measurements set in `BMP280`.
        """
        if isinstance(self.samples, int):
            if self.samples > 50:
                self.samples: int = 50
            self.data: list = [
                [s.fetch() for s in self.sensor]
                for _ in range(self.samples)
            ]
        else:
            self.data: list = []
            _time = time_ns()
            while time_ns() - _time <= self.period * 1e6:
                self.data.append([s.fetch() for s in self.sensor])
                if len(self.data) >= 50:
                    break

    def get(self) -> list:
        """
        Get function. This function fetches data using `self._fetch()` and \
        averages the measurement data before returning.

        Returns: `list[list]`.
        - Format: `BMP280[DATA[temperature, pressure]]`
            - temperature in \u00b0C
            - pressure in Pa. divide by `100` to get hPa.
        """
        self.processed: list = []  # Make list empty
        self._fetch()
        self.processed: list = [
            self._sum(self.data, num)
            for num in range(len(self.data[0]))
        ]
        del self.data  # Preserving space
        return self.processed

    def __str__(self) -> str:
        if self.processed == []:
            _ = self.get()
        return "\n".join([
            f"""{sensor._i2c} [{hex(sensor._addr)}]
            Temperature: {self.processed[num][0]:.2f}   \u00b0C
            Pressure:    {self.processed[num][1]/100.0:.2f} hPa
            """
            for num, sensor in enumerate(self.sensor)
        ])
