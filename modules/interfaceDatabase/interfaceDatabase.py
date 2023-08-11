import numpy as np
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
        self.__createkDatabase()
        self.__initTables()

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

    def __createkDatabase(self):
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

    def storeNewFrame(self, imagePath : str):
        """
        Method to store new frame in database
        """
        timestamp : str = imagePath.split("/")[-1].split(".png")[0]
        connection : mysql.connector = self.__getConnection()
        cursor : any = connection.cursor()
        cursor.executemany(
            schemas.tables["frames"]["insertNewFrame"],
            [(timestamp, imagePath, False)],
        )

        connection.commit()
        cursor.close()
        connection.close()

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