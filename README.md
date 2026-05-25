# Pressure-Sensing Insole

This project was developed as part of my biomedical engineering studies at Universidad La Salle Bajío.

## The Problem
We aimed to create a system to detect foot pressure distribution that could help in diagnosing pathologies like flat feet or plantar fasciitis.

## How It Works
The system uses an array of piezoresistive pressure sensors connected to an Arduino. The Arduino reads the analog voltage from each sensor, and a Python script (using Tkinter, NumPy, and Pandas) visualizes this data as a pressure heatmap.

## How to Use It
1.  Connect the Arduino to your computer.
2.  Upload the provided Arduino code (`.ino` file).
3.  Run the Python script: `python pressure_gui.py`
4.  Step onto the insole.

## Team
- Emilio Gonzalez
- Diego Vandez Garcia
- Maria Fernanda Cruz Angel
- Cesar de Anda Ascencio
