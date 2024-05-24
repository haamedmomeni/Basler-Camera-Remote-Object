import numpy as np
import matplotlib.pyplot as plt
import datetime


def CoM(image):
    """Calculate the centroid of the entire image using a centre-of-mass algorithm."""
    x = np.arange(image.shape[1])
    y = np.arange(image.shape[0])
    xx, yy = np.meshgrid(x, y)

    sumx = np.sum(xx * image)
    sumy = np.sum(yy * image)
    total = np.sum(image)
    x0 = sumx / total
    y0 = sumy / total
    return [x0, y0]


def twoD_Gaussian(xy, amplitude, x0, y0, width, offset):
    """Two-dimensional Gaussian in cartesian coordinates, where width is 1/e2 RADIUS."""
    x0 = float(x0)
    y0 = float(y0)
    x, y = xy
    g = offset + amplitude * np.exp(-2 * ((x - x0) ** 2) / width ** 2) * np.exp(-2 * ((y - y0) ** 2) / width ** 2)
    return g


def iteratively_weighted_CoM(image_raw, spot_fwhm, end_condition=0.01, show_plots=False):
    """Calculate centroid iteratively using weighted centre-of-mass with optional plotting."""
    xy_old = CoM(image_raw)
    image_old = image_raw
    diff = 10  # Arbitrary initial difference greater than end_condition

    x_coords, y_coords = np.arange(image_raw.shape[1]), np.arange(image_raw.shape[0])
    xx, yy = np.meshgrid(x_coords, y_coords)

    N_iterations = 0

    while diff > end_condition:
        N_iterations += 1
        weighting = twoD_Gaussian((xx, yy), 1, xy_old[0], xy_old[1], 3 * spot_fwhm, 0)
        image_new = image_old * weighting
        xy_new = CoM(image_new)

        if show_plots:
            plt.figure(figsize=(16, 9))
            plt.suptitle(f'diff = {diff}')
            plt.subplot(121)
            plt.title('Original')
            plt.imshow(image_raw)
            plt.scatter([xy_old[0]], [xy_old[1]], label='old', color='red')
            plt.scatter([xy_new[0]], [xy_new[1]], label='new', color='orange')
            plt.legend()
            plt.subplot(122)
            plt.title('Current iteration')
            plt.imshow(image_new)
            plt.scatter([xy_old[0]], [xy_old[1]], label='old', color='red')
            plt.scatter([xy_new[0]], [xy_new[1]], label='new', color='orange')
            plt.legend()
            plt.show()

        diff = np.hypot(xy_new[0] - xy_old[0], xy_new[1] - xy_old[1])
        xy_old = xy_new

    return xy_new, N_iterations


def process_images(image, box_1_x_start=0, box_1_x_end=500, box_1_y_start=0, box_1_y_end=500,
                   box_2_x_start=600, box_2_x_end=1000, box_2_y_start=600, box_2_y_end=1000, iwcom=True):
    """Process images by extracting centroids from specified box regions."""
    box_1 = image[box_1_y_start:box_1_y_end, box_1_x_start:box_1_x_end] - np.median(image[:30, :30])
    box_2 = image[box_2_y_start:box_2_y_end, box_2_x_start:box_2_x_end] - np.median(image[:30, :30])
    np.clip(box_1, 0, None, out=box_1)
    np.clip(box_2, 0, None, out=box_2)

    box_1_xy = iteratively_weighted_CoM(box_1, 50)[0] if iwcom else CoM(box_1)
    box_2_xy = iteratively_weighted_CoM(box_2, 50)[0] if iwcom else CoM(box_2)

    box_1_xy[0] += box_1_x_start
    box_1_xy[1] += box_1_y_start
    box_2_xy[0] += box_2_x_start
    box_2_xy[1] += box_2_y_start

    now = datetime.datetime.now()
    return now, box_1_xy, box_2_xy


if __name__ == '__main__':
    image = plt.imread("dark_1000us.tiff")
    now, box_1, box_2 = process_images(image)
    plt.imshow(image)
    plt.scatter(*box_1, c='r')
    plt.scatter(*box_2, c='b')
    plt.show()
