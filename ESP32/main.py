# Standard micropython libraries
import time
import ntptime
import gc
import json
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
# Find the server closest to you:
# https://www.ntppool.org/zone/@
ntptime.host = "2.nl.pool.ntp.org"

# MQTT Settings
#   Enter the desired settings here.
#   More information of the settings?
#   See mqtt/connector.py
MQTT: dict = dict(
    client_id=b'ESP32_TEST',  # ID of this device
    server=b'192.168.0.103',  # Server IP address
    port=1883,
    ssl=False,
    ssl_params=None,
)
MQTT_TOPIC: str = b'ESP32'
MQTT_QOS: int = 1
MQTT_RETAIN: bool = True


def callback(topic, status) -> None:
    print(f"{topic=}, {status=}")


def convert_to_json(time: str,
                    measurements: list,
                    debug: bool = False) -> str:
    sensors: list = [
        [pos, meas]
        for pos, meas in zip(['A1', 'A2', 'B1', 'B2'], measurements)
    ]
    string: str = json.dumps(
        {
            'time': " ".join([
                f"{time[0]}-{time[1]:02d}-{time[2]:02d}",
                f"{time[3] + 2:02d}:{time[4]:02d}:{time[5]:02d}"
            ]),
            'measurements': {
                f'{pos}': vals
                for pos, vals in sensors
            }
        },
        separators=(',', ':'),
    )
    if debug:
        print(string)

    return string


def main(debug: bool = False):
    # Setting up the BMP280 sensors
    i2c = Settings(esp32=ESP32, i2c1=I2C1, i2c2=I2C2, timer_period=TIMER)
    sensor: list[BMP280] = i2c.settings()
    i2c.bmp280_setup(
        sensor,
        power=S().powerMode(2),
        iir=S().iirMode(3),
        spi=False,
        os=S().osMode(2, 4),
    )
    if debug:
        print('DEBUG IS ON\n', i2c)

    # Get data object (contains BMP280 and SoftI2C objects)
    data: object = Data(sensor, period=500)

    # Setting up uMQTT robust
    mqtt: object = Connector(**MQTT)
    mqtt.set_callback_status(callback)
    # If the current MQTT session is still active on the broker
    if not mqtt.connect(clean_session=False):
        print('Setting up new session...')
        mqtt.publish(b'ESP32', f'Connecting...', retain=True, qos=1)

    gc.enable()  # Enable garbage collection
    ntptime.settime()  # Set the local time according to `ntptime.host`
    while True:
        # Get measurement data from all the sensors
        measurement: list = data.get()
        # Make sure MQTT is still connected to the broker
        if mqtt.is_conn_issue():
            while mqtt.is_conn_issue():
                mqtt.reconnect()
            else:
                mqtt.resubscribe()

        # Publish measurements
        mqtt.publish(
            MQTT_TOPIC,
            bytes(convert_to_json(
                time.localtime(), measurement, debug=debug), 'utf-8'),
            retain=MQTT_RETAIN,
            qos=MQTT_QOS,
        )
        # Check if message has arrived. This is to ensure the memory does
        # not overload. Overload of memory only applies to QoS 1
        mqtt.check_msg()


if __name__ == '__main__':
    main(debug=ESP32["DEBUG"])
