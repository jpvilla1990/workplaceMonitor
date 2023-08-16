from modules.interfaceCamera.interfaceCamera import InterfaceCamera
from modules.predictor.predictor import Predictor
interfaceCamera = InterfaceCamera()
predictor = Predictor()
interfaceCamera.startCaptureVideos()
predictor.predictLoop()
#interfaceCamera.stopCaptureVideos()
#predictor.stopPersonPrediction()