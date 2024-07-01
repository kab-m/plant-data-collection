# plant-data-collection
Author: kab-m

Plant Data Collection Bot for AI Training Project.

v1 - Data collection from 1 plant per bot. (Stable)

v2 - Data collection from 2 plant per bot. (Stable)

v3 - More reliable data collection from 2 plant per bot, better code structure, and new hardware integration to give and log watering. (Work In Progress)

Tested on Raspberry Pi 2 and 4.

## Instructions for v1 and v2:
- Set up 'venv' on raspberry pi using the provided "requirementspi2.txt" or "requirementspi4.txt".
- Replace "plant_data.csv" file with an empty file with the same name.
- Run the "calibration.py" script for the soil moisture sensor, following the on screen instructions.
- Run the "data-collection.py" file to start the bot.
- "Ctrl+C" to terminate the program.

## v2 Updates:
- Added second plant.
- Improved code structure.
- Improved and extended data structure.

## v3 Updates:
- Better code structure.
- More robust electrical engineering.
- More reliable data collection.
- Double amount of soil sensors per pot.
- Keypad and LCD screen integration.
- Semi-automated watering and logging.
