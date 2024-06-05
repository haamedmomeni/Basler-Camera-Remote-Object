# Basler-Camera-Remote-Object

## Overview
The Basler Shear Calculator is developed to capture several frames from a Basler camera, averag them, and calculate the centroid of a spotlight on the frames. This application relies on the Basler Pylon library being installed and the camera being connected to the machine. The relative centroid (shear) is calculated by finding the difference in the x and y coordinates of two predefined boxes around two spotlight, reference spotlight and moving spotlight.

## Author
- Hamed Momeni @ MROI, 2024

## Prerequisites
- Basler camera connected to your computer.
- Basler Pylon software installed.
- Python 3 environment with dependencies installed from the `requirements.txt` file.

## Installation
1. Clone this repository to your local machine.
2. Ensure that the Basler Pylon software is installed and properly configured.
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
     

## Usage
To run the program, navigate to the project directory and execute:
  ```bash
  python3 main.py
```

## Functionality
IP Retrieval: Automatically retrieves the IP address of the wired network interface.
Pyro4 Integration: Uses Pyro4 for network communication.
        Starts a Pyro4 name server to manage object references.
        Registers the Basler Shear Calculator instance with the Pyro4 daemon.
Image Processing: Captures frames from the Basler camera, processes them to calculate the shear, and displays the results.

## Components
BaslerShearCalculator: Main class for handling camera operations and shear calculations.
main.py: Entry point of the application, setting up the server and starting the GUI.

## Troubleshooting
Ensure the camera is properly connected and detected by the Basler Pylon software.
Check network settings if there are issues with Pyro4 communication.
