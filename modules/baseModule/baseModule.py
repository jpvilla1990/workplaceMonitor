import os
import shutil
from datetime import datetime
from pathlib import Path
import yaml

class BaseModule(object):
    """
    Class to handle files and paths
    """
    def __init__(self):
        self.__config : dict = self.__loadConfig()
        self.__paths : dict = self.__loadPaths()
        self.__dateTimeFormat : str = self.__config["interfaceCamera"]["dateTimeFormat"]
        self.__createFolders()
        self.__createParamsFile()

    def __loadPaths(self):
        """
        Tool to load paths
        """
        rootPath = Path(os.path.abspath(__file__)).parents[2]

        folders = {
            "data" : os.path.join(rootPath, "data"),
            "imagesDatabase" : os.path.join(rootPath, "data", "imagesDatabase"),
            "tmp" : os.path.join(rootPath, "data", "tmp"),
            "logs" : os.path.join(rootPath, "data", "logs"),
            "params" : os.path.join(rootPath, "data", "params"),
        }

        files = {
            "systemLog" : os.path.join(rootPath, "data", "logs", "log.txt"),
            "databaseParams" : os.path.join(rootPath, "data", "params", "params.yaml"),
        }

        return {
            "folders" : folders,
            "files" : files,
        }
    
    def __createParamsFile(self):
        """
        Method to create params file
        """
        filePath : str = self.__paths["files"]["databaseParams"]
        if os.path.exists(filePath) is False:
            paramsContent : dict = {}
            self.writeParams(paramsContent)

    def writeParams(self, content : dict):
        """
        Method to write in the params file
        """
        filePath : str = self.__paths["files"]["databaseParams"]
        BaseModule.writeYaml(filePath, content)

    def getParams(self) -> dict:
        """
        Method to write in the params file
        """
        filePath : str = self.__paths["files"]["databaseParams"]
        return BaseModule.readYaml(filePath)

    def writeYaml(filePath : str, paramsContent : dict):
        """
        Static method to write in a yaml file
        """
        with open(filePath, 'w') as file:
            yaml.dump(paramsContent, file)

    def readYaml(filePath : str) -> dict:
        """
        Static method to read from a yaml file
        """
        content : dict
        with open(filePath) as file:
            content = yaml.safe_load(file)
        
        return content

    def writeLog(self, text : str, typeLog : str):
        """
        Method to write in log system events
        """
        line : str = datetime.now().strftime(self.__dateTimeFormat) + " " + "TYPE: " + typeLog + " LOG: " + text + "\n"
        fileSize : int = 0
        if os.path.exists(self.__paths["files"]["systemLog"]):
            fileSize = os.path.getsize(self.__paths["files"]["systemLog"])
        if fileSize > self.__config["log"]["maxLogSize"]:
            if os.path.exists(self.__paths["files"]["systemLog"] + ".backUp"):
                os.remove(self.__paths["files"]["systemLog"] + ".backUp")
            shutil.copyfile(self.__paths["files"]["systemLog"], self.__paths["files"]["systemLog"] + ".backUp")
            with open(self.__paths["files"]["systemLog"], "w") as logFile:
                logFile.write(line)
        else:
            with open(self.__paths["files"]["systemLog"], "a") as logFile:
                logFile.write(line)

    def createFolderRecursively(self, folder : str):
        """
        Static method to create recursively a folder if does not exist
        """
        if not os.path.exists(folder):
            os.makedirs(folder)

    def __createFolders(self):
        """
        Tool to create folders
        """
        for key in list(self.__paths["folders"].keys()):
            self.createFolderRecursively(self.__paths["folders"][key])

    def getPaths(self) -> dict:
        """
        Method to get paths
        """
        return self.__paths

    def __loadConfig(self) -> dict:
        """
        Tool to load config.yaml
        """
        rootPath : str = Path(os.path.abspath(__file__)).parents[2]

        return BaseModule.readYaml(os.path.join(rootPath, "config.yaml"))

    def getConfig(self) -> dict:
        """
        Method to obtain config
        """
        return self.__config