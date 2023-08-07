from modules.interfaceDatabase.interfaceDatabase import InterfaceDatabase
from modules.baseModule.baseModule import BaseModule

class VideoProcessing(BaseModule):
    """
    Class to handle the video processing using AI algorithms
    """
    def __init__(self):
        super().__init__()
        self.__interfaceDatabse : InterfaceDatabase = InterfaceDatabase()

    def __detectPersons(self) -> tuple:
        """
        Tool to detect person using YOLO algorithm
        """

    def detectPerson(self):
        """
        Method to detect Person and write to the database the objects
        """
        image, imageIndex = self.__interfaceDatabse.getNextImage()
        prediction : tuple = self.__detectPersons(image)
        self.__interfaceDatabse.writePredictionToDatabase(prediction, imageIndex)
