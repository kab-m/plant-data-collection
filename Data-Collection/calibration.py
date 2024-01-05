"""
Data Collection Script

This script calibrates sensor soil moisture sensor individuating a maximum and minimum voltage reading and saving it to JSON.

Author: Tommaso Bacci
"""


import time
import json
import busio
import board
import digitalio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


def calibrate_soil_moisture():
    max_value = None
    min_value = None

    # Create the ADS object
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)

    # Create single-ended input on channel 0
    chan = AnalogIn(ads, ADS.P0)

    baseline_check = input("Is Soil Moisture Sensor Dry? (enter 'y' to proceed): ")

    if baseline_check == 'y':
        max_values = []
        for x in range(0, 10):
            print(f"detected: {chan.voltage}v")
            max_values.append(chan.voltage)
            time.sleep(0.5)
        max_value = round(max(max_values), 2)
        print(f"\nMax voltage value: {max_value}v\n")

    water_check = input("Is Soil Moisture Sensor in Water? (enter 'y' to proceed): ")

    if water_check == 'y':
        min_values = []
        for x in range(0, 10):
            print(f"detected: {chan.voltage}v")
            min_values.append(chan.voltage)
            time.sleep(0.5)
        min_value = round(min(min_values), 2)
        print(f"\nMin voltage value: {min_value}v\n")

    config_data = dict()
    config_data["min_value"] = min_value
    config_data["max_value"] = max_value

    with open('calibration_data.json', 'w') as outfile:
        json.dump(config_data, outfile)

    print('\n')
    print(config_data)


if __name__ == "__main__":
    calibrate_soil_moisture()
