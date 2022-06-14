# LS Charge Data Collection
## Table of Content
1. [About](#about)
2. [Used Components](#used-components)
    1. [Components ESP32](#components-esp32)
3. [Setup Guide](#setup-guide)
    1. [Preparation](#preparation)
    2. [ESP32](#esp32)
        1. [Flashing and Setup](#flashing-and-setup)
        2. [More Settings](#more-settings)
4. [Revision History](#revision-history)

## About
The LS Charge project is focussing on implementing EV-Chargers into light poles.
ELEQ does not have sufficient data to say with certainty that the power flowing through the light poles will influence the internal temperature of the light pole.

The LSC_TEMP project will tackle this by monitoring the internal temperature of the light pole using ESP32s.
These microcontrollers report back to the Raspberry Pi via the MQTT protocol.
All data can be read out via the LSC_TEMP website that is hosted on the Raspberry Pi.

## Used Components
### Components ESP32
The table below is for one setup. If multiple are needed, multiply these values with the desired quantity.
| Name                               | Function        | Amount | Comments                                                                                       |
| :----------------------------------| :-------------: | :----: | :--------------------------------------------------------------------------------------------- |
| [ESP32-DevKitCVE][ESP32-LINK1]     | Microcontroller | 1      | This is the microcontroller used in this project. <br> Has an on-board WiFi antenna and supports an external antenna as well. |
| [BMP280][ESP32-LINK2]              | Sensor          | 4      | Temperature and Pressure sensor. <br> Communicates via the I2C or SPI communication protocol.  |
| [IPEX to SMA Adapter][ESP32-LINK3] | Antenna Adapter | 1      | SMA Female to IPEX MHF1 Female Coax adapter cable. <br> **50 Ohms**, *100 millimeters*.        |
| [SMA Extension Cable][ESP32-LINK4] | Extension Cable | 1      | Extension cable for the antenna. SMA Male to SMA Female. <br> **50 Ohms**, *5000 millimeters*. |
| [5V Power Supply][ESP32-LINK5]     | DIN-Rail PSU    | 1      | Used for supplying power to the ESP32. <br> Max output: *5V*, *2.4A* -> **12W**                |
| [IP67 Antenna][ESP32-LINK6]        | Antenna         | 1      | Antenna for the ESP32. Can be used outside. <br> **50 Ohms**.                                  |
| [Jumper Cables][ESP32-LINK7]       | I2C Wires       | 1      | Wires for the connection between the ESP32 and the BMP280 sensors.                             |


## Setup Guide
This setup guide will explain the setup procedure of the ESP32 microcontrollers and the Raspberry Pi.
### Preparation
Make sure you have the following points done:

- Installed [Python 3.10](https://www.python.org/downloads/) or newer.
- Have access to a Command Line Interface.
    - An IDE (like [Visual Studio Code](https://code.visualstudio.com/)) is preferable but [CMD](https://en.wikipedia.org/wiki/Cmd.exe) can also be used.
- Cloned the [Github library](https://docs.github.com/en/enterprise-server@3.5/repositories/creating-and-managing-repositories/cloning-a-repository) to the PC.
### ESP32
Before you start with the setup, make sure you have all the components mentioned in [Components ESP32](#components-esp32).
#### Flashing and Setup
The ESP32 can be flashed and set up with the `install.bat` tool. This script is specifically written to automate the flashing and setup process.

Before the files can be uploaded to the ESP32, make sure that the WLAN configuration settings are filled in. This is done by editing the [settings.py][ESPTOOL] file:

``` Python
SSID: str = ''  # <- ADD SSID OF THE DESIRED NETWORK HERE
PASSWORD: str = ''  # <- PASSWORD OF THE DESIRED NETWORK

# NOTE: The SSID and PASSWORD need to be in parenthesis.
#       If there is a parenthesis in the PASSWORD,
#       please escape it by adding a '\' in front of the parenthesis.

# Check if the variables are empty
if (SSID, PASSWORD) == ('', ''):
    raise ValueError(
        "The SSID and PASSWORD for the WiFi-connectors are empty.\n\
        Please check the settings.py file in ESP32/wireless/"
    )
```

Save the changes you just made to the file.
Next, plug in the ESP32 and find the corresponding COM-port.
You can find it at: `Device Manager` -> `Ports (COM & LPT)`

When the COM-port is found, enter the following line in your preferred CLI:
``` Shell
.\install --port COMx --flash --setup
```
_Make sure that you are in the same directory as the `install.bat` file. You can make sure by copying the full directory path and enter it in the cli. Command: `cd 'full directory path'`._

The script should install the Micropython binaries and put the local files in the filesystem.

_The script uses the Python packages [adafruit-ampy][AMPY] and [esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32/). Click on the links to see more information about the packages._

Before the ESP32 device can be used, the third-party libaries umqtt.simple2 and umqtt.robust2 need to be installed.
First of all, download and install the following tool: [PuTTY][PuTTY].
Connect to the ESP32 device using the PuTTY __Serial connection__ type. The __Serial line__ is the _COM_-port and __Speed__ is _115200 bits per second (baudrate)_.
After PuTTY connects to the ESP32 device, you should see the following characters `>>>`. Enter the following commands to install the packages:

```Python REPL
>>> import network
>>> wlan = network.WLAN(network.STA_IF) # Create the network object
>>> wlan.active(True) # Activate the network module. Should return 'True'
>>> wlan.connect('ENTER SSID HERE', 'ENTER PASSWORD HERE') # Connect to the specified network
>>> wlan.ifconfig() # Check if it is connected
>>> import upip # Micropython Package Installer
>>> upip.cleanup() # Remove possible problems
>>> upip.get_install_path() # Set the correct install path
>>> upip.install('micropython-umqtt.simple2') # Install umqtt.simple2 package
>>> upip.install('micropython-umqtt.robust2') # Install umqtt.robust2 package
```
If the above code did not result in errors, all necessary packages and files are installed on the ESP32 module. Now we can focus on the settings for the ESP32 device. These are discussed in the [next](#more-settings) chapter.

#### More Settings
In addition to the WiFi settings mentioned in the [previous chapter](#flashing-and-setup), you are also able to set different parameters for the complete system.
These settings can be found in the [main.py](/ESP32/main.py) file.

These settings are:

``` Python
ESP32: dict = dict(
    FREQ=80_000_000,  # Operating frequency of the ESP32 in Hz (default: 240MHz)
    DEBUG=True,  # Enable/Disable debug functions. These can be read out using PuTTY
)
I2C1: dict = dict(  # Settings for the first I2C bus
    sda=Pin(18),  # Physical ESP32 pin for the data line (I2C)
    scl=Pin(19),  # Physical ESP32 pin for the clock line (I2C)
    freq=100_000,  # Baudrate of the I2C bus (communcation speed in Hz)
)
I2C2: dict = dict(  # Settings for the second I2C bus
    sda=Pin(22),  # Physical ESP32 pin for the data line (I2C)
    scl=Pin(23),  # Physical ESP32 pin for the clock line (I2C)
    freq=100_000,  # Baudrate of the I2C bus (communication speed in Hz)
)
TIMER: int = 250  # Interval between measurements (in milliseconds) per BMP280 sensor.
MQTT: dict = dict(  # MQTT Settings
    client_id=b'',  # ID of the ESP32 device
    server=b'',  # IP address of the MQTT Broker
    port=1883,
    user=None,
    password=None,
    keepalive=5,
    ssl=False,
    ssl_params=None,
    socket_timeout=3,
    message_timeout=30,
)  # More information on these settings can be found in /ESP32/mqtt/connector.py
MQTT_TOPIC: str = b''  # Topic to publish to
MQTT_QOS: int = 1  # Quality of Service of the communication system
MQTT_RETAIN: bool = True  # Tell the broker to retain the last message or not.
                          # Can be used to debug quicker.
```

The ESP32 does not receive the updated code automatically.
The user has to upload the code. This can be done using the `install.bat` file. Simply write the following line: `.\install --port COMx --setup`.

There is also a quicker way.
``` Powershell
cd ./ESP32
ampy --port COMx --baud 115200 --delay 1 put main.py
```
_When inserting the new files, make sure the PuTTY program is not connected to the ESP32. Otherwise the install file (and ampy) cannot write files to the ESP32 device._


## Revision History

| Release Name | Date       | Pull Request | Type           | Stable             |
| :----------- | :--------: | :----------: | :------------: | :----------------: |
| v0.1.0       | 03-06-2022 | [#1][PR1]    | Pre-release    | :x:                |
| v1.0.0       | 14-06-2022 | [#2][PR2]    | Stable release | :heavy_check_mark: |

[ESP32-LINK1]: https://www.espressif.com/en/products/devkits/esp32-devkitc
[ESP32-LINK2]: https://www.bosch-sensortec.com/products/environmental-sensors/pressure-sensors/bmp280/
[ESP32-LINK3]: https://www.digikey.nl/nl/products/detail/cvilux-usa/DH-20G50016/13177485
[ESP32-LINK4]: https://www.allekabels.nl/sma-kabel/1326/1306109/sma-kabel.html
[ESP32-LINK5]: https://www.conrad.nl/nl/p/mean-well-hdr-15-5-din-rail-netvoeding-5-v-dc-2-4-a-12-w-1-x-1894091.html
[ESP32-LINK6]: https://www.digikey.nl/nl/products/detail/linx-technologies-inc/ANT-W63-WRT-SMA/15622872
[ESP32-LINK7]: https://www.conrad.nl/nl/p/renkforce-jkff403-jumper-kabel-arduino-banana-pi-raspberry-pi-40x-draadbrug-bus-40x-draadbrug-bus-30-00-cm-bont-2299845.html
[AMPY]: https://pypi.org/project/adafruit-ampy/
[ESPTOOL]:/ESP32/wireless/settings.py
[PuTTY]: https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html
[PR1]: https://github.com/DutchFakeTuber/LSC_TEMP/releases/tag/v0.1.0
[PR2]: https://github.com/DutchFakeTuber/LSC_TEMP/releases/tag/v1.0.0

