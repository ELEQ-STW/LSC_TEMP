# Standard microPython libraries
import time
import ntptime
import gc
import json
from machine import Pin
from machine import reset as reset_device

# Local modules and variables
from helpers import Data
from helpers import Settings
from sensor import BMP280
from sensor import SETTINGS as S
from mqtt import Connector


CONFIG: dict = json.loads(open('setup.json', 'r').read())
ESP32: dict = CONFIG['ESP32']
I2C: dict = CONFIG['I2C']
SENSOR: dict = CONFIG['BMP280']
WIRELESS: dict = CONFIG['WIRELESS']
NTP: dict = CONFIG['NTP']
MQTT: dict = CONFIG['MQTT']
del CONFIG


def callback(pid: int, status: int) -> None:
    """MQTT Callback function.

    Args:
        pid (int): Is delivered by the MQTT module.
        status (int): Is delivered by the MQTT module.

    NOTE: The output is printed in the terminal and can be viewed using
    PuTTY or something similar.
    """
    _status: list = ['Timeout', 'Successfully Delivered', 'Unknown PID']
    print(f'{pid=}, {status=} ({_status[status]})')


def cet_tz(convert=NTP['COMPUTE_CET']):
    """
    Converting Coordinated Universal Time (UTC) to
    Central European (Summer) Time (CE(S)T).

    This method checks if the current datetime is between the
    last sunday of March and the last sunday of October.
    If true, add two hours to the GMT time.
    Else, add one hour.
    """
    now: time.time = time.time()
    if convert:
        year: int = time.localtime()[0]
        month: function = lambda month: time.mktime(
            (year, month, (31-(int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0, 0))
        if month(3) < now < month(10):
            cet: time.localtime = time.localtime(now + 2 * 60**2)
        else:
            cet: time.localtime = time.localtime(now + 60**2)
    else:
        cet: time.localtime = time.localtime(now)
    return cet[:6]  # Return without the weekday and yearday values


def jsonize(time: bool = False,
            message: list | str = None,
            debug: bool = ESP32['DEBUG']) -> str:
    """Converting data to JSON.

    Args:
        time (str): time.time() function.
        measurements (list): Measurements measured from the BMP280 modules
        ping (bool): Indication if the message is a 'ping'.
        debug (bool, optional): Defaults to CONFIG['ESP32']['DEBUG'].

    Returns:
        str: _description_
    """
    string: dict = {'message': 'Measurement' if time else message}
    if time:
        string['time'] = cet_tz(NTP['COMPUTE_CET'])
        string['measurements'] = message
    jsonString: str = json.dumps(string, separators=(',', ':'))
    if debug:
        print(jsonString)
    return jsonString


def setup() -> tuple[Data, Connector, list[str]]:
    """
    Setup function for initializing the ESP32.

    The function does the following:
    - Initialize the I2C bus(es)
    - Configuring the BMP280 sensor(s)
    - Connecting to the WiFi access point
    - Initializing MQTT (QoS 0 or 1)

    Returns:
        tuple[Data, Connector, list[str]]
    """
    # Setting up the BMP280 sensors
    BUS_A: bool = I2C['BUS_A'].pop('ACTIVE')
    BUS_B: bool = I2C['BUS_B'].pop('ACTIVE')
    assert any((BUS_A, BUS_B)), "No I2C bus active, \
        please check the setup.json file."
    bus: list = []
    if BUS_A:
        bus += ['A1', 'A2']
    if BUS_B:
        bus += ['B1', 'B2']

    buses: function = lambda bus: {
        k.lower(): v if k == 'FREQ' else Pin(v)
        for k, v in bus.items()
    }
    i2c = Settings(
        esp32=ESP32,
        i2c1=buses(I2C['BUS_A']),
        i2c2=buses(I2C['BUS_B']),
        timer_period=SENSOR['TIMER']
    )
    sensor: list[BMP280] = i2c.settings(
        BUS_A=BUS_A,
        BUS_B=BUS_B
    )
    i2c.bmp280_setup(
        sensor,
        # Dictionary unpacking
        **{k.lower(): list(v.values()) if k == 'OS' else v
           for k, v in SENSOR['SETUP'].items()}
    )

    # Try to connect to the WiFi network.
    # If the connection fails, reboot device.
    i2c.wireless(*list(WIRELESS.values()))

    if ESP32['DEBUG']:
        print('DEBUG IS ON\n', i2c)

    # Get data object (Contains BMP280 and SoftI2C objects)
    data: Data = Data(
        sensor,
        samples=SENSOR['SAMPLES'],
        period=SENSOR['PERIOD']
    )

    # Setting up uMQTT robust
    file: function = lambda path: (
        None if not path else open(path, 'rb').read())
    mqtt: Connector = Connector(
        MQTT['CLIENT_ID'],
        MQTT['SERVER'],
        port=MQTT['PORT'],
        user=MQTT['USER'],
        password=MQTT['PASSWORD'],
        keepalive=MQTT['KEEPALIVE'],
        ssl=MQTT['SSL'].pop('USE_SSL'),
        ssl_params={
            k.lower(): v if k not in ['KEY', 'CERT'] else file(v)
            for k, v in MQTT['SSL'].items()
        },
        socket_timeout=MQTT['SOCKET_TIMEOUT'],
        message_timeout=MQTT['MESSAGE_TIMEOUT']
    )
    mqtt.set_callback_status(callback)
    # If the current MQTT session is still active on the broker
    if not mqtt.connect(clean_session=False):
        if ESP32['DEBUG']:
            print('Setting up new session...')
        mqtt.publish(
            MQTT['TOPIC'],
            bytes(jsonize(message='Connecting...'), 'utf-8'),
            retain=MQTT['RETAIN'],
            qos=MQTT['QOS'],
        )

    # Set up a connection with the NTP server if desired.
    # If the connection fails, reset the device.
    if NTP['USE_NTP']:
        ntptime.host = NTP['ADDRESS']
        try:
            ntptime.settime()
        except:
            reset_device()

    # Enable garbage collection
    gc.enable()

    return data, mqtt, bus


def main(data: Data, mqtt: Connector, buses: list[str]) -> None:
    """
    Main function of the ESP32 measurement system.
    The function will, after the setup has been successfully executed,
    send messages (ping or measurements) to the MQTT broker. Repeat the
    process if the keepalive set in the setup.json file is maintained.
    The function automatically reboots if the connection with the broker
    is lost.

    Args:
        data (Data): Initialized object (returned by setup)
        mqtt (Connector): Initialized object (returned by setup)
        buses (list[str]): List with active sensors. Two for each bus (A, B)
    """
    timer: int = time.time_ns()
    counter: int = MQTT['SEND_MEASUREMENT'] // MQTT['SEND_KEEPALIVE']
    while mqtt.is_keepalive():
        send_message: bool = False
        # If it is time to measure
        if counter == 0:
            # Get measurement data from all the sensors
            message: dict = {
                f'{bus}': {'Temperature': val[0], 'Pressure': val[1]/100.0}
                for bus, val in zip(buses, data.get())
            }
            send_message: bool = True
            counter: int = MQTT['SEND_MEASUREMENT'] // MQTT['SEND_KEEPALIVE']

        # If it is ready to send a 'ping' to preserve keepalive
        elif ((time.time_ns() - timer) / 10**9) - MQTT['SEND_KEEPALIVE'] > 0:
            message: str = 'Ping'
            send_message: bool = True
            counter -= 1
            timer: int = time.time_ns()

        # Send message if available
        if send_message:
            message: bytes = bytes(
                jsonize(time=isinstance(message, dict), message=message),
                'utf-8'
            )
            mqtt.publish(MQTT['TOPIC'],
                         message,
                         retain=MQTT['RETAIN'],
                         qos=MQTT['QOS'])

        try:
            # Check if message has arrived. This is to ensure the memory
            # does not overload. Overload of memory only applies to QoS 1.
            if MQTT['QOS'] == 1:
                mqtt.check_msg()
            mqtt.send_queue()
        except AttributeError as e:
            # If a connection with the broker could not be established during startup.
            # raise AttributeError(f'Broker could not be reached.\n{e}')
            reset_device()

    if ESP32['DEBUG']:
        print("Connection with broker has been lost, rebooting device...")
        time.sleep(1)
    reset_device()


if __name__ == '__main__':
    data, mqtt, buses = setup()
    main(data, mqtt, buses)
