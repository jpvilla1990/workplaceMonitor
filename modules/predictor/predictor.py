import numpy as np
import time
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
        self.__actionsConfig = self.getConfig()["actions"]
        self.__predictionConfig = self.getConfig()["prediction"]
        self.__yoloWeightsPath : str = self.__initYoloWeights()
        self.__interfaceDatabase : InterfaceDatabase = InterfaceDatabase()
        self.__nextEntryPersonDetected, self.__nextEntryActionDetected = self.__initParamsDetectionIndex()
        self.__videoProcessing : VideoProcessing = VideoProcessing()
        self.__device : torch.Tensor = self.__setupHardware()
        self.__modelPersonDetection : DetectBackend = self.__setupModelPersonDetection()

    def __initParamsDetectionIndex(self) -> tuple:
        """
        Tool to init params related to database
        """
        nextEntryPersonDetected = self.__interfaceDatabase.getNextEntryPersonDetected()
        nextEntryActionDetected = self.__interfaceDatabase.getNextEntryActionDetected()

        return nextEntryPersonDetected, nextEntryActionDetected
    
    def __updateNextEntryPersonDetected(self):
        """
        Tool to update next entry of person detected
        """
        while True:
            try:
                nextEntryPersonDetected : int = self.__interfaceDatabase.getNextEntryPersonDetected()
                self.__nextEntryPersonDetected = nextEntryPersonDetected
                break
            except Exception as e:
                self.writeLog("Could not update new entry, " + e, "WARNING")
                time.sleep(self.__predictionConfig["sleepPrediction"])

    def __updateNextEntryActionDetected(self):
        """
        Tool to update next entry of action detected
        """
        while True:
            try:
                nextEntryActionDetected : int = self.__interfaceDatabase.getNextEntryActionDetected()
                self.__nextEntryActionDetected = nextEntryActionDetected
                break
            except Exception as e:
                self.writeLog("Could not update new entry, " + str(e), "WARNING")
                time.sleep(self.__predictionConfig["sleepPrediction"])

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
    
    def __getImageCurrentActionPrediction(self) -> str:
        """
        Tool to get image of current action prediction index
        """
        return str(self.__interfaceDatabase.getImageFromFrameId(self.__nextEntryActionDetected))
    
    def __getObjectsNextFrame(self) -> list:
        """
        Tool to get objects next image
        """
        return self.__interfaceDatabase.getObjectsIdFromFrameId(self.__nextEntryActionDetected)
    
    def __getActivePersons(self) -> list:
        """
        Tool to get persons that are still active
        """
        return self.__interfaceDatabase.getActivePersons()
    
    def __getCoordinates(self, personId : int = None, objectId : int = None) -> list:
        """
        Tool to get object 
        """
        if personId is not None:
            return self.__interfaceDatabase.getCoordinatesByPersonId(personId)
        elif objectId is not None:
            return self.__interfaceDatabase.getCoordinatesByObjectId(objectId)
        
    def __getNumberFramesFromObjectId(self, objectId : int) -> int:
        """
        Tool to get number frames from object
        """
        personId : int = self.__interfaceDatabase.getPersonIdFromObjectId(objectId)
        frames : list = self.__interfaceDatabase.getFramesFromPersonId(personId)

        return len(frames)

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
    
    def __addNewPerson(self, objectId : int):
        """
        Tool to add new person in database
        """
        self.__interfaceDatabase.createNewPerson()
        personId : int = self.__interfaceDatabase.getNewPerson()
        self.__interfaceDatabase.updatePersonIdFromObjectId(objectId, personId)

    def __updatePersonsAsCompleted(self, personId : int):
        """
        Tool to update person as completed
        """
        self.__interfaceDatabase.setPersonAsCompleted(personId)

    def __updatePersonAsIdle(self, objectId : int):
        """
        Tool to classify person as idle
        """
        personId : int = self.__interfaceDatabase.getPersonIdFromObjectId(objectId)
        self.__interfaceDatabase.setIdleClasification(personId)

    def __getCurrenTimestamp(self) -> int:
        """
        Tool to get current frame timestamp
        """
        return self.__interfaceDatabase.getTimestampFromFrameId(self.__nextEntryActionDetected)
    
    def __updateAnnotatedImagePath(self, imagePath : str):
        """
        Tool to update annotated image
        """
        self.__interfaceDatabase.setAnnotatedImagePath(imagePath, self.__nextEntryActionDetected)

    def __getPersonTimestamp(self, personId : int) -> int:
        """
        Tool to get object timestamp
        """
        frameId : int = self.__interfaceDatabase.getFrameIdFromPersonId(personId)
        return self.__interfaceDatabase.getTimestampFromFrameId(frameId)
    
    def __getImagesFromPersonId(self, personId) -> dict:
        """
        Tool to get images from Person Id
        """
        objects : list = self.__interfaceDatabase.getObjectsFromPersonId(personId)

        images : dict = dict()
        index : int = 0
        for object in objects:
            x0 : int = int(object[0])
            y0 : int = int(object[1])
            x1 : int = int(object[2])
            y1 : int = int(object[3])
            frameId : int = int(object[4])

            framePath : str = self.__interfaceDatabase.getImageFromFrameId(frameId)

            images.update({
                index : {
                    "x0" : x0,
                    "y0" : y0,
                    "x1" : x1,
                    "y1" : y1,
                    "framePath" : framePath,
                }
            })

            index += 1

        return images

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

    def __compareCoordinates(self, coordinates1 : list, coordinates2 : list) -> tuple:
        """
        Tool to compare coordinates according to the configured tolerance
        """
        tolerance : float = self.__actionsConfig["boxTolerance"]
        tolerated : bool = True
        if int(coordinates1[0]) > (1 + tolerance) * int(coordinates2[0]) or int(coordinates1[0]) < (1 - tolerance) * int(coordinates2[0]):
            tolerated = False
        if int(coordinates1[1]) > (1 + tolerance) * int(coordinates2[1]) or int(coordinates1[1]) < (1 - tolerance) * int(coordinates2[1]):
            tolerated = False
        if int(coordinates1[2]) > (1 + tolerance) * int(coordinates2[2]) or int(coordinates1[2]) < (1 - tolerance) * int(coordinates2[2]):
            tolerated = False
        if int(coordinates1[3]) > (1 + tolerance) * int(coordinates2[3]) or int(coordinates1[3]) < (1 - tolerance) * int(coordinates2[3]):
            tolerated = False

        distance : float = ((((coordinates1[0] - coordinates2[0])**2) + ((coordinates1[1] - coordinates2[1])**2) + ((coordinates1[2] - coordinates2[2])**2) + ((coordinates1[3] - coordinates2[3])**2)) / len(coordinates1)) ** (1/2)

        return tolerated, distance
    
    def __createImagePrediction(self, objects : list):
        """
        Tool to create image prediction
        """
        imagePath : str = self.__getImageCurrentActionPrediction()

        coordinatesDict : dict = dict()

        for object in objects:
            numberFrames : int = self.__getNumberFramesFromObjectId(object)
            annotationIdle : bool = False

            if numberFrames > self.__actionsConfig["idleFrames"]:
                annotationIdle = True
                self.__updatePersonAsIdle(object)
            coordinatesDict.update({
                object : {
                    "coordinates" : self.__getCoordinates(objectId=object)[0],
                    "annotation" : annotationIdle,
                }
            })

        annotatedImagePath : str = self.__videoProcessing.annotateImage(imagePath, coordinatesDict)

        self.__updateAnnotatedImagePath(annotatedImagePath)

    def predictPerson(self):
        """
        Tool to perform prediction of a person
        """
        imagePath : str = self.__getNextImage()
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

        coordinates : dict = self.__getCoordinatesPersons(prediction, imageTensor)

        self.__updateDatabasePerson(coordinates)

    def createPredictionVideo(self):
        """
        Method to create videos if exists new clasification
        """
        nextPerson : list = self.__interfaceDatabase.getNextVideo()
        if len(nextPerson) == 0:
            return
        else:
            personId : int = int(nextPerson[0])
            images : dict = self.__getImagesFromPersonId(personId)

            videoPath : str = self.__videoProcessing.createVideoFromImages(images, personId)

            self.__interfaceDatabase.updateVideoPath(videoPath, personId)

    def predictAction(self):
        """
        Method to predict actions
        """
        if self.__nextEntryActionDetected >= self.__nextEntryPersonDetected:
            self.writeLog("The Action detection frame has reached Person detection frame", "WARNING")
            return
        objects : list = self.__getObjectsNextFrame()
        persons : list = self.__getActivePersons()

        currentObjectsCoordinates : dict = dict()
        activePersonsCoordinates : dict = dict()

        for object in objects:
            currentObjectsCoordinates.update({
                object : self.__getCoordinates(objectId=object),
            })

        for person in persons:
            activePersonsCoordinates.update({
                person : self.__getCoordinates(personId=person),
            })

        if len(objects) != 0 and len(persons) == 0:
            for object in objects:
                self.__addNewPerson(object)

        if len(objects) == 0 and len(persons) != 0:
            for person in persons:
                self.__updatePersonsAsCompleted(person)

        if len(objects) != 0 and len(persons) != 0:
            currentTimestamp : int = self.__getCurrenTimestamp()
            for person in persons:
                personTimestamp : int = self.__getPersonTimestamp(person)

                if personTimestamp - currentTimestamp > self.__actionsConfig["maxTimestampDifference"]:
                    self.__updatePersonsAsCompleted(person)
                else:
                    distances : dict = dict()
                    for object in list(currentObjectsCoordinates.keys()):
                        comparison, distance = self.__compareCoordinates(
                            currentObjectsCoordinates[object][0],
                            activePersonsCoordinates[person][0],
                        )

                        if comparison:
                            distances.update({
                                object : distance,
                            })

                    if len(distances) > 0:
                        minDistanceObject : float = min(distances, key=lambda k: distances[k])
                        currentObjectsCoordinates.pop(minDistanceObject)
                        self.__interfaceDatabase.updatePersonIdFromObjectId(minDistanceObject, person)
                    else:
                        self.__updatePersonsAsCompleted(person)

            for object in list(currentObjectsCoordinates.keys()):
                self.__addNewPerson(object)

        self.__createImagePrediction(objects)

        self.__interfaceDatabase.updateActionDetected(self.__nextEntryActionDetected)
        self.__updateNextEntryActionDetected()

    def predictLoop(self):
        """
        Method to run predict loop
        """
        while True:
            self.predictPerson()
            self.predictAction()
            self.createPredictionVideo()
