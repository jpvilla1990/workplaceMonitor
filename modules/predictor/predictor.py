import os
import numpy as np
import torch
from yolov6.layers.common import DetectBackend
from yolov6.utils.nms import non_max_suppression
from yolov6.core.inferer import Inferer
from modules.baseModule.baseModule import BaseModule
from modules.interfaceDatabase.interfaceDatabase import InterfaceDatabase
from modules.videoProcessing.videoProcessing import VideoProcessing

class Predictor(BaseModule):
    """
    Class to predict persons and actions
    """
    def __init__(self):
        super().__init__()
        self.__yoloConfig = self.getConfig()["yolo"]
        self.__yoloWeightsPath : str = self.__initYoloWeights()
        self.__interfaceDatabase : InterfaceDatabase = InterfaceDatabase()
        self.__lastEntryPersonDetected, self.__lastEntryActionDetected = self.__initParams()
        self.__videoProcessing : VideoProcessing = VideoProcessing()
        self.__device : torch.Tensor = self.__setupHardware()
        self.__modelPersonDetection : DetectBackend = self.__setupModelPersonDetection()

    def __initParams(self) -> tuple:
        """
        Tool to init params related to database
        """
        lastEntryPersonDetected : int
        lastEntryActionDetected : int
        params : dict = self.getParams()
        lastEntryPersonDetectedKey : str = "lastEntryPersonDetected"
        lastEntryActionDetectedKey : str = "lastEntryActionDetected"
        if lastEntryPersonDetectedKey not in params:
            lastEntryPersonDetected = self.__interfaceDatabase.getLastEntryPersonDetected()
            params.update({
                lastEntryPersonDetectedKey : lastEntryPersonDetected,
            })
        else:
            lastEntryPersonDetected = params[lastEntryPersonDetectedKey]

        if lastEntryActionDetectedKey not in params:
            lastEntryActionDetected = self.__interfaceDatabase.getLastEntryActionDetected()
            params.update({
                lastEntryActionDetectedKey : lastEntryActionDetected,
            })
        else:
            lastEntryActionDetected = params[lastEntryActionDetectedKey]

        self.writeParams(params)

        return lastEntryPersonDetected, lastEntryActionDetected

    def __initYoloWeights(self):
        """
        Tool to download yolo pretrained weights if does not exists
        """
        weightsUrl : str = self.__yoloConfig["weightsUrl"] + self.__yoloConfig["version"] + "/" + self.__yoloConfig["checkpoint"] + ".pt"
        return self.downloadYoloWeights(
            url=weightsUrl,
        )

    def __setupHardware(self) -> torch.Tensor:
        """
        Tool to setup hardware
        """
        device = ""
        if torch.cuda.is_available():
            device = "cuda:0"
        else:
            device = "cpu"

        return torch.device(device)

    def __setupModelPersonDetection(self):
        """
        Tool to setup model person detection
        """
        modelPersonDetection : DetectBackend = DetectBackend(
            self.__yoloWeightsPath,
            device=self.__device,
        )

        if self.__yoloConfig["half"] and (self.__device.type != 'cpu'):
            modelPersonDetection = modelPersonDetection.half()
        else:
            modelPersonDetection = modelPersonDetection.float()

        if self.__device.type != 'cpu':
             modelPersonDetection(
                 torch.zeros(1, 3, *self.__yoloConfig["imgSize"]).to(self.__device).type_as(next(modelPersonDetection.parameters()))
            ) # warm up
             
        return modelPersonDetection

    def __getNextImage(self) -> str:
        """
        Tool to get next image
        """
        return str(self.__interfaceDatabase.getImageFromTimestamp(self.__lastEntryPersonDetected))

    def __predict(self, img : torch.Tensor, imageNumpy: np.ndarray) -> torch.Tensor:
        """
        Tool to predict from an image
        """
        prediction : torch.Tensor = self.__modelPersonDetection(img).clone().detach()
        det : any = non_max_suppression(
            prediction=prediction,
            conf_thres=self.__yoloConfig["conf_thres"],
            iou_thres=self.__yoloConfig["iou_thres"],
            classes=None,
            agnostic=self.__yoloConfig["agnostic_nms"],
            max_det=self.__yoloConfig["max_det"],
        )[0]

        if len(det):
            det[:, :4] = Inferer.rescale(img.shape[2:], det[:, :4], imageNumpy.shape).round()

        return det

    def __getCoordinatesPersons(self, prediction : torch.Tensor, image : torch.Tensor) -> dict:
        """
        Tool to get coordinates of persons
        """
        classes : list = self.__yoloConfig["classes"]
        coordinates : dict = dict()

        index : int = 0
        for *xyxy, conf, cls in reversed(prediction):
            classNum : int = int(cls)
            if classNum < len(classes) and conf > self.__yoloConfig["desiredConfidence"]:
                coordinates.update({
                    index : {
                        "x1" : xyxy[0],
                        "y1" : xyxy[1],
                        "x2" : xyxy[2],
                        "y2" : xyxy[3],
                    }
                })
                index += 1

        return coordinates
    
    def __updateDatabasePerson(self, coordinates : list):
        """
        Tool to update new persons detected
        """
        self.__interfaceDatabase.updatePersonDetected(self.__lastEntryPersonDetected)
        self.__interfaceDatabase.addNewObject(self.__lastEntryPersonDetected, coordinates)
        self.__lastEntryPersonDetected = self.__interfaceDatabase.getLastEntryActionDetected()

    def predictPerson(self):
        """
        Method to perform prediction of a person
        """
        imagePath = self.__getNextImage()
        imageTensor, imageNumpy = self.__videoProcessing.processImageToTensorPersonDetection(
            imagePath,
            imgSize = self.__yoloConfig["imgSize"],
            stride = self.__modelPersonDetection.stride,
            half = self.__yoloConfig["half"],
            device = self.__device,
        )

        prediction = self.__predict(imageTensor, imageNumpy)

        coordinates = self.__getCoordinatesPersons(prediction, imageTensor)

        self.__updateDatabasePerson(coordinates)

