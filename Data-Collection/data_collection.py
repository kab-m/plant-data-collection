"""
Data Collection Script

This script collects sensor data from various environmental sensors and logs it to a CSV file for AI training.

Author: Tommaso Bacci
"""

import time
import csv
import datetime
import sensor_manager
import logging

# Global variables
csv_filename_1 = "plant_data_1.csv"
csv_filename_2 = "plant_data_2.csv"
headers = ["plant_order", "plant_family", "plant_subfamily", "plant_genus", "day", "time",
           "soil_moisture_percent", "lux", "temperature", "humidity", "was_watered", "ml", "environment", "plant_id"] 
sensor_manager = sensor_manager.SensorManager()

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
        
        # Individual Soil Moisture Readings + watering
        sensors = sensor_manager.get_soil_readings()
        soil_moisture_percent_1, was_watered_1, ml_1 = sensors[0]
        soil_moisture_percent_2, was_watered_2, ml_2 = sensors[1]

        printlog("\nPackaging Data...")
        
        # Set Data
        values_1 = [plant_order, plant_family, plant_subfamily, plant_genus, reading_day, reading_time, 
                soil_moisture_percent_1, lux, temperature, humidity, was_watered_1, ml_1, enivronment, plant_1_id]
        values_2 = [plant_order, plant_family, plant_subfamily, plant_genus, reading_day, reading_time, 
                soil_moisture_percent_2, lux, temperature, humidity, was_watered_2, ml_2, enivronment, plant_2_id]
        # Return Data
        printlog("Packing OK!")
        return dict(zip(headers, values_1)), dict(zip(headers, values_2))

    except Exception as e:
        printlog(f"Error reading sensors: {e}")
        return None, None


def log_data(data, filename):
    printlog(f"\nLogging Data...")
    try:
        global headers
        # Open csv
        with open(filename, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            # If file empty add headers
            if file.tell() == 0:
                writer.writeheader()
            # Write file
            writer.writerow(data)
        printlog(f"Logging {filename} OK!")
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


def testHardware():
    sensor_manager.test()

if __name__ == "__main__":
    # Get last water levels
    # for x in range(2):
    #     last_level = float(input(f"Last water moisture level (plant {x+1}) ? "))
    #     sensor_manager.soil_sensors[x] = last_level

    # Start program
    while True:
        #Get time and date
        now = datetime.datetime.now()
        day_now = now.strftime("%d/%m/%Y")
        time_now = now.strftime("%H:%M:%S")
        printlog(f"\n########## Date: {day_now} Time: {time_now}")
        try:
            # Pack and log data to csv
            data_1, data_2 = package_data()
            if data_1 and data_2 is not None:
                log_data(data_1, csv_filename_1)
                log_data(data_2, csv_filename_2)
            # Set and sleep to next interval
            sleep_until_next_interval(30)
        except KeyboardInterrupt:
            break

        # try:
        #     testHardware()
        #     print("\nTEST PASSED\n")
        # except KeyboardInterrupt:
        #     print("quitting")
    
