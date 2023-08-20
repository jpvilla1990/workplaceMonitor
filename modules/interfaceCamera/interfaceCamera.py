import os
import cv2
import multiprocessing
import numpy as np
import time
from datetime import datetime
from PIL import Image
from modules.baseModule.baseModule import BaseModule
from modules.interfaceDatabase.interfaceDatabase import InterfaceDatabase

class InterfaceCamera(BaseModule):
    """
    Class to handle Cameras

    IP camera: https://www.aranacorp.com/en/managing-an-ip-camera-with-python/
    """
    def __init__(self):
        super().__init__()
        self.__cameraConfig : dict = self.getConfig()["cameras"]
        self.__interfaceCameraConfig : dict = self.getConfig()["interfaceCamera"]
        self.__dateTimeFormat : str = self.getConfig()["interfaceCamera"]["dateTimeFormat"]
        self.__imageFormat : str = self.getConfig()["interfaceCamera"]["imageFormat"]
        self.__cameraImagesFolder : str = self.getPaths()["folders"]["imagesDatabase"]
        self.__processes : dict = dict()
        self.__cameraProcess : multiprocessing.Process
        self.__interfaceDatabase : InterfaceDatabase = InterfaceDatabase()
        self.__runningProcess : bool = False

    def __del__(self):
        if self.__runningProcess:
            if self.__cameraProcess.is_alive():
                self.stopCaptureVideos()

    def __saveImage(self, frame : np.ndarray, camera : str):
        """
        Tool to save image in folder
        """
        self.createFolderRecursively(os.path.join(self.__cameraImagesFolder, camera))
        imageName : str = os.path.join(
            self.__cameraImagesFolder,
            camera,
            datetime.now().strftime(self.__dateTimeFormat) + self.__imageFormat,
        )

        self.__interfaceDatabase.storeNewFrame(imageName)

        Image.fromarray(frame).save(imageName)

    def __captureVideo(self, camera : str):
        """
        Method to get Images from Camera
        """
        capture : cv2.VideoCapture = cv2.VideoCapture(self.__cameraConfig[camera])
        fps : int = capture.get(cv2.CAP_PROP_FPS)
        frameIndexToCapture = int(fps / self.__interfaceCameraConfig["framesPerSecond"])

        videoIndex : int = 0
        while(True):
            ret , frame = capture.read()
            if videoIndex % frameIndexToCapture == 0:
                if ret:
                    self.__saveImage(
                        cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),
                        camera,
                    )
                else:
                    break

                if self.getProcessesState("interfaceCameraSubProcess" + camera) == "terminate":
                    break

    def captureVideos(self):
        """
        Method to capture videos from cameras
        """
        cameras : list = list(self.__cameraConfig.keys())
        for index in range(len(cameras)):
            self.__processes.update({
                index : multiprocessing.Process(target=self.__captureVideo, args=[cameras[index]])
            })

        index : int = 0
        firstCycleFinished : bool = False
        while(True):
            if index == len(self.__processes):
                index = 0
                firstCycleFinished = True
                time.sleep(self.__interfaceCameraConfig["recordingRatePerSecond"])
            if firstCycleFinished is False:
                self.updateProcessesState({
                    "interfaceCameraSubProcess" + cameras[index] : "running",
                })
                self.__processes[index].start()
            if firstCycleFinished:
                if self.__processes[index].is_alive():
                    self.updateProcessesState({
                        "interfaceCameraSubProcess" + cameras[index] : "terminate",
                    })
                    self.__processes[index].join()
                self.__processes.pop(index)
                self.__processes[index] = multiprocessing.Process(target=self.__captureVideo, args=[cameras[index]])
                self.__processes[index].start()
            index += 1

            if self.getProcessesState("interfaceCamera") == "terminate":
                break

    def startCaptureVideos(self):
        """
        Method to capture videos from cameras in the background
        """
        self.__cameraProcess = multiprocessing.Process(target=self.captureVideos)
        self.updateProcessesState({
            "interfaceCamera" : "running",
        })
        self.__runningProcess = True
        self.__cameraProcess.start()

    def stopCaptureVideos(self):
        """
        Method to stop videos capture
        """
        self.updateProcessesState({
            "interfaceCamera" : "terminate",
        })
        self.__runningProcess = False
        self.__cameraProcess.join()
