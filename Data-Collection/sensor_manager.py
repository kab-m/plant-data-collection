import time
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_dht
import adafruit_bh1750
import json
import busio
import logging


class SensorManager:


    def __init__(self):
        # Initialize sensors and other properties
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        self.ads = ADS.ADS1115(self.i2c)
        self.dht = adafruit_dht.DHT11(12)
        # print(f"(Sensors) Initialized i2c for sensors = {self.i2c}")
        self.soil_sensors = [
            SoilMoistureSensor(self.i2c, self.ads, "peace-lily-1", 'calibration_data_1.json'),
            SoilMoistureSensor(self.i2c, self.ads, "peace-lily-2", 'calibration_data_2.json')
        ]
        self.light_sensor = adafruit_bh1750.BH1750(self.i2c, address=0x23)
        self.MAX_RETRY = 3
        self.RETRY_WAIT = 3


    def get_soil_readings(self):
        soil_data = []

        printlog("\nReading Soils...")
        for sensor in self.soil_sensors:
            data = sensor.get_soil_reading()
            if data:
                soil_data.append(data)
        
        return soil_data

    
    def get_light_reading(self):

        printlog("\nReading Light...")
        for _ in range(self.MAX_RETRY):
            try:
                # read and return light value
                lux = self.light_sensor.lux
                printlog(f"Light OK! {round(lux, 2)}")
                return round(lux, 2)
            except RuntimeError as e:
                printlog(f"Error reading Light sensor: {e}")
                time.sleep(self.RETRY_WAIT)  
        return None  


    def get_air_reading(self):
        printlog("\nReading Air...")
        for _ in range(self.MAX_RETRY):
                try:
                    # read and return air values
                    humidity = self.dht.humidity
                    temperature = self.dht.temperature
                    printlog(f"Air OK! {humidity}%, {temperature}C")
                    return humidity, temperature
                except RuntimeError as e:
                    printlog(f"Error reading DHT sensor: {e}")
                    time.sleep(self.RETRY_WAIT) 
        return None  


    def test(self):
        print(f"Testing Hardware...\nGetting Air...")
        air = self.get_air_reading()
        print(f"Air = {air}\nGetting Light...")
        light = self.get_light_reading()
        print(f"Light = {light}\nGetting Soils")
        soils = self.get_soil_readings()
        print(f"Soils = {soils}")
