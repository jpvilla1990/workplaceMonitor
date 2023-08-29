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
            actionDetection = 0,
        ))

    def __executeQuery(self, query : str) -> list:
        """
        Tool to perform query
        """
        connection : mysql.connector = self.__getConnection()
        cursor : any = connection.cursor()
        cursor.execute(query)

        results : list = list()

        while True:
            queryResult : tuple = cursor.fetchone()
            if queryResult is not None:
                if len(queryResult) > 1:
                    elements : list = list()
                    for element in queryResult:
                        elements.append(element)
                    results.append(
                        elements
                    )
                else:
                    results.append(
                        queryResult[0]  
                    )
            else:
                break

        connection.commit()
        cursor.close()
        connection.close()

        return results

    def getNextEntryPersonDetected(self) -> int:
        """
        Method to obtain last entry of person detected in database
        """
        resultQuery : list
        while True:
            resultQuery = self.__executeQuery(schemas.tables["frames"]["getFrameIdLastPersonPrediction"])
            if len(resultQuery) == 0:
                time.sleep(self.__config["sleepDatabase"])
            else:
                break

        return int(resultQuery[0])
    
    def getImageFromFrameId(self, frameId : int) -> str:
        """
        Method to get image path from frameId
        """
        resultQuery : list = self.__executeQuery(schemas.tables["frames"]["getImagePathFromFrameId"].format(frameId = str(frameId)))

        return str(resultQuery[0])
    
    def getObjectsFromPersonId(self, personId : int) -> list:
        """
        Method to get objects from person id
        """
        resultQuery : list = self.__executeQuery(schemas.tables["objects"]["getObjectsIdFromPersonId"].format(personId = str(personId)))
        return resultQuery
    
    def updateVideoPath(self, videoPath : str, personId : int):
        """
        Method to update video path by person id
        """
        self.__executeQuery(schemas.tables["persons"]["updateVideoPathFromPersonId"].format(pathVideoPredict = videoPath, personId = personId))

    def getObjectsIdFromFrameId(self, frameId: int) -> list:
        """
        Method to get objects from frame id
        """
        resultQuery : list = self.__executeQuery(schemas.tables["objects"]["getObjectsIdFromFrameId"].format(frameId = str(frameId)))
        return resultQuery
    
    def getActivePersons(self) -> list:
        """
        Method to get active persons
        """
        resultQuery : list = self.__executeQuery(schemas.tables["persons"]["getPersonsIdFromPersonCompleted"].format(personCompleted = 0))
        return resultQuery

    def getCoordinatesByPersonId(self, personId : int) -> list:
        """
        Method to get coordinates by person id
        """
        resultQuery : list = self.__executeQuery(schemas.tables["objects"]["getCoordinatesByPersonId"].format(personId = personId))
        return resultQuery
    
    def getCoordinatesByObjectId(self, objectId : int) -> list:
        """
        Method to get coordinates by person id
        """
        resultQuery : list = self.__executeQuery(schemas.tables["objects"]["getCoordinatesByObjectId"].format(objectId = objectId))
        return resultQuery

    def createNewPerson(self):
        """
        Method to create a new person
        """
        self.__executeQuery(schemas.tables["persons"]["insertNewPerson"])

    def getNewPerson(self) -> int:
        """
        Method to create a new person
        """
        resultQuery : list = self.__executeQuery(schemas.tables["persons"]["getNewPerson"])

        return int(resultQuery[0])
    def updatePersonIdFromObjectId(self, objectId : int, personId : int):
        """
        Method to update person id from object id
        """
        self.__executeQuery(schemas.tables["objects"]["updatePersonIdFromObjectId"].format(objectId = objectId, personId = personId))

    def updatePersonDetected(self, frameId : int):
        """
        Method to update new person detected in frames table
        """
        self.__executeQuery(schemas.tables["frames"]["updatePersonDetectionFromFrameId"].format(personDetection = 1, frameId = str(frameId)))

    def updateActionDetected(self, frameId : int):
        """
        Method to update new person detected in frames table
        """
        self.__executeQuery(schemas.tables["frames"]["updateActionDetectionFromFrameId"].format(actionDetection = 1, frameId = str(frameId)))

    def setPersonAsCompleted(self, personId: int):
        """
        Method to set persons as updated
        """
        self.__executeQuery(schemas.tables["persons"]["updatePersonCompletedFromPersonId"].format(personId = personId, personCompleted = 1))

    def setIdleClasification(self, personId: int):
        """
        Method to set persons as updated
        """
        self.__executeQuery(schemas.tables["persons"]["updateIdleClasificationFromPersonId"].format(personId = personId, idleClasification = 1))

    def setAnnotatedImagePath(self, imagePath : str, frameId : int):
        """
        Method to update annotated image path by frame id
        """
        self.__executeQuery(schemas.tables["frames"]["updateAnnotatedImagePathFromFrameId"].format(pathImagePredict = imagePath, frameId = str(frameId)))

    def getTimestampFromFrameId(self, frameId : int) -> int:
        """
        Method to get timestamp from frame id
        """
        resultQuery : list = self.__executeQuery(schemas.tables["frames"]["getTimestampFromFrameId"].format(frameId = frameId))

        return int(resultQuery[0])

    def getFrameIdFromPersonId(self, personId : int) -> int:
        """
        Method to get frame id from object id
        """
        resultQuery : list = self.__executeQuery(schemas.tables["objects"]["getFrameIdFromPersonId"].format(personId = personId))
        return int(resultQuery[0])
    
    def getPersonIdFromObjectId(self, objectId : int) -> int:
        """
        Method to get person id from object id
        """
        resultQuery : list = self.__executeQuery(schemas.tables["objects"]["getPersonIdFromObjectId"].format(objectId = objectId))
        return int(resultQuery[0])
    
    def getFramesFromPersonId(self, personId : int) -> list:
        """
        Method to get number of frames from person id
        """
        resultQuery : list = self.__executeQuery(schemas.tables["objects"]["getFramesFromPersonId"].format(personId = personId))
        return resultQuery
    
    def getNextVideo(self) -> list:
        """
        Method to get next video to store, return personId
        """
        resultQuery : list = self.__executeQuery(schemas.tables["persons"]["getNextPersonIdVideoToStore"])
        return resultQuery

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
            if len(resultQuery) == 0:
                time.sleep(self.__config["sleepDatabase"])
            else:
                break

        return int(resultQuery[0])

    def writePredictionToDatabase(self, prediction : tuple, indexImage : str):
        """
        Method to write to database the prediction
        """