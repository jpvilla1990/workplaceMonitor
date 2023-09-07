from fastapi import FastAPI

from modules.bash.bash import Bash
from modules.interfaceCamera.interfaceCamera import InterfaceCamera
from modules.interfaceDatabase.interfaceDatabase import InterfaceDatabase
from modules.predictor.predictor import Predictor


interfaceCamera : InterfaceCamera = InterfaceCamera()
bash : Bash = Bash()
interfaceDatabase : InterfaceDatabase = InterfaceDatabase()
app = FastAPI()

@app.post("/cameraCapture/{status}")
def cameraCapture(status : str):
    """
    Start camera capture
    """
    if status == "start":
        bash.startCameraScript()
    elif status == "stop":
        bash.stopBashScript("camera")

@app.post("/reset")
def reset():
    """
    Method to reset database
    """
    bash.stopBashScript("camera")
    bash.stopBashScript("predictor")
    interfaceDatabase.resetDatabase()
    interfaceDatabase.writeParams({})

@app.post("/predictor/{status}")
def predictor(status : str):
    """
    Method to predict
    """
    if status == "start":
        bash.startPredictorScript()
    elif status == "stop":
        bash.stopBashScript("predictor")