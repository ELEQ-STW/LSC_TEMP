# Standard micropython libraries
import time
import ntptime
import gc
from machine import Pin

# Local modules and variables
from helpers import Data
from helpers import Settings
from sensor import BMP280
from sensor import SETTINGS as S
from mqtt import Connector

# General settings for the ESP32
ESP32: dict = dict(
    FREQ=80_000_000,
    DEBUG=True  # Set this value to False if debug is not desired.
)

# I2C Settings:
#   sda:  Data Pin  -> Data communication line
#   scl:  Clock Pin -> Clock line
#   freq: Baudrate  -> Communication speed in Hz
I2C1: dict = dict(sda=Pin(18), scl=Pin(19), freq=100_000)
I2C2: dict = dict(sda=Pin(22), scl=Pin(23), freq=100_000)
# The timeout timer for the BMP280. This value is the least time in
# milliseconds between consecutive measurements on one BMP280 sensor.
TIMER: int = 50

# Configure time by accessing this server
ntptime.host = "0.nl.pool.ntp.org"

def callback(topic, status) -> None:
    print(f"{topic=}, {status=}")

def main(debug: bool=False):
    gc.enable()  # Enable garbage collection
    i2c = Settings(esp32=ESP32, i2c1=I2C1, i2c2=I2C2, timer_period=TIMER)
    sensor: list[BMP280] = i2c.settings()
    if debug: print('DEBUG IS ON\n', i2c)
    i2c.bmp280_setup(
        sensor,
        power=S().powerMode(2),
        iir=S().iirMode(3),
        spi=False,
        os=S().osMode(2, 4),
    )
    
    data: object = Data(sensor, period=500)

    mqtt = Connector(
        b'ESP32_TEST',
        b'10.10.3.39',
        port=1883,
        keepalive=30,
        message_timeout=60,
    )
    mqtt.set_callback_status(callback)
    mqtt.set_config(
        DEBUG=False,
        KEEP_QOS0=False,
        NO_QUEUE_DUPS=True,
        MSG_QUEUE_MAX=5,
        CONFIRM_QUEUE_MAX=10,
        RESUBSCRIBE=True,
    )
    if not mqtt.connect(clean_session=False):
        print('Setting up new session...')
        mqtt.publish(b'ESP32', f'Connecting...', retain=True, qos=1)

    ntptime.settime()
    while True:
        gc.collect()
        measurement = data.get()

        if mqtt.is_conn_issue():
            while mqtt.is_conn_issue(): mqtt.reconnect()
            else: mqtt.resubscribe()

        _time: function = lambda t: " ".join([
            f"{t[0]}-{t[1]:02d}-{t[2]:02d}",
            f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"
        ])
        print(_time(time.localtime()), measurement)

        mqtt.publish(
            b'ESP32',
            bytes(f"{measurement + [_time(time.localtime())]}", 'utf-8'),
            retain=True,
            qos=1,
        )
        mqtt.check_msg()

if __name__ == '__main__':
    main(debug=ESP32["DEBUG"])
