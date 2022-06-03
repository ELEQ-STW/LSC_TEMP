"""
This is the 'main' micropython file for the ESP32.
The code is constructed for the assignment 'Final Assignment IoT Fundamentals'.
This code is written by:

    Student Name:       Sybrand van Loenen,
    Student Number:     358541
    Student E-Mail:     s.van.loenen@st.hanze.nl
    Class Name:         IoT Fundamentals
    Assignment Name:    Final Assignment IoT Fundamentals
    Study Student:      Elektrotechniek major Electronica
    Code version:       v1.0
"""

from machine import Pin, I2C        #Import GPIO and I2C libriaries for communication to BME280.
import network                      #Import network library for connecting to the internet.
from umqtt.simple import MQTTClient #Import the MQTTClient for communicating with the Raspberry Pi over the internet.
import os, sys
from time import sleep, time              #Import sleep for the time delays in the program.

# - I M P O R T   E X T E R N A L   F I L E S -
from extraFiles import BME280       #Import the BME280 configuration file.

#Read the client key file [rb = read binary]
with open("./certs/client.key", "rb") as key:
    client_key = key.read()

#Read the client certificate file [rb = read binary]
with open("./certs/client.crt", "rb") as certificate:
    client_cert = certificate.read()

class BME_280():
    def __init__(self):
        self.scl = Pin(22) #GPIO22 ESP32
        self.sda = Pin(21) #GPIO21 ESP32
        self.frequency = 10000 #10kHz

    def BME280_fetchInfo(self):
        i2c = I2C(
            scl=self.scl,
            sda=self.sda,
            freq=self.frequency
            )
        bme = BME280.BME280(i2c=i2c) #Shortening the BME280 command
        temp = bme.temperature #Fetch 'temperature' from the BME280.py-file
        hum = bme.humidity #Fetch 'humidity' from the BME280.py-file
        pres = bme.pressure #Fetch 'pressure' from the BME280.py-file
        # print('Temperature: ', temp) #For testing purposes.
        # print('Humidity: ', hum)
        # print('Pressure: ', pres)
        #Filter only numbers (and decimal points) from string.
        newTemp = float("".join(filter(lambda d: str.isdigit(d) or d == '.', temp)))
        newHum = float("".join(filter(lambda d: str.isdigit(d) or d == '.', hum)))
        newPres = float("".join(filter(lambda d: str.isdigit(d) or d == '.', pres)))
        return newTemp, newHum, newPres
    
    def BME280_test(self):
        i2c = I2C(
            scl=self.scl,
            sda=self.sda,
            freq=self.frequency
            )
        bme = BME280.BME280(i2c=i2c)
        temp = bme.temperature
        print(temp)

class MQTT():
    def __init__(self):
        self.clientName = "ESP32" #Name of the publisher/subscriber
        self.topic = 'ESP32_BME280'
        self.server = "192.168.178.39" #IP-Address external broker
        self.port = 8883 #Port used. 1883 unsecure, 8883 secure
        self.user = None #Optional
        self.password = None #Optional
        self.ssl = True #Enable the use of SSL keys and certificates
    
    #For testing purposes
    def MQTT_clientNoCertificate(self):
        client = MQTTClient(
            self.clientName,
            self.server,
            port=8883,
            user=None,
            password=None,
            ssl=False
        )
        #Try and Except routine in case the broker rejects the ESP32
        try:
            client.connect()
            client.publish(
                b'%s'%self.topic,
                b'Hello from ESP32!'
            )
            print("Sent 'Hello from ESP32' to Raspberry Pi with Topic name: '%s'" %self.topic)
            client.disconnect()
        except OSError as E:
            print("An error occurred: " + str(E)) #Print the error.

    def MQTT_Client(self, key=client_key, cert=client_cert, BME280_Temperature=None, BME280_Humidity=None, BME280_Pressure=None):
        client = MQTTClient(
            self.clientName,
            self.server,
            port=self.port,
            user=self.user,
            password=self.password,
            ssl=self.ssl,
            ssl_params={'key': key, 'cert': cert}
            )
        client.connect()
        #If there are BME280 measurements, execute this
        if ((BME280_Temperature != None) and (BME280_Humidity != None) and (BME280_Pressure != None)):
            client.publish(
                b'%s' %self.topic,
                b"[%s, %s, %s]" %(BME280_Temperature, BME280_Humidity, BME280_Pressure)
                )
            client.disconnect()
        #If there are no BME280 measurement, execute this
        else:
            client.publish(
                b'%s' %self.topic,
                b"Hello from ESP32"
                )
            client.disconnect()

class internetConnection():
    def __init__(self):
        self.networkName = 'WIFIMonster' #Network name you want to connect to
        self.networkPassword = 'TingYang!2' #Password of the network

    def connectToWiFi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(self.networkName, self.networkPassword)
            while not wlan.isconnected():
                pass
        print('network config:', wlan.ifconfig())

def main():
    #Connect to the internet first:
    internetConnection().connectToWiFi()
    sleep(1)

    # MQTT().MQTT_clientNoCertificate() #For demonstrative purposes
    # MQTT().MQTT_Client() #Used for only connecting to the broker once

    #Used for sending BME280 to the broker/Raspberry Pi
    count = int(0)
    while(True):
        start_time = time()
        newTemp, newHum, newPres = BME_280().BME280_fetchInfo()
        sleep(1)
        MQTT().MQTT_Client(BME280_Temperature=newTemp, BME280_Humidity=newHum, BME280_Pressure=newPres)
        sleep(1)
        count = count + 1
        print("Loop time: %s seconds, Loop count: %s" %((time() - start_time), str(count)))

if __name__ == "__main__":
    main()
