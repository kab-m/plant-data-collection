import time
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_dht
import adafruit_bh1750
import json
import busio
from utils import printlog


class SoilMoistureSensor:
    def __init__(self, ads, channel, plant_id, filename):
        self.soil_moisture_chan = AnalogIn(ads, channel)
        self.plant_id = plant_id
        self.last_soil_moisture_reading = 0.0
        self.calibration_data = filename
        self.MAX_RETRY = 3
        self.RETRY_WAIT = 3

    def get_soil_reading(self):

        for _ in range(self.MAX_RETRY):
            try:
        
        # set calibrated values
                with open(self.calibration_data, 'r') as cal_file:
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

                # Return new soil moisture, was_watered, and ml
                was_watered = 1 if soil_moisture_percent > self.last_soil_moisture_reading + 5 else 0
                ml = 1000 if was_watered == 1 else 0

                return round(soil_moisture_percent, 2), was_watered, ml
            
            except RuntimeError as e:
                printlog(f"Error reading Soil sensor: {e}")
                print("Retrying...")
                time.sleep(self.RETRY_WAIT)
        printlog(f"!!! Impossible to retreive Soil Moisture !!!")
        return None, None, None


class SensorManager:
    def __init__(self):
        # Initialize sensors and other properties
        self.dht = adafruit_dht.DHT11(12)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.soil_sensors = [
            SoilMoistureSensor(self.ads, ADS.P0, "peace-lily-1", 'calibration_data_1.json'),
            SoilMoistureSensor(self.ads, ADS.P1, "peace-lily-2", 'calibration_data_2.json')
        ]
        self.light_sensor = adafruit_bh1750.BH1750(self.i2c)
        self.MAX_RETRY = 3
        self.RETRY_WAIT = 3


    def get_soil_readings(self):
        soil_data = []
        
        printlog("\nReading Soils...")
        for soil_sensor in self.soil_sensors:
            # read both sensors and return array [[s1_soil%, s1_watered, s1_ml], [s2_soil%, s2_watered, s2_ml]]
            soil_data.append(soil_sensor.get_soil_reading()) 
        
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

