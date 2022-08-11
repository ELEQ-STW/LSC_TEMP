# Standard micropython libraries
import time
import ntptime
import gc
import json
import machine
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
TIMER: int = 250
# Select which buses to activate.
# Two sensors per bus are required to avoid errors.
BUS_A: bool = True
BUS_B: bool = False

buses: list = None
if BUS_A:
    buses: list = ['A1', 'A2']
if BUS_B:
    if isinstance(buses, list):
        buses += ['B1', 'B2']
    else:
        buses: list = ['B1', 'B2']
if not BUS_A and not BUS_B:
    raise ValueError('BUS_A and BUS_B are both set to False')


# Configure time by accessing this server
# Find the server closest to you:
# https://www.ntppool.org/zone/@
ntptime.host = "0.europe.pool.ntp.org"

# MQTT SSL settings. This can be set as True if the use of certificates is desired.
# Please see the README for more information.
MQTT_SSL: bool = False
if MQTT_SSL:
    with open('mqtt/certs/client.key', 'rb') as key:
        k: str = key.read()
    with open('mqtt/certs/client.crt', 'rb') as cert:
        c: str = cert.read()
    MQTT_SSL_DICT: dict = dict(key=k, cert=c)
else:
    MQTT_SSL_DICT: dict = None


# MQTT Settings
#   Enter the desired settings here.
#   More information of the settings?
#   See mqtt/connector.py
MQTT: dict = dict(
    client_id=b'',  # ID of this device
    server=b'',  # Server IP address
    port=1883,
    user=None,
    password=None,
    keepalive=60,
    ssl=MQTT_SSL,
    ssl_params=MQTT_SSL_DICT,
    socket_timeout=1,
    message_timeout=60,
)
MQTT_TOPIC: str = b''
MQTT_QOS: int = 0
MQTT_RETAIN: bool = True


def callback(pid, status) -> None:
    _status = ['Timeout', 'Successfully Delivered', 'Unknown PID']
    print(f"{pid=}, {status=} ({_status[status]})")


def convert_to_json(time: str,
                    measurements: list,
                    debug: bool = False) -> str:
    # Print date as YEAR-MONTH-DAY with always two decimals
    f_date: function = lambda y, m, d: f"{y}-{m:02d}-{d:02d}"
    # Print time as HH:MM:SS with always two decimals
    f_time: function = lambda h, m, s: f"{h:02d}:{m:02d}:{s:02d}"
    string: str = json.dumps(
        {
            'time': " ".join([f_date(*time[0:3]), f_time(*time[3:6])]),
            'measurements': measurements
        },
        separators=(',', ':'),
    )
    if debug:
        print(string)

    return string


def cet_cest_timezone():
    """
    This function determines which timezone the module is in.
    The module is used in the CET timezone, which has a normal
    and summer timezone value (+1 or +2 offset).
    """
    year = time.localtime()[0]
    HHMarch = time.mktime(
        (year, 3, (31-(int(5*year/4+4)) % 7), 1, 0, 0, 0, 0, 0))
    HHOctober = time.mktime(
        (year, 10, (31-(int(5*year/4+1)) % 7), 1, 0, 0, 0, 0, 0))
    now = time.time()
    if now < HHMarch:  # Before the last sunday of March
        cet = time.localtime(now+3600)
    elif now < HHOctober:  # Before the last sunday of October
        cet = time.localtime(now+7200)
    else:  # After the last day of October
        cet = time.localtime(now+3600)
    return cet


def main(debug: bool = False):
    # Setting up the BMP280 sensors
    i2c = Settings(esp32=ESP32, i2c1=I2C1, i2c2=I2C2, timer_period=TIMER)
    sensor: list[BMP280] = i2c.settings(BUS_A=BUS_A, BUS_B=BUS_B)
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
    data: object = Data(sensor, samples=10, period=1_000)

    # Setting up uMQTT robust
    mqtt: object = Connector(**MQTT)
    mqtt.set_callback_status(callback)
    # If the current MQTT session is still active on the broker
    if not mqtt.connect(clean_session=False):
        print('Setting up new session...')
        mqtt.publish(
            MQTT_TOPIC,
            bytes('Connecting...', 'utf-8'),
            retain=MQTT_RETAIN,
            qos=MQTT_QOS,
        )

    gc.enable()  # Enable garbage collection
    # Sometimes the ESP32 fails to connect to the ntp server.
    try:
        ntptime.settime()  # Set the local time according to `ntptime.host`
    except:  # If unsuccessful, reset device.
        machine.reset()

    while mqtt.is_keepalive():
        # Get measurement data from all the sensors
        measurement: dict = {
            f'{bus}': {'Temperature': val[0], 'Pressure': val[1]}
            for bus, val in zip(buses, data.get())
        }
        if debug:
            print(f'{mqtt.is_conn_issue()=}; {mqtt.is_keepalive()=}')

        # Publish measurements
        mqtt.publish(
            MQTT_TOPIC,
            bytes(convert_to_json(
                cet_cest_timezone(), measurement, debug=debug), 'utf-8'),
            retain=MQTT_RETAIN,
            qos=MQTT_QOS,
        )
        try:
            # Check if message has arrived. This is to ensure the memory does
            # not overload. Overload of memory only applies to QoS 1
            mqtt.check_msg()
        except AttributeError as e:
            # If the Broker could not be reached during startup.
            raise AttributeError(f"Broker could not be reached.\n{e}")
            # machine.reset() # Uncomment this line if a reset is desired.
        mqtt.send_queue()

    print("Connection with broker has been lost, rebooting device...")
    machine.reset()


if __name__ == '__main__':
    main(debug=ESP32["DEBUG"])
