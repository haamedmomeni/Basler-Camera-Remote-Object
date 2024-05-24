import time
import Pyro4

ip_address = "10.10.17.19"
uri_bs = f"PYRONAME:AAS.BSC@{ip_address}:9090"
proxy_bss = Pyro4.Proxy(uri_bs)

###########################################################
# The rest of code is used to calibrate a motorized mirror#
###########################################################

ip_address = "10.10.0.109"
uri_vcc = f"PYRONAME:AAS.vcc1@{ip_address}:9090"
proxy_vcc = Pyro4.Proxy(uri_vcc)


def perform_movement_and_readings(proxy_vcc, proxy_bss, move_value, data_storage):
    proxy_vcc.move_mirror_top_bot(move_value)
    time.sleep(2)

    encoder_value = proxy_vcc.read_encoder_top_bot()
    shear_x, shear_y = proxy_bss.get_shear()

    print(f"encoder_top_bot: {encoder_value}")
    print(f"shearX: {shear_x}, shearY: {shear_y}")

    # Store data for slope calculation
    data_storage['encoder_values'].append(encoder_value)
    data_storage['shear_x_values'].append(shear_x)
    data_storage['shear_y_values'].append(shear_y)


def calculate_slope(x_values, y_values):
    if len(x_values) > 1 and len(y_values) > 1:
        # Using numpy to perform linear regression
        import numpy as np
        slope, intercept = np.polyfit(x_values, y_values, 1)
        return slope
    return None


def main():
    movements = [100, -100, -100, 100]
    repetitions = 3
    data_storage = {
        'encoder_values': [],
        'shear_x_values': [],
        'shear_y_values': []
    }
    for _ in range(repetitions):
        for move in movements:
            perform_movement_and_readings(proxy_vcc, proxy_bss, move, data_storage)

    # Calculating slopes
    slope_x = calculate_slope(data_storage['encoder_values'], data_storage['shear_x_values'])
    slope_y = calculate_slope(data_storage['encoder_values'], data_storage['shear_y_values'])

    print(f"Slope for Shear X over Encoder: {slope_x}")
    print(f"Slope for Shear Y over Encoder: {slope_y}")


if __name__ == "__main__":
    main()

