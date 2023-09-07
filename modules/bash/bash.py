import psutil
import subprocess
from modules.baseModule.baseModule import BaseModule

class Bash(BaseModule):
    """
    Class to execute bash commands
    """
    def __init__(self):
        super().__init__()
        self.__processes = {
            "camera" : None,
            "predictor" : None,
        }

        self.__executable = "python3"

        self.__paths = self.getPaths()

        self.__scripts = {
            "camera" : self.__paths["files"]["cameraScript"],
            "predictor" : self.__paths["files"]["predictorScript"],
        }

    def __killProcessByScript(self, scriptName : str):
        """
        Tool to kill process by script name
        """
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if self.__executable in process.info['name'] and scriptName in ' '.join(process.info['cmdline']):
                    print(int(process.info['pid']))
                    self.executeBashCommand("kill " + str(process.info['pid']))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def startBashScript(self, executable : str, process : str):
        """
        Method to start bash script
        """
        if process is not None:
            self.stopBashScript(process)
        command : str = executable + " " + self.__scripts[process] + " &"

        self.__processes[process] = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stopBashScript(self, processName : str):
        """
        Method to stop running process
        """
        if self.__processes[processName]:
            self.__killProcessByScript(self.__scripts[processName])
            self.__processes[processName].kill()
            self.__processes[processName].wait()
            self.__processes[processName] = None

    def startPredictorScript(self):
        """
        Start predictor script
        """
        executable : str = "python3"
        self.startBashScript(executable, "predictor")

    def startCameraScript(self):
        """
        Start predictor script
        """
        predictorScript : str = self.__paths["files"]["cameraScript"]
        executable : str = "python3"
        self.startBashScript(executable, "camera")

    def executeBashCommand(self, command : str):
        """
        Method to execute bash command
        """
        subprocess.Popen(["bash", "-c", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)