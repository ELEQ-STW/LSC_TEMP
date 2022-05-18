SETTINGS: dict = dict(
    FREQ=int(80e6)  # Frequency (in Hz) of the ESP32 device.
)

INTERNET: dict = dict(
    SSID='ELEQ-DATA',
    PASSWORD='2kQxfrXd',
)

I2C1: dict = dict(
    SDA=18,         # Data pin for I2C Communication
    SCL=19,         # Clock pin for I2C Communication
    CLK=4e5,        # Frequency in Hz (Communication speed)
)

I2C2: dict = dict(
    SDA=22,
    SCL=23,
    CLK=4e5,
)
