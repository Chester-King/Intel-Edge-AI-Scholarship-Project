import time
import cv2 as cv
import argparse
import psutil
import os
import pyrebase

from openvino.inference_engine import IECore, IENetwork


def run_app():

    config = {
        "apiKey": "<Database Secret>",
        "authDomain": "intelaiopenvino.firebaseapp.com",
        "databaseURL": "https://intelaiopenvino.firebaseio.com",
        "storageBucket": "intelaiopenvino.appspot.com"
    }

    firebase = pyrebase.initialize_app(config)

    db = firebase.database()

    human_count = 0
    car_count = 0
    frame_count = 0

    print("App INITIALIZED")
    print("---------")

    # Load Network
    OpenVinoNetwork = IENetwork(
        model=arguments.model_xml, weights=arguments.model_bin)

    print("XML and BIN files loded")
    # Get Input Layer Information
    InputLayer = next(iter(OpenVinoNetwork.inputs))
    print("Input Layer: ", InputLayer)

    # Get Output Layer Information
    OutputLayer = next(iter(OpenVinoNetwork.outputs))
    print("Output Layer: ", OutputLayer)

    # Get Input Shape of Model
    InputShape = OpenVinoNetwork.inputs[InputLayer].shape
    print("Input Shape: ", InputShape)

    # Get Output Shape of Model
    OutputShape = OpenVinoNetwork.outputs[OutputLayer].shape
    print("Output Shape: ", OutputShape)

    # Load IECore Object
    OpenVinoIE = IECore()
    print("Available Devices: ", OpenVinoIE.available_devices)

    # Create Executable Network
    if arguments.async:
        print("Async Mode Enabled")
        OpenVinoExecutable = OpenVinoIE.load_network(
            network=OpenVinoNetwork, device_name=arguments.target_device, num_requests=number_of_async_req)
    else:
        OpenVinoExecutable = OpenVinoIE.load_network(
            network=OpenVinoNetwork, device_name=arguments.target_device)

    # Generate a Named Window to Show Output
    cv.namedWindow('Window', cv.WINDOW_NORMAL)
    cv.resizeWindow('Window', 800, 600)

    start_time = time.time()

    if arguments.input_type == 'image':
        frame_count += 1
        # Read Image
        image = cv.imread(arguments.input)

        # Get Shape Values

        N, C, H, W = OpenVinoNetwork.inputs[InputLayer].shape

        # Pre-process Image
        resized = cv.resize(image, (W, H))
        # Change data layout from HWC to CHW
        resized = resized.transpose((2, 0, 1))
        input_image = resized.reshape((N, C, H, W))

        # Start Inference
        start = time.time()
        results = OpenVinoExecutable.infer(inputs={InputLayer: input_image})
        end = time.time()
        inf_time = end - start
        print('Inference Time: {} Seconds Single Image'.format(inf_time))

        fps = 1./(end-start)
        print('Estimated FPS: {} FPS Single Image'.format(fps))

        fh = image.shape[0]
        fw = image.shape[1]

        # Write Information on Image
        text = 'FPS: {}, INF: {}'.format(round(fps, 2), round(inf_time, 2))
        cv.putText(image, text, (0, 20), cv.FONT_HERSHEY_COMPLEX,
                   0.6, (0, 125, 255), 1)

        # Print Bounding Boxes on Image
        detections = results[OutputLayer][0][0]

        print(detections)
        # refined_detections = []
        human_count = 0
        car_count = 0
        for detection in detections:

            print("*********************************************")
            print(detection)
            print("*********************************************")

            if(detection[2] > arguments.detection_threshold):
                # refined_detections.append(detection)
                print(detection)
                for detr in detection:
                    print(detr)
                print('Original Frame Shape: ', fw, fh)
                xmin = int(detection[3] * fw)
                ymin = int(detection[4] * fh)
                xmax = int(detection[5] * fw)
                ymax = int(detection[6] * fh)
                if(detection[1] == 1):
                    car_count += 1
                    cv.rectangle(frame, (xmin, ymin),
                                 (xmax, ymax), (0, 255, 0), 3)
                if(detection[1] == 2):
                    human_count += 1
                    cv.rectangle(frame, (xmin, ymin),
                                 (xmax, ymax), (0, 0, 255), 3)
                db.child("cars").set(car_count)
                db.child("humans").set(human_count)
                print("Number Of Humans present : ", human_count)
                print("Number Of Cars present : ", car_count)
            else:
                break
                # if detection[2] > arguments.detection_threshold:
                #     print('Original Frame Shape: ', fw, fh)
                #     xmin = int(detection[3] * fw)
                #     ymin = int(detection[4] * fh)
                #     xmax = int(detection[5] * fw)
                #     ymax = int(detection[6] * fh)
                #     cv.rectangle(image, (xmin, ymin),
                #                  (xmax, ymax), (0, 125, 255), 3)
                #     text = '{}, %: {}'.format(
                #         mobilenet_ssd_labels[int(detection[1])], round(detection[2], 2))
                #     cv.putText(image, text, (xmin, ymin - 7),
                #                cv.FONT_HERSHEY_PLAIN, 0.8, (0, 125, 255), 1)

        cv.imshow('Window', image)
        cv.waitKey(0)

    else:
        print("Running Inference for {} - {}".format(arguments.input_type, arguments.input))

        process_id = os.getpid()
        process = psutil.Process(process_id)

        total_inference_time = 0.0
        # Implementation for CAM or Video File
        # Read Image

        if(arguments.input == "0"):
            capture = cv.VideoCapture(0)
        else:
            capture = cv.VideoCapture(arguments.input)
        has_frame, frame = capture.read()
        frame_count += 1

        if not has_frame:
            print("Can't Open Input Video Source {}".format(arguments.input))
            exit(-1)

        # Get Shape Values
        N, C, H, W = OpenVinoNetwork.inputs[InputLayer].shape
        fh = frame.shape[0]
        fw = frame.shape[1]
        print('Original Frame Shape: ', fw, fh)

        request_order = list()
        process_order = list()
        frame_order = list()
        if arguments.async:
            print("Async Mode Set")
            for i in range(number_of_async_req):
                request_order.append(i)
                print('Request Id {} Created'.format(i))

            print('Request Ids {}'.format(request_order))
        cc = 0
        hc = 0
        while has_frame:

            if arguments.async:
                if len(request_order) > 0:
                    resized = cv.resize(frame, (W, H))
                    # Change data layout from HWC to CHW
                    resized = resized.transpose((2, 0, 1))
                    input_data = resized.reshape((N, C, H, W))
                    req_id = request_order[0]
                    request_order.pop(0)
                    OpenVinoExecutable.start_async(
                        req_id, inputs={InputLayer: input_data})
                    process_order.append(req_id)
                    frame_order.append(frame)

                if len(process_order) > 0:
                    first = process_order[0]
                    if OpenVinoExecutable.requests[first].wait(0) == 0:
                        results = OpenVinoExecutable.requests[first].outputs[OutputLayer]
                        process_order.pop(0)
                        request_order.append(first)
                        show_frame = frame_order[0]
                        frame_order.pop(0)

                        detections = results[0][0]
                        human_count = 0
                        car_count = 0
                        for detection in detections:

                            if detection[2] > arguments.detection_threshold:

                                xmin = int(detection[3] * fw)
                                ymin = int(detection[4] * fh)
                                xmax = int(detection[5] * fw)
                                ymax = int(detection[6] * fh)
                                if(detection[1] == 1):
                                    car_count += 1
                                    cv.rectangle(frame, (xmin, ymin),
                                                 (xmax, ymax), (0, 255, 0), 3)
                                    text = '{}, %: {}'.format("CAR",
                                                              round(detection[2], 3))
                                    cv.putText(
                                        show_frame, text, (xmin, ymin - 7), cv.FONT_HERSHEY_PLAIN, 0.8, (0, 255, 0), 1)
                                if(detection[1] == 2):
                                    human_count += 1
                                    cv.rectangle(frame, (xmin, ymin),
                                                 (xmax, ymax), (0, 0, 255), 3)
                                    text = '{}, %: {}'.format("HUMAN",
                                                              round(detection[2], 3))
                                    cv.putText(
                                        show_frame, text, (xmin, ymin - 7), cv.FONT_HERSHEY_PLAIN, 0.8, (0, 0, 255), 1)
                        if(cc != car_count):
                            cc = car_count
                            db.child("cars").set(car_count)
                        if(hc != human_count):
                            hc = human_count
                            db.child("humans").set(human_count)

                        print("Number Of Humans present : ", human_count)
                        print("Number Of Cars present : ", car_count)
                        fps = frame_count / (time.time() - start_time)
                        # Write Information on Image
                        text = 'FPS: {}, INF: {} ms'.format(round(fps, 3), "-")
                        cv.putText(show_frame, text, (0, 20),
                                   cv.FONT_HERSHEY_COMPLEX, 0.8, (0, 125, 255), 1)

                        text = "SYS CPU% {} SYS MEM% {} \n " \
                               "PROC CPU Affinity {} \n " \
                               "NUM Threads {} \n " \
                               "PROC CPU% {} \n " \
                               "PROC MEM% {}".format(psutil.cpu_percent(),
                                                     psutil.virtual_memory()[
                                   2],
                                   process.cpu_affinity(),
                                   process.num_threads(),
                                   process.cpu_percent(),
                                   round(process.memory_percent(), 4))

                        cv.putText(show_frame, text, (0, 50),
                                   cv.FONT_HERSHEY_COMPLEX, 1, (250, 0, 255), 1)
                        cv.imshow('Window', show_frame)
                        if cv.waitKey(1) & 0xFF == ord('q'):
                            break

                if len(process_order) > 0:
                    has_frame, frame = capture.read()
                    frame_count += 1
            else:
                frame_count += 1
                resized = cv.resize(frame, (W, H))
                # Change data layout from HWC to CHW
                resized = resized.transpose((2, 0, 1))
                input_data = resized.reshape((N, C, H, W))
                # Start Inference
                results = OpenVinoExecutable.infer(
                    inputs={InputLayer: input_data})

                fps = frame_count / (time.time() - start_time)
                inf_time = (time.time() - start_time) / frame_count
                # Write Information on Image
                text = 'FPS: {}, INF: {} ms'.format(
                    round(fps, 3), round(inf_time, 3))
                cv.putText(frame, text, (0, 20),
                           cv.FONT_HERSHEY_COMPLEX, 0.8, (0, 125, 255), 1)

                # Print Bounding Boxes on Image
                detections = results[OutputLayer][0][0]
                human_count = 0
                car_count = 0
                for detection in detections:

                    if detection[2] > arguments.detection_threshold:

                        xmin = int(detection[3] * fw)
                        ymin = int(detection[4] * fh)
                        xmax = int(detection[5] * fw)
                        ymax = int(detection[6] * fh)

                        if(detection[1] == 1):
                            car_count += 1
                            cv.rectangle(frame, (xmin, ymin),
                                         (xmax, ymax), (0, 255, 0), 3)
                            text = '{}, %: {}'.format("CAR",
                                                      round(detection[2], 3))
                            cv.putText(
                                frame, text, (xmin, ymin - 7), cv.FONT_HERSHEY_PLAIN, 0.8, (0, 255, 0), 1)
                        if(detection[1] == 2):
                            human_count += 1
                            cv.rectangle(frame, (xmin, ymin),
                                         (xmax, ymax), (0, 0, 255), 3)
                            text = '{}, %: {}'.format("HUMAN",
                                                      round(detection[2], 3))
                            cv.putText(
                                frame, text, (xmin, ymin - 7), cv.FONT_HERSHEY_PLAIN, 0.8, (0, 0, 255), 1)
                        detection_percentage = round(detection[2], 4)

                # db.child("cars").set(car_count)
                # print("Number Of Humans present : ", human_count)
                # db.child("humans").set(human_count)
                # print("Number Of Cars present : ", car_count)
                if(cc != car_count):
                    cc = car_count
                    db.child("cars").set(car_count)
                    print("Number Of Cars present : ", car_count)
                if(hc != human_count):
                    hc = human_count
                    db.child("humans").set(human_count)
                    print("Number Of Humans present : ", human_count)

                text = "SYS CPU% {} SYS MEM% {} \n " \
                       "PROC CPU Affinity {} \n " \
                       "NUM Threads {} \n " \
                       "PROC CPU% {} \n " \
                       "PROC MEM% {}".format(psutil.cpu_percent(),
                                             psutil.virtual_memory()[2],
                                             process.cpu_affinity(),
                                             process.num_threads(),
                                             process.cpu_percent(),
                                             round(process.memory_percent(), 4))

                cv.putText(frame, text, (0, 50),
                           cv.FONT_HERSHEY_COMPLEX, 0.8, (250, 0, 250), 1)
                cv.imshow('Window', frame)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
                has_frame, frame = capture.read()

    print("---------")
    print("App ENDS")


