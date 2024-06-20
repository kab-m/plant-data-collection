# plant-data-collection
Author: kbmDEV

Final Year Project Plant Data Collection Bot for AI training.

v1 - Data collection from 1 plant per bot (Stable)

v2 - Data collection from 2 plant per bot (Stable)


Tested on pi 2 and 4.

Instructions:
- Set up venv on raspberry pi and install requirements using the provided "requirementspi2.txt" or "requirementspi4.txt" (rename chosen one to requirements.txt and delete the other file).
- Replace "plant_data.csv" file with an empty file with the same name.
- Run the "calibration.py" script for the soil moisture sensor, following the on screen instructions.
- Run the "data-collection.py" file to start the bot.
- "Ctrl+C" to terminate the program.

v2 Updates:
- Added second plant.
- Improved code structure.
- Improved and extended data structure.
