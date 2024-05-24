import os
import re
import time
import numpy as np
from pypylon import pylon


def str_extract(string, pre='', post=''):
    """string: string to be searched"""
    return re.search(pre + '(.*?)' + post, string).group(1)


def connectCameraBySerialNumber(serial_number_str=""):
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()
    print("Available devices:")
    for i, device in enumerate(devices):
        device_str = device.GetFriendlyName()
        print(device_str)
        device_serial_number_str = str_extract(device_str, pre='\(', post='\)')

        if serial_number_str == device_serial_number_str:
            device_index = i
            break

    camera = pylon.InstantCamera(tl_factory.CreateDevice(devices[device_index]))

    print(
        '\nConnected to ' + camera.GetDeviceInfo().GetModelName() + ' (' + camera.GetDeviceInfo().GetSerialNumber() + ')')

    return camera


def connectFirstFoundCamera():
    """Instantiate camera and open it."""
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    print('\nFound ' + camera.GetDeviceInfo().GetModelName())


def applyStreamSettings(camera_object, packet_size=9012, frame_rate=10):
    """Initialise stream grabber"""
    camera_object.Open()
    print('Camera opened')
    print('\nSetting parameters for stream grabber')
    print('Type of stream grabber (before): ' + camera_object.StreamGrabberNodeMap.Type.GetValue())
    camera_object.StreamGrabberNodeMap.Type.SetValue('SocketDriver')
    print('Type of stream grabber: ' + camera_object.StreamGrabberNodeMap.Type.GetValue())
    print('Transport layer packet size (before): ' + str(camera_object.GevSCPSPacketSize.GetValue()))
    camera_object.GevSCPSPacketSize.SetValue(packet_size)
    print('Transport layer packet size (after): ' + str(camera_object.GevSCPSPacketSize.GetValue()))
    camera_object.AcquisitionFrameRateEnable.SetValue(True)
    camera_object.AcquisitionFrameRateAbs.SetValue(frame_rate)
    camera_object.Close()


def applyCameraParams(camera_object, black_level=50, pixel_format='Mono10', exposure_ms=1):
    """
        Apply default values for:
        1. black level (50 for acA1280-60gm, ??? for acA1300-75gm)
        2. 'Mono12' for acA1280-60gm, 'Mono10' for acA1300-75gm
        3. exposure time
        """

    camera_object.Open()

    print('\nSetting initial parameters for camera')
    camera_object.BlackLevelRaw.Value = black_level
    camera_object.PixelFormat.Value = pixel_format
    camera_object.ExposureTimeAbs.Value = exposure_ms * 1e3
    print('Black level raw: ' + str(camera_object.BlackLevelRaw.GetValue()))
    print('Pixel format: ' + camera_object.PixelFormat.GetValue())
    print('Exposure time (ms): ' + str(camera_object.ExposureTimeAbs.GetValue() / 1e3))

    camera_object.Close()


def cameraOpen(camera_object):
    camera_object.Open()
    return None


def cameraClose(camera_object):
    camera_object.Close()
    return None


def cameraStartGrabbing(camera_object, strategy="LatestImageOnly"):
    if strategy == "OneByOne":
        camera_object.StartGrabbing(pylon.GrabStrategy_OneByOne)
    if strategy == "LatestImageOnly":
        camera_object.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    return None


def cameraStopGrabbing(camera_object):
    camera_object.StopGrabbing()
    return None


def setBuffer(camera_object, buffer_size=100):
    camera_object.MaxNumBuffer.Value = buffer_size


def clearBaslerBuffer(camera_object):
    while camera_object.NumReadyBuffers.GetValue() > 0:
        camera_object.RetrieveResult(100, pylon.TimeoutHandling_Return)


def baslerGrab(camera_object, number_of_images=100):
    """Renamed from BaslerGrabNew()"""
    camera_object.Open()
    camera_object.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    images = []

    frame_rate = camera_object.AcquisitionFrameRateAbs.GetValue()

    timeout_ms = int(5 * (1 / frame_rate * 1000))

    time.sleep(1)
    while len(images) < number_of_images:
        grabResult = camera_object.RetrieveResult(timeout_ms, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            img = grabResult.Array
            images.append(img)

            grabResult.Release()
            # print(img)
    camera_object.Close()
    return np.array(images)


def baslerGrab_SaveMean(camera_object, number_of_images, save_directory, save_filename='.tiff'):
    os.chdir(save_directory)

    images = baslerGrab(camera_object, number_of_images, debug=False)

    camera_object.Open()
    metadata = {
        'Date/Time': time.asctime(),
        'Number of images': len(images),
        'Exposure time (ms)': camera_object.ExposureTimeAbs.GetValue() / 1e3,
        'Pixel format': camera_object.PixelFormat.GetValue(),
        'Black level': camera_object.BlackLevelRaw.GetValue(),
        'Stream grabber type': camera_object.StreamGrabberNodeMap.Type.GetValue(),
        'Transport layer packet size': camera_object.GevSCPSPacketSize.GetValue()
    }
    camera_object.Close()

    # u.save_image(np.mean(images,axis=0),save_filename,metadata=metadata)


def setExposure(camera_object, exposure_time_ms):
    """Set exposure time for camera, in ms"""
    camera_object.Open()
    camera_object.ExposureTimeAbs.SetValue(exposure_time_ms * 1e3)
    camera_object.Close()


def getExposure(camera_object):
    camera_object.Open()
    exposure_time_ms = camera_object.ExposureTimeAbs.GetValue() / 1e3
    camera_object.Close()
    return exposure_time_ms


def setFrameRate(camera_object, framerate_hz):
    camera_object.Open()
    camera_object.AcquisitionFrameRateEnable.SetValue(True)
    camera_object.AcquisitionFrameRateAbs.SetValue(framerate_hz)
    camera_object.Close()
