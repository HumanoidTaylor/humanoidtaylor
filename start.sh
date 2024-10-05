#!/bin/bash

# Determine the path to the Conda initialization script
CONDA_BASE=$(conda info --base)
CONDA_SH="$CONDA_BASE/etc/profile.d/conda.sh"

# Open the first terminal and run the first set of commands
gnome-terminal -- bash --login -c "source '$CONDA_SH'; conda activate tts-env-new; python controlRobot_Mic.py; echo 'Press Enter to exit...'; read; exec bash"

# Open the second terminal and run the second set of commands
gnome-terminal -- bash --login -c "source '$CONDA_SH'; conda activate tts-env; python transcribe_Mic.py; echo 'Press Enter to exit...'; read; exec bash"

# Open the first terminal and run the first set of commands
gnome-terminal -- bash --login -c "source '$CONDA_SH'; conda activate tts-env; python Ask_Mic.py; echo 'Press Enter to exit...'; read; exec bash"

# Open the second terminal and run the second set of commands
gnome-terminal -- bash --login -c "source '$CONDA_SH'; conda activate tts-env-new; python prosse_Mic.py; echo 'Press Enter to exit...'; read; exec bash"



