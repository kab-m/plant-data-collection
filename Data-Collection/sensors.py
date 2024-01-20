import time
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_dht
import adafruit_bh1750
import json
import busio
from utils import printlog


class SensorManager:
    def __init__(self):
        # Initialize sensors and other properties
        self.dht = adafruit_dht.DHT11(12)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.soil_moisture_1_chan = AnalogIn(self.ads, ADS.P0)
        # self.soil_moisture_2_chan = AnalogIn(self.ads, ADS.P0)
        self.light_sensor = adafruit_bh1750.BH1750(self.i2c)
        self.last_soil_moisture_1_reading = 0.0
        self.last_soil_moisture_2_reading = 0.0
        self.MAX_RETRY = 3
        self.RETRY_WAIT = 3


    def get_soil_reading(self, plant_id):
        
        printlog("\nReading Soil...")
        for _ in range(self.MAX_RETRY):
            try:
                # set calibrated values
                with open('calibration_data.json', 'r') as cal_file:
                    calibration_data = json.load(cal_file)

                min_soil_moisture = calibration_data["max_value"]
                max_soil_moisture = calibration_data["min_value"]

                # calculate percentage
                soil_moisture_percent = (
                    (self.soil_moisture_chan.voltage - min_soil_moisture) / (
                        max_soil_moisture - min_soil_moisture
                    )
                ) * 100

                # correct for occasional over or under scale
                if soil_moisture_percent >= 100:
                    soil_moisture_percent = 100.0
                elif soil_moisture_percent <= 0:
                    soil_moisture_percent = 0

                # return soil new soil moisture, was_watered and ml + update global variable 
                if plant_id == "peace-lily-1":
                    printlog(f"Soil plant 1 OK! {round(soil_moisture_percent, 2)}")
                    self.last_soil_moisture_1_reading = round(soil_moisture_percent, 2)

                    # set watered
                    was_watered = 1 if soil_moisture_percent > self.last_soil_moisture_1_reading + 5 else 0

                    # set ml
                    ml = 1000 if was_watered == 1 else 0
                    
                    # return plant 1 data
                    return self.last_soil_moisture_1_reading, was_watered, ml
                
                elif plant_id == "peace-lily-2":
                    printlog(f"Soil plant 2 OK! {round(soil_moisture_percent, 2)}")
                    self.last_soil_moisture_2_reading = round(soil_moisture_percent, 2)

                    # set watered
                    was_watered = 1 if soil_moisture_percent > self.last_soil_moisture_1_reading + 5 else 0

                    # set ml
                    ml = 1000 if was_watered == 1 else 0

                    # return plant 2 data
                    return self.last_soil_moisture_2_reading

            except RuntimeError as e:
                printlog(f"Error reading Soil sensor: {e}")
                print("Retrying...")
                time.sleep(self.RETRY_WAIT)
        printlog(f"!!! Impossible to retreive Soil Moisture !!!")
        return None


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

