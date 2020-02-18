import time
import cv2 as cv
import argparse
import psutil
import os

from openvino.inference_engine import IECore, IENetwork


def run_app():

    frame_count = 0

    print("App INITIALIZED")
    print("---------")

    # Load Network
    OpenVinoNetwork = IENetwork(
        model=arguments.model_xml, weights=arguments.model_bin)

    print("XML and BIN files loded")
    # # Get Input Layer Information
    # InputLayer = next(iter(OpenVinoNetwork.inputs))
    # print("Input Layer: ", InputLayer)

    # # Get Output Layer Information
    # OutputLayer = next(iter(OpenVinoNetwork.outputs))
    # print("Output Layer: ", OutputLayer)

    # # Get Input Shape of Model
    # InputShape = OpenVinoNetwork.inputs[InputLayer].shape
    # print("Input Shape: ", InputShape)

    # # Get Output Shape of Model
    # OutputShape = OpenVinoNetwork.outputs[OutputLayer].shape
    # print("Output Shape: ", OutputShape)

    # # Load IECore Object
    # OpenVinoIE = IECore()
    # print("Available Devices: ", OpenVinoIE.available_devices)

    print("---------")
    print("App ENDS")


if __name__ == '__main__':

    # Parse Arguments
    parser = argparse.ArgumentParser(
        description='Open VINO vehical detection ADAS')
    parser.add_argument('--model-xml',
                        default='D:/Work/IntelOpenVINO/vehicle-detection-adas-model/vehicle-detection-adas-0002.xml',
                        help='XML File')
    parser.add_argument('--model-bin',
                        default='D:/Work/IntelOpenVINO/vehicle-detection-adas-model/vehicle-detection-adas-0002.bin',
                        help='BIN File')

    global arguments
    arguments = parser.parse_args()

    run_app()
