# LS Charge Data Collection
## Table of Content
1. [About](#about)
2. [Components Used](#components-used)
    1. [Components ESP32](#components-esp32)
3. [Setup Guide](#setup-guide)
    1. [ESP32](#esp32)
        1. [Installing Packages](#installing-packages)
        2. [Flashing the ESP32](#flashing-the-esp32)
4. [Revision History](#revision-history)

## About
The LS Charge project is focussing on implementing EV-Chargers into light poles.
ELEQ does not have sufficient data to say with certainty that the power flowing through the light poles will influence the internal temperature of the light pole.

The LSC_TEMP project will tackle this by monitoring the internal temperature of the light pole using ESP32s.
These microcontrollers report back to the Raspberry Pi via the MQTT protocol.
All data can be read out via the LSC_TEMP website that is hosted on the Raspberry Pi.

## Components Used
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

[ESP32-LINK1]: (https://www.espressif.com/en/products/devkits/esp32-devkitc)
[ESP32-LINK2]: (https://www.bosch-sensortec.com/products/environmental-sensors/pressure-sensors/bmp280/)
[ESP32-LINK3]: (https://www.digikey.nl/nl/products/detail/cvilux-usa/DH-20G50016/13177485)
[ESP32-LINK4]: (https://www.allekabels.nl/sma-kabel/1326/1306109/sma-kabel.html)
[ESP32-LINK5]: (https://www.conrad.nl/nl/p/mean-well-hdr-15-5-din-rail-netvoeding-5-v-dc-2-4-a-12-w-1-x-1894091.html)
[ESP32-LINK6]: (https://www.digikey.nl/nl/products/detail/linx-technologies-inc/ANT-W63-WRT-SMA/15622872)
[ESP32-LINK7]: (https://www.conrad.nl/nl/p/renkforce-jkff403-jumper-kabel-arduino-banana-pi-raspberry-pi-40x-draadbrug-bus-40x-draadbrug-bus-30-00-cm-bont-2299845.html)

## Setup Guide
This setup guide will explain the setup procedure of the ESP32 microcontrollers and the Raspberry Pi.
### ESP32
Before you start with the setup, make sure you have all the components mentioned in [Components ESP32](#components-esp32).
#### Installing Packages
Before we can commission the ESP32's, we need to flash and upload some files.
We need Python packages that can do that for us.

First of all, make sure you have Python installed on your computer. It is advised to use Python 3.8 or newer.

The packages needed are: `esptool` and `adafruit-ampy`. We can install these packages by entering the following commands in a Command Line Interface (CLI):
```
py -m pip install esptool adafruit-ampy
```
If the packages are installed successfully, go to the next step.

#### Flashing the ESP32
The ESP32 cannot understand MicroPython out of the box. We need to flash it first.
The binary file is available in this folder. Connect the ESP32 to the computer via a USB to Micro USB cable.
Check the used COM-port via Device Manager and type in the following command in the CLI:
```
py -m esptool --port COMX erase_flash
py -m esptool --chip esp32 --port COMX --baud 460800 write_flash -z 0x1000 esp32-20220117-v1.18.bin
```
Make sure that you enter this command when the CLI is executed from the same folder as the binary file.

## Revision History

| Release Name | Date       | Pull Request | Type        | Stable |
| :----------- | :--------: | :----------: | :---:       | :----: |
| v0.0.1-alpha | 18-05-2022 | [#1][PR1]    | Pre-release | :x:    |

[PR1]: ()
