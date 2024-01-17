#!/bin/bash

# Start a new tmux session named "plant" + activate venv and run data_collection script
tmux new-session -d -s plant "source /home/kaboom/Data_Collection/venv/bin/activate && python /home/kaboom/Data_Collection/data_collection.py"
   