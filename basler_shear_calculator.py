import basler as b
import numpy as np
import matplotlib.pyplot as plt
import tifffile
from shear_claculator import process_images
import Pyro4


@Pyro4.expose
class BaslerShearCalculator:
    def __init__(self, camera_serial_number_str):
        self.camera_serial_number_str = camera_serial_number_str

    def grab_frame(self, exposure_ms=1.0, framerate_hz=30.0):
        camera_object = b.connectCameraBySerialNumber(serial_number_str=self.camera_serial_number_str)

        b.cameraOpen(camera_object)
        b.setExposure(camera_object, exposure_ms)
        b.setFrameRate(camera_object, framerate_hz)
        b.setBuffer(camera_object, buffer_size=80)
        images = b.baslerGrab(camera_object, number_of_images=30)
        b.cameraClose(camera_object)

        mean_image = np.mean(images, axis=0)
        mean_image *= 2 ** (16 - 10)  # scale up for saving as 16 bit tiff

        dark = plt.imread("dark_1000us.tiff")
        # dark *= 2**(16-10) # only if saved image hasn't been scaled up to 16 bit
        res = np.subtract(mean_image, dark)
        res[res < 0] = 0

        return res

    def get_shear(self, exposure_ms=1.0, framerate_hz=30.0):
        frame = self.grab_frame(exposure_ms=exposure_ms, framerate_hz=framerate_hz)
        now, box_1, box_2 = process_images(frame)
        x1, y1 = box_1
        x2, y2 = box_2
        return x2 - x1, y2 - y1


if __name__ == "__main__":
    serial_number = "24810746"
    basler_shear_calculator = BaslerShearCalculator(serial_number)
    exposure = 1.0
    frame_rate = 15.0
    image = basler_shear_calculator.grab_frame(exposure, frame_rate)
    now, box_1, box_2 = process_images(image)
    plt.imshow(image)
    plt.scatter(*box_1, c='r')
    plt.scatter(*box_2, c='b')
    plt.show()

    tifffile.imwrite("image.tiff", image.astype(np.uint16))