if __name__ == '__main__':

    # Parse Arguments
    parser = argparse.ArgumentParser(
        description='Open VINO vehical detection ADAS')
    parser.add_argument('--model-xml',
                        default='D:/Work/IntelOpenVINO/pedestrian-and-vehicle-detector-adas-0001/pedestrian-and-vehicle-detector-adas-0001.xml',
                        help='XML File')
    parser.add_argument('--model-bin',
                        default='D:/Work/IntelOpenVINO/pedestrian-and-vehicle-detector-adas-0001/pedestrian-and-vehicle-detector-adas-0001.bin',
                        help='BIN File')

    parser.add_argument('--target-device', default='CPU',
                        help='Target Plugin: CPU, GPU, FPGA, MYRIAD, MULTI:CPU,GPU, HETERO:FPGA,CPU')
    parser.add_argument('--input-type', default='video',
                        help='Type of Input: image, video, cam')
    parser.add_argument('--input', default='D:/Work/IntelOpenVINO/videos/Walk_cut.mp4',
                        help='Path to Input: WebCam: 0, Video File or Image file')

    parser.add_argument('--detection-threshold', default=0.6,
                        help='Object Detection Accuracy Threshold')

    parser.add_argument('--async', action="store_true",
                        default=False, help='Run Async Mode')
    parser.add_argument('--request-number', default=1,
                        help='Number of Requests')

    global arguments
    arguments = parser.parse_args()

    global number_of_async_req
    number_of_async_req = int(arguments.request_number)

    run_app()
