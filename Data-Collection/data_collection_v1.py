"""
Data Collection Script

This script collects sensor data from various environmental sensors and logs it to a CSV file for AI training.

Author: Tommaso Bacci
"""

import time
import board
import digitalio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_dht
import adafruit_bh1750
import csv
import json
import datetime
import schedule
import busio

# Global variables
csv_filename = "plant_data.csv"
headers = ["plant_order", "plant_family", "plant_subfamily", "plant_genus", "day", "time",
           "soil_moisture_percent", "lux", "temperature", "humidity", "was_watered"]
dht = adafruit_dht.DHT11(12)
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
soil_moisture_chan = AnalogIn(ads, ADS.P0)
light_sensor = adafruit_bh1750.BH1750(i2c)
last_soil_moisture_reading = 0.0

# Constants
MAX_RETRY = 3
RETRY_WAIT = 3

# Plant information
plant_order = "Alismatales"
plant_family = "Araceae"
plant_subfamily = "Monsteroideae"
plant_genus = "Spathiphylleae"


def get_soil_reading():
    print("\nReading Soil...")
    for _ in range(MAX_RETRY):
        try:
            # Load calibration data from JSON
            with open('calibration_data.json', 'r') as cal_file:
                calibration_data = json.load(cal_file)
            # Slight mix up in assigniment but works
            min_soil_moisture = calibration_data["max_value"]
            max_soil_moisture = calibration_data["min_value"]
            # Calculate soil percentage
            soil_moisture_percent = ((soil_moisture_chan.voltage - min_soil_moisture) / (
                        max_soil_moisture - min_soil_moisture)) * 100
            # Correct for scale
            if soil_moisture_percent >= 100:
                soil_moisture_percent = 100.0
            elif soil_moisture_percent <= 0:
                soil_moisture_percent = 0
            # Return
            print("Soil OK!")
            return round(soil_moisture_percent, 2)            
        except RuntimeError as e:
            print(f"Error reading Soil sensor: {e}")
            time.sleep(RETRY_WAIT)  
    return None


def get_light_reading():
    print("\nReading Light...")
    for _ in range(MAX_RETRY):
        try:
            lux = light_sensor.lux
            print("Light OK!")
            return round(lux, 2)
        except RuntimeError as e:
            print(f"Error reading Light sensor: {e}")
            time.sleep(RETRY_WAIT)  
    return None  


def get_air_reading():
    print("\nReading Air...")
    for _ in range(MAX_RETRY):
            try:
                humidity = dht.humidity
                temperature = dht.temperature
                print("Air OK!")
                return humidity, temperature
            except RuntimeError as e:
                print(f"Error reading DHT sensor: {e}")
                time.sleep(RETRY_WAIT)  # Wait before the next attempt
    return None  # If not within 3 tries


def package_data():
    print("\nPackaging Data...")
    try:
        # Sensor Readings
        soil_moisture_percent = get_soil_reading()
        lux = get_light_reading()
        humidity, temperature = get_air_reading()
        global last_soil_moisture_reading
        global headers
        # Date and time
        now = datetime.datetime.now()
        reading_day = now.strftime("%Y-%m-%d")
        reading_time = now.strftime("%H:%M:%S")
        # Calculate was_watered
        was_watered = 1 if soil_moisture_percent > last_soil_moisture_reading + 5 else 0
        last_soil_moisture_reading = soil_moisture_percent
        # Return Data
        values = [plant_order, plant_family, plant_subfamily, plant_genus, reading_day, reading_time, 
                soil_moisture_percent, lux, temperature, humidity, was_watered]
        print("Packing OK!")
        return dict(zip(headers, values))

    except Exception as e:
        print(f"Error reading sensors: {e}")
        return None


def log_data(data):
    now = datetime.datetime.now()
    day = now.strftime("%d/%m/%Y")
    time = now.strftime("%H:%M:%S")
    print(f"\nLogging Data...\nDate: {day}\nTime: {time}")
    try:
        global headers
        # open csv
        with open(csv_filename, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            # If file empty add headers
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
        print("Logging OK!")
    except Exception as e:
        print(f"Error logging data: {e}")


def sleep_until_next_interval(interval_minutes):
    current_time = datetime.datetime.now()
    # calculate second to next interval xx:00 or xx:30
    minutes_to_next_interval = interval_minutes - (current_time.minute % interval_minutes)
    seconds_to_next_interval = (60 - current_time.second) + (minutes_to_next_interval - 1) * 60
    # Sleep until
    print(f"\nNext interval in {seconds_to_next_interval} seconds")
    time.sleep(seconds_to_next_interval)


if __name__ == "__main__":
    while True:
        try:
            data = package_data()
            if data is not None:
                log_data(data)
            sleep_until_next_interval(30)
        except KeyboardInterrupt:
            break
