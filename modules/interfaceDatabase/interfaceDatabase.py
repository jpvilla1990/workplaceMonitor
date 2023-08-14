import numpy as np
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
        connection : mysql.connector = self.__getConnection()
        cursor : any = connection.cursor()
        cursor.execute(
            "DROP TABLE " + table + ";"
        )

        connection.commit()
        cursor.close()
        connection.close()

    def resetDatabase(self):
        """
        Method to reset database
        """
        for table in list(schemas.tables.keys()):
            self.deleteTable(table)
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
        connection : mysql.connector = self.__getConnection()
        cursor : any = connection.cursor()
        cursor.executemany(
            schemas.tables["frames"]["insertNewFrame"],
            [(timestampMilliseconds, timestampStrf, imagePath, False)],
        )

        connection.commit()
        cursor.close()
        connection.close()

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

    def getLastEntryPersonDetected(self) -> int:
        """
        Method to obtain last entry of person detected in database
        """
        resultQuery : str = self.__executeQuery(schemas.tables["frames"]["getIdLastPrediction"])

        return int(resultQuery[0])
    
    def getImageFromTimestamp(self, timestamp : int):
        """
        Method to get image path from timestamp
        """
        resultQuery : str = self.__executeQuery(schemas.tables["frames"]["getImagePathFromTimestamp"].format(timestamp = str(timestamp)))

        return str(resultQuery[0])

    def getLastEntryActionDetected(self) -> int:
        """
        Method to obtain last entry of action detected in database
        """
        # TODO
        return 0

    def writePredictionToDatabase(self, prediction : tuple, indexImage : str):
        """
        Method to write to database the prediction
        """