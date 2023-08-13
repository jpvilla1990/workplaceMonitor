
from modules.baseModule.baseModule import BaseModule
from modules.interfaceDatabase.interfaceDatabase import InterfaceDatabase

class Predictor(BaseModule):
    """
    Class to predict persons and actions
    """
    def __init__(self):
        super().__init__()
        self.__interfaceDatabase : InterfaceDatabase = InterfaceDatabase()
        self.__lastEntryPersonDetected, self.__lastEntryActionDetected = self.__initParams()

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