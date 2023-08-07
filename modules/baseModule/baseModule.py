import os
from pathlib import Path
import yaml

class BaseModule(object):
    """
    Class to handle files and paths
    """
    def __init__(self):
        self.__config : dict = self.__loadConfig()
        self.__paths : dict = self.__loadPaths()
        self.__createFolders()

    def __loadPaths(self):
        """
        Tool to load paths
        """
        rootPath = Path(os.path.abspath(__file__)).parents[2]

        folders = {
            "data" : os.path.join(rootPath, "data"),
            "imagesDatabase" : os.path.join(rootPath, "data", "imagesDatabase"),
            "tmp" : os.path.join(rootPath, "data", "tmp"),
        }

        files = {}

        return {
            "folders" : folders,
            "files" : files,
        }
    
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

        config : dict = dict()
        with open(os.path.join(rootPath, "config.yaml")) as file:
            config = yaml.safe_load(file)
        
        return config

    def getConfig(self) -> dict:
        """
        Method to obtain config
        """
        return self.__config