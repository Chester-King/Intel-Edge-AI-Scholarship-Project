# Home Guardian

The objective of the project is to run AI on the edge on CCTV camera at home looking over the driveway and the Android application can show you the status of the number of Cars or People present at the driveway in realtime. On the base level the camera uses the Optimized model to detect the number of cars and people present in the driveway and then if there is any change in the number of cars or people it updates the change to the [cloud database](https://firebase.google.com/). The android app picks up the changes in the cloud database in realtime and thus updates it on the app.

## Getting Started

To get the project you have to clone this [github repository](https://github.com/Chester-King/Intel-Edge-AI-Scholarship-Project). You also need to install OpenVINO in your machine. You can get the setup from this [website](https://software.intel.com/en-us/openvino-toolkit/choose-download).You would also need to have an Android Phone to install the APK of the app on your phone. You can download the APK from [here](https://drive.google.com/open?id=1H7cvGGaIPwG5YxuqezwdjMZXCCbIObMg). If you want to look at the android code, you'll need Android Studio in your system. You can download Android Studio frorm [here](https://developer.android.com/studio). To get a better view for the script of hardware or camera I recommend the use of VS Code. You can download VS Code from [here](https://code.visualstudio.com/download).

### Prerequisites

You need to have the following things installed in your system for the project to work

- OpenVINO
- CMake
- Python 3
- Microsoft Visual Studio
- Android Studio (If you want to take a look at android code as well)

### Installing

To know how to install and setup openVINO on different platforms you can take a look at [OpenVINO's repository](https://github.com/opencv/dldt).
To know how to install Android Studio you can take a look at the [user guide of android](https://developer.android.com/studio/install)

## Deployment

- First you need to start with running the Command Prompt with Administrator Privileges.
- Then you have to run the setupvars.bat file in it to set up the openVINO environment.
  The command I used for doing so is `D:\IntelSWTools\openvino_2020.1.033\bin\setupvars.bat`
  You will get an output on the screen something like this.

```
Python 3.6.8
ECHO is off.
PYTHONPATH=D:\IntelSWTools\openvino_2020.1.033\deployment_tools\open_model_zoo\tools\accuracy_checker;D:\IntelSWTools\openvino_2020.1.033\python\python3.6;D:\IntelSWTools\openvino_2020.1.033\python\python3;D:\IntelSWTools\openvino_2020.1.033\deployment_tools\model_optimizer;
[setupvars.bat] OpenVINO environment initialized
```

- You can now run your openvino application using the command `python D:\Work\IntelOpenVINO\hardware\tscriptCloud.py` **Note: This will only work if your machine is connected to the internet. If your machine is not connected to the internet and you still want to see the script in progress you can go with `python D:\Work\IntelOpenVINO\hardware\tscript1.py` but the app won't show live changes detected by the script**. You can also use multiple arguments to change the outcome of the application accordingly. You will get an output something like this.

```
python D:\Work\IntelOpenVINO\hardware\tscriptCloud.py
App INITIALIZED
---------
XML and BIN files loded
Input Layer:  data
Output Layer:  detection_out
Input Shape:  [1, 3, 384, 672]
Output Shape:  [1, 1, 200, 7]
[E:] [BSL] found 0 ioexpander device
Available Devices:  ['CPU', 'GNA', 'GPU']
Running Inference for video - D:/Work/IntelOpenVINO/videos/Walk_cut.mp4
MFX: Unsupported extension: D:/Work/IntelOpenVINO/videos/Walk_cut.mp4
Original Frame Shape:  1920 1080
Number Of Cars present :  2
Number Of Humans present :  1
Number Of Humans present :  0
Number Of Humans present :  1
Number Of Cars present :  1
Number Of Cars present :  2
Number Of Humans present :  0
Number Of Humans present :  1
---------
App ENDS
```

You will also have a video screen which will show you the detection of the cars and humans by the script.

- Wihle the application is running if you check the android application then you can see that the android application updates the values of the cars and humans in the app in realtime.

## The Various Command Line Parameters

`--model-xml` which can be used to specify your own model's XML file
`--model-bin` which can be used to specify your own model's BIN file
`--target-device` this param can be used to run the script using FPGA, MYRIAD, MULTI:CPU,GPU, HETERO:FPGA,CPU by default it is set to CPU
`--input-type` this param is used to specify the type of input you will give to the script. It can have three types of input `image`,`video`,`cam`
`--input` this param is used to specify the path of the input you will give to the script. For example `D:/Work/IntelOpenVINO/videos/Walk_cut.mp4`. For webcam you need to give `0` as input
`--detection-threshold` you can change the detection threshold if you want. By default the detection threshold is set to `0.6`

A sample command : `python D:\Work\IntelOpenVINO\hardware\tscriptCloud.py --target-device GPU --input-type cam --input 0 --detection-threshold 0.4`

## Demo of working project

[If you want to see the demo video of the working project you can get that here](https://drive.google.com/open?id=1cIGan87kJsCDwkodEyu0BUJ7j49WNweL)

## Authors

- **Madhur Dixit** - _Initial work_ - [Chester-King](https://github.com/Chester-King)

## License

This project is open source so if anyone wants to use any part of the code feel free to do so.

## Acknowledgments

- Intel Edge AI Scholarship Challenge
