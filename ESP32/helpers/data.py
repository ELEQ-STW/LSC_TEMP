# Standard micropython libraries
# None

# Local modules and variables
from sensor import BMP280  # Only used for typing

class Data:
    def __init__(self, sensor: list[BMP280], amount: int=15) -> None:
        """
        The Data class is used to fetch BMP280 sensor data.
        - arguments:
            - sensor: `list`. The function is using the BMP280 objects \
                directly to fetch temperature and pressure data from the \
                sensor. Make sure the objects (`SoftI2C` & `BMP280`) are \
                called and configured before using this class.
        - keyword arguments:
            - amount: `int`. Set the amount of data points to be fetched. \
                The class will return the average of the fetched amount. \
                The timeout time can be configured during the initialization \
                of the `BMP280` object. See `timer_period` in `BMP280`.
        """
        self._sum: function = lambda data, num: [
            sum(val[num][pos] for val in data)/len(data) for pos in [0, 1]
        ]
        self.sensor: list[BMP280] = sensor
        self.amount: int = amount
        self.processed: list = []
    
    def _fetch(self) -> None:
        """
        Fetch function.
        This function fetches the temperature and pressure data \
            `self.amount` of times.
        """
        self.data: list = [
            [s.fetch() for s in self.sensor]
            for _ in range(self.amount)
        ]
    
    def get(self) -> list:
        """
        Get function. This function fetches data using `self.fetch` and \
            averages the measurement data before returning.
        
        returns: `list[list]`.
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