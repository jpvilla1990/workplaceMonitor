import numpy as np
import time
from datetime import datetime
import mysql.connector
from modules.baseModule.baseModule import BaseModule
from modules.interfaceDatabase import schemas

class InterfaceDatabase(BaseModule):
    """
    Class to manage interface to the databases
    """
    def __init__(self):
        super().__init__()
        self.__config = self.getConfig()["database"]
        self.__dateTimeFormat : str = self.getConfig()["interfaceCamera"]["dateTimeFormat"]
        self.__createDatabase()
        self.__initTables()
        self.__timestampRef : float = self.__initParams()

    def __initParams(self) -> float:
        """
        Tool to init params related to database
        """
        timestampRef : float
        params : dict = self.getParams()
        timestampRefKey : str = "timestampRef"
        if timestampRefKey not in params:
            timestampNow : float = datetime.now().timestamp()
            params.update({
                timestampRefKey : timestampNow,
            })
            self.writeParams(params)
            timestampRef = timestampNow
        else:
            timestampRef = params[timestampRefKey]

        return timestampRef

    def __initTables(self):
        """
        Tool to init tables if they do not exist
        """
        connection : mysql.connector = self.__getConnection()
        cursor : mysql.connector.cursor = connection.cursor()
        for table in list(schemas.tables.keys()):
            cursor.execute(schemas.tables[table]["checkTable"])
            if cursor.fetchone() is None:
                print(schemas.tables[table]["createTable"])
                cursor.execute(schemas.tables[table]["createTable"])

        connection.commit()
        cursor.close()
        connection.close()

    def __createDatabase(self):
        """
        Method to create database
        """
        connector : mysql.connector = mysql.connector.connect(
            user=self.__config["user"],
            password=self.__config["password"],
            host=self.__config["host"],
        )
        cursor : any = connector.cursor()

        cursor.execute(schemas.database["checkDatabase"])

        databases : list = [row[0] for row in cursor]

        if self.__config["database"] not in databases:
            cursor.execute(schemas.database["createDatabase"] + self.__config["database"])
            connector.commit()
            cursor.close()
            connector.close()
    
    def __getConnection(self) -> mysql.connector:
        """
        Method to get a connection
        """
        connector = mysql.connector.connect(
            user=self.__config["user"],
            password=self.__config["password"],
            host=self.__config["host"],
            database=self.__config["database"],
        )

        return connector
    
    def deleteTable(self, table : str):
        """
        Method to delete a table
        """
        self.__executeQuery("DROP TABLE " + table + ";")

    def resetDatabase(self):
        """
        Method to reset database
        """
        tables : list = list(schemas.tables.keys())
        numberKeys : int = len(tables) - 1
        while numberKeys >= 0:
            self.deleteTable(tables[numberKeys])
            numberKeys -= 1
        self.__initTables()
        params : dict = self.getParams()
        timestampRefKey : str = "timestampRef"
        params.pop(timestampRefKey)
        self.writeParams(params)
        self.__timestampRef : float = self.__initParams()

    def storeNewFrame(self, imagePath : str):
        """
        Method to store new frame in database
        """
        timestampStrf : str = imagePath.split("/")[-1].split(".png")[0]
        timestampMilliseconds : int = int(datetime.strptime(timestampStrf, self.__dateTimeFormat).timestamp() - self.__timestampRef)

        self.__executeQuery(schemas.tables["frames"]["insertNewFrame"].format(
            timestamp = timestampMilliseconds,
            timestampStrf = timestampStrf,
            pathImage = imagePath,
            personDetection = 0,
        ))

    def __executeQuery(self, query : str) -> str:
        """
        Tool to perform query
        """
        connection : mysql.connector = self.__getConnection()
        cursor : any = connection.cursor()
        cursor.execute(query)

        row : str = cursor.fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return row

    def getNextEntryPersonDetected(self) -> int:
        """
        Method to obtain last entry of person detected in database
        """
        resultQuery : list
        while True:
            resultQuery = self.__executeQuery(schemas.tables["frames"]["getFrameIdLastPersonPrediction"])
            if resultQuery is None:
                time.sleep(self.__config["sleepDatabase"])
            else:
                break

        return int(resultQuery[0])
    
    def getImageFromFrameId(self, frameId : int):
        """
        Method to get image path from frameId
        """
        resultQuery : str = self.__executeQuery(schemas.tables["frames"]["getImagePathFromFrameId"].format(frameId = str(frameId)))

        return str(resultQuery[0])
    
    def updatePersonDetected(self, frameId : int):
        """
        Method to update new person detected in frames table
        """
        self.__executeQuery(schemas.tables["frames"]["updateImagePathFromFrameId"].format(personDetection = 1, frameId = str(frameId)))

    def storeNewObject(self, frameId : int, x_0 : int, y_0 : int, x_1 : int, y_1 : int):
        """
        Method to add new object detected in frame
        """
        self.__executeQuery(schemas.tables["objects"]["insertNewObject"].format(
            frameId = frameId,
            x_0 = str(x_0),
            y_0 = str(y_0),
            x_1 = str(x_1),
            y_1 = str(y_1),
        ))

    def getNextEntryActionDetected(self) -> int:
        """
        Method to obtain last entry of action detected in database
        """
        resultQuery : list
        while True:
            resultQuery = self.__executeQuery(schemas.tables["frames"]["getFrameIdLastActionPrediction"])
            if resultQuery is None:
                time.sleep(self.__config["sleepDatabase"])
            else:
                break

        return int(resultQuery[0])

    def writePredictionToDatabase(self, prediction : tuple, indexImage : str):
        """
        Method to write to database the prediction
        """