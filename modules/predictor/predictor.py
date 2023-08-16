import multiprocessing
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
        self.__nextEntryPersonDetected, self.__nextEntryActionDetected = self.__initParams()
        self.__videoProcessing : VideoProcessing = VideoProcessing()
        self.__device : torch.Tensor = self.__setupHardware()
        self.__modelPersonDetection : DetectBackend = self.__setupModelPersonDetection()
        self.__personPredictionProcess : multiprocessing.Process

    def __initParams(self) -> tuple:
        """
        Tool to init params related to database
        """
        nextEntryPersonDetected : int
        nextEntryActionDetected : int
        params : dict = self.getParams()
        nextEntryPersonDetectedKey : str = "nextEntryPersonDetected"
        nextEntryActionDetectedKey : str = "nextEntryActionDetected"
        if nextEntryPersonDetectedKey not in params:
            nextEntryPersonDetected = self.__interfaceDatabase.getNextEntryPersonDetected()
            params.update({
                nextEntryPersonDetectedKey : nextEntryPersonDetected,
            })
        else:
            nextEntryPersonDetected = params[nextEntryPersonDetectedKey]

        if nextEntryActionDetectedKey not in params:
            nextEntryActionDetected = self.__interfaceDatabase.getNextEntryActionDetected()
            params.update({
                nextEntryActionDetectedKey : nextEntryActionDetected,
            })
        else:
            nextEntryActionDetected = params[nextEntryActionDetectedKey]

        self.writeParams(params)

        return nextEntryPersonDetected, nextEntryActionDetected
    
    def __updateNextEntryPersonDetected(self):
        """
        Tool to update next entry of person detected
        """
        params : dict = self.getParams()
        nextEntryPersonDetectedKey : str = "nextEntryPersonDetected"
        nextEntryPersonDetected : int = self.__interfaceDatabase.getNextEntryPersonDetected()
        params.update({
            nextEntryPersonDetectedKey : nextEntryPersonDetected,
        })
        self.writeParams(params)

        self.__nextEntryPersonDetected = nextEntryPersonDetected

    def __updateNextEntryActionDetected(self):
        """
        Tool to update next entry of action detected
        """
        params : dict = self.getParams()
        nextEntryActionDetectedKey : str = "nextEntryActionDetected"
        nextEntryActionDetected : int = self.__interfaceDatabase.getNextEntryActionDetected()
        params.update({
            nextEntryActionDetectedKey : nextEntryActionDetected,
        })
        self.writeParams(params)

        self.__nextEntryActionDetected = nextEntryActionDetected

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
        return str(self.__interfaceDatabase.getImageFromFrameId(self.__nextEntryPersonDetected))
    
    def __getObjectsNextFrame(self) -> dict:
        """
        Tool to get objects next image
        """
        self.__interfaceDatabase.getImageFromFrameId(self.__nextEntryActionDetected)

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
                        "x_0" : xyxy[0],
                        "y_0" : xyxy[1],
                        "x_1" : xyxy[2],
                        "y_1" : xyxy[3],
                    }
                })
                index += 1

        return coordinates

    def __updateDatabasePerson(self, coordinates : dict):
        """
        Tool to update new persons detected
        """
        self.__nextEntryPersonDetected
        self.__interfaceDatabase.updatePersonDetected(self.__nextEntryPersonDetected)
        for index in list(coordinates.keys()):
            self.__interfaceDatabase.storeNewObject(
                self.__nextEntryPersonDetected,
                int(coordinates[index]["x_0"]),
                int(coordinates[index]["y_0"]),
                int(coordinates[index]["x_1"]),
                int(coordinates[index]["y_1"]),
            )
        self.__updateNextEntryPersonDetected()

    def predictPerson(self):
        """
        Tool to perform prediction of a person
        """
        imagePath = self.__getNextImage()
        try:
            imageTensor, imageNumpy = self.__videoProcessing.processImageToTensorPersonDetection(
                imagePath,
                imgSize = self.__yoloConfig["imgSize"],
                stride = self.__modelPersonDetection.stride,
                half = self.__yoloConfig["half"],
                device = self.__device,
            )
        except Exception as e:
            self.writeLog("Image " + imagePath + " could not be processed" + str(e), "ERROR")
            self.__updateDatabasePerson(dict())
            return

        prediction : torch.Tensor = self.__predict(imageTensor, imageNumpy)

        coordinates = self.__getCoordinatesPersons(prediction, imageTensor)

        self.__updateDatabasePerson(coordinates)

    def predictAction(self):
        """
        Method to predict actions
        """
        self.__getObjectsNextFrame()

    def predictLoop(self):
        """
        Method to run predict loop
        """
        while True:
            self.predictPerson()

