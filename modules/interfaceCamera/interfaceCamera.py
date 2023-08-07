import os
import cv2
import multiprocessing
import numpy as np
import time
from datetime import datetime
from PIL import Image
from modules.baseModule.baseModule import BaseModule

class InterfaceCamera(BaseModule):
    """
    Class to handle Cameras
    """
    def __init__(self):
        super().__init__()
        self.__cameraConfig : dict = self.getConfig()["cameras"]
        self.__dateTimeFormat : str = self.getConfig()["interfaceCamera"]["dateTimeFormat"]
        self.__imageFormat : str = self.getConfig()["interfaceCamera"]["imageFormat"]
        self.__continuousRecording : str = self.getConfig()["interfaceCamera"]["continuousRecording"]
        self.__cameraImagesFolder : str = self.getPaths()["folders"]["imagesDatabase"]
        self.__processes : dict = dict()
        self.__cameraProcess : multiprocessing.Process
        self.__terminateQueue : multiprocessing.Queue = multiprocessing.Queue()

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

        Image.fromarray(frame).save(imageName)

    def __captureVideo(self, camera : str):
        """
        Method to get Images from Camera
        """
        capture : cv2.VideoCapture = cv2.VideoCapture(self.__cameraConfig[camera])
        while(True):
            ret , frame = capture.read()

            if ret:
                self.__saveImage(
                    cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),
                    camera,
                )
            else:
                self.writeLog("Frame not available", "ERROR")

            if not self.__terminateQueue.empty():
                if self.__terminateQueue.get() == "terminate":
                    self.__terminateQueue.put("")
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
            if firstCycleFinished is False:
                self.__processes[index].start()
            if index == len(self.__processes):
                index = 0
                firstCycleFinished = True
                time.sleep(self.__continuousRecording)
            if firstCycleFinished and self.__processes[index].is_alive():
                self.__terminateQueue.put("terminate")
                self.__processes[index].join()
                self.__processes[index] = multiprocessing.Process(target=self.__captureVideo, args=[cameras[index]])
                self.__processes[index].start()
            index += 1

            if not self.__terminateQueue.empty():
                if self.__terminateQueue.get() == "terminate":
                    break

    def startCaptureVideos(self):
        """
        Method to capture videos from cameras in the background
        """
        self.__cameraProcess : multiprocessing.Process = multiprocessing.Process(target=self.captureVideos)
        self.__cameraProcess.start()

    def stopCaptureVideos(self):
        """
        Method to stop videos capture
        """
        self.__terminateQueue.put("terminate")