import numpy as np
import torch
from PIL import Image
import torchvision
from yolov6.data.data_augment import letterbox
from modules.interfaceDatabase.interfaceDatabase import InterfaceDatabase
from modules.baseModule.baseModule import BaseModule

class VideoProcessing(BaseModule):
    """
    Class to handle the video processing using AI algorithms
    """
    def __init__(self):
        super().__init__()
        self.__interfaceDatabse : InterfaceDatabase = InterfaceDatabase()

    def __imageToTensor(self, imageNumpy : np.ndarray, imgSize : list, stride : int, half : bool, device : str) -> tuple:
        """
        Tool to conver image np to tensor
        """
        image : np.ndarray = letterbox(imageNumpy, imgSize, stride=stride)[0]

        resize : torchvision.transforms.Resize = torchvision.transforms.Resize(imgSize)

        image = image.transpose((2, 0, 1))  # HWC to CHW
        imageTorch : torch.Tensor = torch.from_numpy(np.ascontiguousarray(image))
        imageTorch = resize.forward(imageTorch)
        imageTorch = imageTorch.half() if half else imageTorch.float()  # uint8 to fp16/32
        imageTorch /= 255  # 0 - 255 to 0.0 - 1.0

        imageTorch = imageTorch.to(device)
        if len(imageTorch.shape) == 3:
            imageTorch = imageTorch[None]

        return imageTorch, imageNumpy

    def processImageToTensorPersonDetection(self, path : str, imgSize : int, stride : int, half : bool, device : str) -> tuple:
        """
        Method to convert image to tensor
        """
        imageNumpy : np.ndarray = np.asarray(
            Image.open(
                open(path, "rb")
            )
        )

        return self.__imageToTensor(
            imageNumpy=imageNumpy,
            imgSize=imgSize,
            stride=stride,
            half=half,
            device=device,
        )

    def detectPerson(self):
        """
        Method to detect Person and write to the database the objects
        """
        image, imageIndex = self.__interfaceDatabse.getNextImage()
        prediction : tuple = self.__detectPersons(image)
        self.__interfaceDatabse.writePredictionToDatabase(prediction, imageIndex)
