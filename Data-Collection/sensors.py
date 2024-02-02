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
    

    def __init__(self, i2c, ads, plant_id, filename):
        self.i2c = i2c
        self.ads = ads
        self.filename = filename

        if plant_id == "peace-lily-1": 
            self.soil_moisture_chan = AnalogIn(self.ads, ADS.P0) 
        elif plant_id == "peace-lily-2":
            self.soil_moisture_chan = AnalogIn(self.ads, ADS.P1)

        self.plant_id = plant_id
        self.last_soil_moisture_reading = 0.0
        self.calibration_data = self.load_calibration_data()
        self.MAX_RETRY = 3
        self.RETRY_WAIT = 3
     

    def load_calibration_data(self):
        try:
            with open(self.filename, 'r') as cal_file:
                return json.load(cal_file)
        except FileNotFoundError:
            # Handle the case where the file doesn't exist
            return {"min_value": 0, "max_value": 100, "last_level": 0}
        


    def save_calibration_data(self):
        with open(self.filename, 'w') as cal_file:
            json.dump(self.calibration_data, cal_file)


    def update_last_level(self, new_level):
        self.calibration_data["last_level"] = new_level
        self.save_calibration_data()


    def get_soil_reading(self):

        for _ in range(self.MAX_RETRY):
            try:
                # Set calibrated data
                min_soil_moisture = self.calibration_data["max_value"]
                max_soil_moisture = self.calibration_data["min_value"]
                self.last_soil_moisture_reading = self.calibration_data["last_level"]
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

                self.update_last_level(round(soil_moisture_percent, 2))

                printlog(f"\n{self.plant_id}:\nSoil: {round(soil_moisture_percent, 2)}\nWatered: {was_watered}, {ml}")
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
