"""
This class is written to grab frames from Basler camera and calculate the shear of spotlight on camera.
This program assumes that the Basler camera is connected to the machine and the Basler Pylon software is installed.
The shear is calculated by finding the difference in the x and y coordinates of the two boxes drawn around the spotlight.
Written by Hamed Momeni @ MROI, 2024
"""
import sys
import netifaces as ni
import Pyro4
import subprocess
import time
from basler_shear_calculator import BaslerShearCalculator

CAMERA_SERIAL_NUMBER = "24810746"
DELAY_TO_START = 2  # Delay in seconds to start the Pyro name server
TIMEOUT = 3  # Timeout in seconds
PORT_NUMBER = 9090  # Port number for the Pyro server
NAME_SERVER_PORT_NUMBER = 9091  # Port number for the Pyro name server


def get_wired_interface_ip():
    """
    Function to retrieve the IP address of the wired network interface of the current machine.
    """
    try:
        # Get a list of all available network interfaces on the system
        interfaces = ni.interfaces()

        # Loop through each interface to find the wired one
        for interface in interfaces:
            # Get addresses associated with the current interface
            addresses = ni.ifaddresses(interface)

            # Check if there are addresses available for the interface
            if ni.AF_INET in addresses:
                # Retrieve the IPv4 address from the interface
                ip_address = addresses[ni.AF_INET][0]['addr']
                # Return the IP address of the first non-loopback wired interface found
                return ip_address

        # Raise a custom exception if no wired interface is found
        raise Exception("No wired interface found")

    except Exception as e:
        print(f"Error getting wired interface IP: {e}")

    """
    Difference between Pyro server and Pyro name server:
    Here's a simple analogy: think of the Pyro server as a telephone,
    and the Pyro objects it hosts as the people who can be reached on that telephone.
    The Pyro name server is like a telephone directory:
    it lets you look up people (Pyro objects) by name instead of
    having to remember their phone number (object ID and server location).
    """


def start_nameserver(ip_address):
    """
    Function to start the Pyro name server.
    We start the name server in a separate process by using the Popen() function from the subprocess module.
    We then let the server have some time to start by using the sleep function from the time module.
    """
    subprocess.Popen(["pyro4-ns", "-n", ip_address, "-p", str(PORT_NUMBER)])
    time.sleep(DELAY_TO_START)  # Give the name server some time to start


def main():
    """
    The main function where the Pyro server is started and the BeamTrainController instance is registered.
    """
    str_dumb = "_______________________________"
    print(f"{str_dumb}\nStart AAS for first fringes...\n{str_dumb}")

    # Construct beam train control instances
    try:
        basler_shear_calculator = BaslerShearCalculator(CAMERA_SERIAL_NUMBER)
    except Exception as e:
        print("error creating instances")
        return

    # Get the IP address of the current machine
    ip_address = get_wired_interface_ip()
    # Check if wired interface is found or there was an error
    if ip_address:
        print(f"IP address of wired interface: {ip_address}")
    else:
        print("No wired interface found or error occurred while retrieving the IP address.")
        sys.exit()  # Terminate the program execution

    # Define the port as a variable
    port = NAME_SERVER_PORT_NUMBER

    # Start a Pyro name server on the current machine
    start_nameserver(ip_address)

    daemon = None
    try:
        # Create a Pyro daemon (server) on the specified IP address and port
        daemon = Pyro4.Daemon(host=ip_address, port=port)

        daemon.timeout = TIMEOUT  # Set the daemon timeout in seconds

        # Locate the Pyro name server
        ns = Pyro4.locateNS()

        # Register the BeamTrainController instance with the daemon and get its URI,
        # URI: Uniform Resource Identifier
        uri = daemon.register(basler_shear_calculator)

        # Register the BeamTrainController instance with the name server
        ns.register("AAS.BSC", uri)

        print(f"Pyro server started on {ip_address}:{port}")

        # Get a list of all registered objects
        all_registered = ns.list()

        # Print out all registered objects
        for name, uri in all_registered.items():
            print(f"{name} is available!")

        print(f"{str_dumb}\n")
        # Start the request loop of the daemon to process requests
        daemon.requestLoop()

    except Exception as e:
        print(f"Error starting Pyro server: {e}")

    finally:
        # Shutdown the Pyro daemon
        if daemon:
            daemon.shutdown()

        # Terminate the name server process and wait for it to finish
        subprocess.Popen.terminate
        subprocess.Popen.wait
        # "wait" ensures that the process has been terminated by blocking the parent process
        # until the child process has exited and its exit status has been collected.

        print("Name server and Pyro server have been shut down.")


if __name__ == "__main__":
    main()
