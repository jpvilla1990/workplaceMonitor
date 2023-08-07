import numpy as np
from modules.baseModule.baseModule import BaseModule

class InterfaceDatabase(BaseModule):
    """
    Class to manage interface to the databases
    """
    def __init__(self):
        super().__init__()

    def getNextImagePersonDetection(self) -> np.ndarray:
        """
        Method to obtain next image for person detection to be predicted
        """

    def getNextImageActionDetection(self) -> np.ndarray:
        """
        Method to obtain next image for action detection to be predicted
        """

    def writePredictionToDatabase(self, prediction : tuple, indexImage : str):
        """
        Method to write to database the prediction
        """