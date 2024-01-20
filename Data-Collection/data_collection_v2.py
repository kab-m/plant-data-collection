"""
Data Collection Script

This script collects sensor data from various environmental sensors and logs it to a CSV file for AI training.

Author: Tommaso Bacci
"""

import time
import csv
import datetime
import sensors
from utils import printlog

# Global variables
csv_filename = "plant_data.csv"
headers = ["plant_order", "plant_family", "plant_subfamily", "plant_genus", "day", "time",
           "soil_moisture_percent", "lux", "temperature", "humidity", "was_watered", "ml", "environment", "plant_id"] 
sensor_manager = sensors.SensorManager()

# Constants
MAX_RETRY = 3
RETRY_WAIT = 3

# Plant information
plant_order = "Alismatales"
plant_family = "Araceae"
plant_subfamily = "Monsteroideae"
plant_genus = "Spathiphylleae"
enivronment = "indoor"
plant_1_id = "peace-lily-1"
plant_2_id = "peace-lily-2"



def package_data():
    try:
        global headers, enivronment, plant_1_id, plant_2_id

        # Date and time
        now = datetime.datetime.now()
        reading_day = now.strftime("%Y-%m-%d")
        reading_time = now.strftime("%H:%M:%S")

        # Common Sensor Readings
        lux = sensor_manager.get_light_reading()
        humidity, temperature = sensor_manager.get_air_reading()
        last_soil_moisture_reading = sensor_manager.last_soil_moisture_reading
        
        # Individual Soil Moisture Readings + watering
        soil_moisture_percent_1, was_watered, ml = sensor_manager.get_soil_reading(plant_1_id)
        soil_moisture_percent_2 = sensor_manager.get_soil_reading(plant_2_id)
        printlog("\nPackaging Data...")
        
        # Return Data
        values_1 = [plant_order, plant_family, plant_subfamily, plant_genus, reading_day, reading_time, 
                soil_moisture_percent_1, lux, temperature, humidity, was_watered, ml, enivronment, plant_1_id]
        values_2 = [plant_order, plant_family, plant_subfamily, plant_genus, reading_day, reading_time, 
                soil_moisture_percent_2, lux, temperature, humidity, was_watered, ml, enivronment, plant_2_id]
        printlog("Packing OK!")
        return dict(zip(headers, values_1)), dict(zip(headers, values_2))

    except Exception as e:
        printlog(f"Error reading sensors: {e}")
        return None, None


def log_data(data):
    printlog(f"\nLogging Data...")
    try:
        global headers
        # open csv
        with open(csv_filename, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            # If file empty add headers
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
        printlog("Logging OK!")
    except Exception as e:
        printlog(f"Error logging data: {e}")


def sleep_until_next_interval(interval_minutes):
    current_time = datetime.datetime.now()
    # calculate second to next interval xx:00 or xx:30
    minutes_to_next_interval = interval_minutes - (current_time.minute % interval_minutes)
    seconds_to_next_interval = (60 - current_time.second) + (minutes_to_next_interval - 1) * 60
    # Sleep until
    print(f"\nNext interval in {seconds_to_next_interval} seconds")
    time.sleep(seconds_to_next_interval)


if __name__ == "__main__":
    # get last water levels
    last_level = float(input("Last water moisture level (plant 1) ? "))
    sensor_manager.last_soil_moisture_1_reading = last_level
    last_level = float(input("Last water moisture level (plant 2) ? "))
    sensor_manager.last_soil_moisture_2_reading = last_level

    # start program
    while True:
        #get time and date
        now = datetime.datetime.now()
        day_now = now.strftime("%d/%m/%Y")
        time_now = now.strftime("%H:%M:%S")
        printlog(f"\n########## Date: {day_now} Time: {time_now}")
        try:
            #pack and log data to csv
            data_1, data_2 = package_data()
            if data_1 and data_2 is not None:
                log_data(data_1)
                log_data(data_2)
            # set and sleep to next interval
            sleep_until_next_interval(30)
        except KeyboardInterrupt:
            break
