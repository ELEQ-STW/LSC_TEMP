SSID: str = ''
PASSWORD: str = ''

# Check if the variables are empty
if (SSID, PASSWORD) == ('', ''):
    raise ValueError(
        "The SSID and PASSWORD for the WiFi-connectors are empty.\n\
        Please check the settings.py file in ESP32/wireless/"
    )